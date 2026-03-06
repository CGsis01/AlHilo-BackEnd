# Generic ApiResponse wrapper
from typing import Optional, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    status: int
    message: str
    code: str
    data: Optional[T] = None
