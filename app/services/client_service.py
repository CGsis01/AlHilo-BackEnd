from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.repositories.client_repository import ClientRepository
from app.schemas.api_response import ApiResponse
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse

class ClientService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client_repository = ClientRepository(db)
    
    async def create_client(self, client_data: ClientCreate) -> ApiResponse[ClientResponse]:
        response = ApiResponse[ClientResponse](
            status=201,
            message="Client created successfully",
            code="SUCCESS",
            data=None)
        
        try:
            client_dict = client_data.model_dump()
            client = await self.client_repository.create(client_dict)

            response.data = ClientResponse.model_validate(client)
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "CLIENT_CREATION_ERROR"

        return response
    
    async def update_client(self, client_id: UUID, client_data: ClientUpdate) -> ApiResponse[ClientResponse]:
        response = ApiResponse[ClientResponse](
            status=200,
            message="Client updated successfully",
            code="SUCCESS",
            data=None)
        
        try:
            client = await self.client_repository.get_by_id(client_id)
            if not client:
                response.status = 404
                response.message = "No client found with the provided ID"
                response.code = "CLIENT_RETRIEVAL_ERROR"

                return response
            
            update_dict = client_data.model_dump(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(client, field, value)
            
            await self.db.commit()
            await self.db.refresh(client)
            
            response.data = ClientResponse.model_validate(client)
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "CLIENT_UPDATE_ERROR"
        
        return response
    
    async def get_client(self, client_id: UUID) -> ApiResponse[ClientResponse]:
        response = ApiResponse[ClientResponse](
            status=200,
            message="Client retrieved successfully",
            code="SUCCESS",
            data=None)
        
        try:
            client = await self.client_repository.get_by_id(client_id)
            if not client:
                response.status = 404
                response.message = "No client found with the provided ID"
                response.code = "CLIENT_RETRIEVAL_ERROR"

                return response
            
            response.data = ClientResponse.model_validate(client)
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "CLIENT_RETRIEVAL_ERROR"
        
        return response
    
    async def get_client_by_phone(self, phone: str) -> ApiResponse[ClientResponse]:
        response = ApiResponse[ClientResponse](
            status=200,
            message="Client retrieved successfully",
            code="SUCCESS",
            data=None)
        
        try:
            client = await self.client_repository.get_by_phone(phone)
            if not client:
                response.status = 404
                response.message = "No clients found with the provided phone number"
                response.code = "CLIENT_NOT_FOUND"

                return response
            
            response.data = ClientResponse.model_validate(client)
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "CLIENT_RETRIEVAL_ERROR"
        
        return response
    
    async def search_clients(self) -> ApiResponse[List[ClientResponse]]:
        response = ApiResponse[List[ClientResponse]](
            status=200,
            message="Clients retrieved successfully",
            code="SUCCESS",
            data=None)
        
        try:
            clients = await self.client_repository.get_all()
            
            if clients is not None:
                response.data = [ClientResponse.model_validate(client) for client in clients]
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "CLIENT_SEARCH_ERROR"
        
        return response
