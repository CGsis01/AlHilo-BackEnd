import asyncio
import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.role import Role
from app.models.repair_status import RepairStatus
from app.models.repair_type import RepairType


async def seed_data():
    async with AsyncSessionLocal() as db:
        # Create Roles
        admin_role = Role(
            role_id=uuid4(),
            name="Administrator",
            code="ADMIN",
            is_active=True
        )
        receptionist_role = Role(
            role_id=uuid4(),
            name="Receptionist",
            code="RECEP",
            is_active=True
        )
        seamstress_role = Role(
            role_id=uuid4(),
            name="Seamstress",
            code="SEAM",
            is_active=True
        )
        
        db.add_all([admin_role, receptionist_role, seamstress_role])
        await db.commit()
        
        # Create Users
        admin_user = User(
            user_id=uuid4(),
            name="Administrator",
            email="admin@alhilo.com",
            password_hash=get_password_hash("admin123"),
            role_id=admin_role.role_id,
            is_active=True
        )
        
        receptionist_user = User(
            user_id=uuid4(),
            name="Receptionist",
            email="recepcion@alhilo.com",
            password_hash=get_password_hash("recep123"),
            role_id=receptionist_role.role_id,
            is_active=True
        )
        
        seamstress_user = User(
            user_id=uuid4(),
            name="Seamstress",
            email="costurera@alhilo.com",
            password_hash=get_password_hash("seam123"),
            role_id=seamstress_role.role_id,
            is_active=True
        )
        
        db.add_all([admin_user, receptionist_user, seamstress_user])
        await db.commit()
        
        # Create Repair Statuses
        pending_status = RepairStatus(
            repair_status_id=uuid4(),
            name="Pending",
            is_active=True
        )
        in_progress_status = RepairStatus(
            repair_status_id=uuid4(),
            name="In Progress",
            is_active=True
        )
        completed_status = RepairStatus(
            repair_status_id=uuid4(),
            name="Completed",
            is_active=True
        )
        delivered_status = RepairStatus(
            repair_status_id=uuid4(),
            name="Delivered",
            is_active=True
        )
        
        db.add_all([pending_status, in_progress_status, completed_status, delivered_status])
        await db.commit()
        
        # Create Repair Types
        hem_repair = RepairType(
            repair_type_id=uuid4(),
            name="Hem Adjustment",
            code="HEM",
            estimated_price=150.00,
            estimated_time=24,
            is_active=True
        )
        zipper_repair = RepairType(
            repair_type_id=uuid4(),
            name="Zipper Replacement",
            code="ZIP",
            estimated_price=250.00,
            estimated_time=48,
            is_active=True
        )
        button_repair = RepairType(
            repair_type_id=uuid4(),
            name="Button Replacement",
            code="BTN",
            estimated_price=100.00,
            estimated_time=12,
            is_active=True
        )
        
        db.add_all([hem_repair, zipper_repair, button_repair])
        await db.commit()
        
        print("✅ Database seeded successfully!")
        print("\nTest Users Created:")
        print("- Admin: admin@alhilo.com / admin123")
        print("- Receptionist: recepcion@alhilo.com / recep123")
        print("- Seamstress: costurera@alhilo.com / seam123")


if __name__ == "__main__":
    asyncio.run(seed_data())
