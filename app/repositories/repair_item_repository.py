from typing import List, Optional, cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import joinedload
from uuid import UUID
from app.models.repair_item import RepairItem
from app.models.repair_item_repair_type import RepairItemRepairType
from app.models.repair_type import RepairType
from app.models.repair_status import RepairStatus
from app.repositories.base import BaseRepository

class RepairItemRepository(BaseRepository[RepairItem]):
    def __init__(self, db: AsyncSession):
        super().__init__(RepairItem, db)

    async def _get_status_id_by_name(self, status_name: str) -> Optional[UUID]:
        result = await self.db.execute(select(RepairStatus.repair_status_id).filter(RepairStatus.name == status_name))

        return result.scalar_one_or_none()

    def _query_with_relations(self):
        return (
            select(RepairItem).options(
                joinedload(RepairItem.repair_item_repair_types).joinedload(RepairItemRepairType.repair_type).joinedload(RepairType.repair_complexity),
                joinedload(RepairItem.repair_status),
                joinedload(RepairItem.garment),
                joinedload(RepairItem.assigned_to)
            )
        )

    async def get_by_id_with_relations(self, id: UUID) -> Optional[RepairItem]:
        result = await self.db.execute(
            self._query_with_relations().filter(RepairItem.id == id))
        
        return result.unique().scalar_one_or_none()

    async def get_by_repair_id(self, repair_id: UUID) -> List[RepairItem]:
        result = await self.db.execute(
            self._query_with_relations().filter(RepairItem.repair_id == repair_id))
        
        return list(result.scalars().unique().all())

    async def get_by_assigned_to(self, assigned_to_id: UUID) -> List[RepairItem]:
        """Get all repair items assigned to a seamstress"""
        result = await self.db.execute(
            self._query_with_relations().filter(
                or_(
                    RepairItem.assigned_to_id == assigned_to_id,
                    RepairItem.attended_by_id == assigned_to_id,
                )
            )
        )
        
        return list(result.scalars().unique().all())

    async def _is_seamstress_assigned_elsewhere(self, seamstress_id: UUID, repair_item_id: UUID) -> bool:
        validated_status_id = await self._get_status_id_by_name("Validada")
        delivered_status_id = await self._get_status_id_by_name("Entregada")

        filters = [
            RepairItem.id != repair_item_id,
            or_(
                RepairItem.assigned_to_id == seamstress_id,
                RepairItem.attended_by_id == seamstress_id,
            ),
        ]

        released_status_ids = [
            status_id
            for status_id in (validated_status_id, delivered_status_id)
            if status_id is not None
        ]

        if released_status_ids:
            filters.append(
                or_(
                    RepairItem.repair_status_id.is_(None),
                    RepairItem.repair_status_id.not_in(released_status_ids),
                )
            )

        result = await self.db.execute(
            select(RepairItem.id).filter(and_(*filters)).limit(1)
        )

        return result.scalar_one_or_none() is not None

    async def _validate_assignment_change(
        self,
        db_obj: RepairItem,
        requested_primary_id: Optional[UUID],
        requested_secondary_id: Optional[UUID],
    ) -> None:
        current_primary_id = getattr(db_obj, "assigned_to_id", None)
        current_secondary_id = getattr(db_obj, "attended_by_id", None)

        if requested_secondary_id is not None and requested_primary_id is None:
            raise ValueError("Debes asignar una costurera principal antes de agregar una secundaria.")

        if (
            requested_primary_id is not None
            and requested_secondary_id is not None
            and requested_primary_id == requested_secondary_id
        ):
            raise ValueError("No puedes asignar la misma costurera como principal y secundaria.")

        validated_status_id = await self._get_status_id_by_name("Validada")
        is_validated = (
            validated_status_id is not None
            and getattr(db_obj, "repair_status_id", None) == validated_status_id
        )

        if (
            (current_primary_id is not None or current_secondary_id is not None)
            and (requested_primary_id != current_primary_id or requested_secondary_id != current_secondary_id)
            and not is_validated
        ):
            raise ValueError(
                "No se pueden cambiar o desasignar costureras hasta que la prenda este en estatus Validada."
            )

        requested_ids = [
            user_id for user_id in (requested_primary_id, requested_secondary_id) if user_id is not None
        ]

        for seamstress_id in set(requested_ids):
            if await self._is_seamstress_assigned_elsewhere(seamstress_id, cast(UUID, db_obj.id)):
                raise ValueError(
                    "La costurera seleccionada ya esta asignada a otra prenda. "
                    "Se liberara cuando esa prenda pase a Validada."
                )

    async def assign(
        self,
        repair_item_id: UUID,
        assigned_to_id: Optional[UUID],
        attended_by_id: Optional[UUID] = None,
    ) -> Optional[RepairItem]:
        """Assign or unassign a repair item to a seamstress"""
        try:
            result = await self.db.execute(
                select(self.model).filter(self.model.id == repair_item_id).with_for_update()
            )

            db_obj = result.scalar_one_or_none()

            if not db_obj:
                return None

            await self._validate_assignment_change(
                db_obj=db_obj,
                requested_primary_id=assigned_to_id,
                requested_secondary_id=attended_by_id,
            )

            in_progress_status_id = await self._get_status_id_by_name("En progreso")
            pending_status_id = await self._get_status_id_by_name("Pendiente")

            setattr(db_obj, 'assigned_to_id', assigned_to_id)
            setattr(db_obj, 'attended_by_id', attended_by_id)
            
            has_assignment = assigned_to_id is not None or attended_by_id is not None
            target_status_id = in_progress_status_id if has_assignment else pending_status_id
            
            if target_status_id:
                setattr(db_obj, 'repair_status_id', target_status_id)

            await self.db.commit()
            return await self.get_by_id_with_relations(repair_item_id)
        except Exception:
            await self.db.rollback()
            raise

    async def assign_bulk(self, assignments: dict[UUID, dict[str, Optional[UUID]]]) -> List[RepairItem]:
        """Bulk assign/unassign multiple repair items"""
        try:
            updated_items = []
            in_progress_status_id = await self._get_status_id_by_name("En progreso")
            pending_status_id = await self._get_status_id_by_name("Pendiente")

            for repair_item_id, assignment_data in assignments.items():
                result = await self.db.execute(
                    select(self.model).filter(self.model.id == repair_item_id).with_for_update()
                )

                db_obj = result.scalar_one_or_none()

                if not db_obj:
                    continue

                current_primary_id = getattr(db_obj, "assigned_to_id", None)
                current_secondary_id = getattr(db_obj, "attended_by_id", None)

                requested_primary_id = assignment_data.get("assigned_to_id", current_primary_id)
                requested_secondary_id = assignment_data.get("attended_by_id", current_secondary_id)

                await self._validate_assignment_change(
                    db_obj=db_obj,
                    requested_primary_id=requested_primary_id,
                    requested_secondary_id=requested_secondary_id,
                )

                setattr(db_obj, "assigned_to_id", requested_primary_id)
                setattr(db_obj, "attended_by_id", requested_secondary_id)

                has_assignment = requested_primary_id is not None or requested_secondary_id is not None
                target_status_id = in_progress_status_id if has_assignment else pending_status_id

                if target_status_id:
                    setattr(db_obj, "repair_status_id", target_status_id)

                updated_items.append(db_obj)

            if not updated_items:
                return []

            await self.db.commit()
            
            # Reload with relations
            updated_with_relations = []
            for item in updated_items:
                item_id = item.id
                item = await self.get_by_id_with_relations(item_id)
                if item:
                    updated_with_relations.append(item)
            
            return updated_with_relations
        except Exception:
            await self.db.rollback()
            raise

    async def update_status(self, repair_item_id: UUID, repair_status_id: UUID) -> Optional[RepairItem]:
        result = await self.db.execute(select(self.model).filter(self.model.id == repair_item_id))
        db_obj = result.scalar_one_or_none()

        if db_obj:
            status_result = await self.db.execute(select(RepairStatus.name).filter(RepairStatus.repair_status_id == repair_status_id))
            target_status_name = status_result.scalar_one_or_none()

            setattr(db_obj, 'repair_status_id', repair_status_id)
            
            if target_status_name == "Validada":
                setattr(db_obj, 'assigned_to_id', None)
                setattr(db_obj, 'attended_by_id', None)
            
            await self.db.commit()
            await self.db.refresh(db_obj)

            return await self.get_by_id_with_relations(repair_item_id)

        return None
