from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.user import PyObjectId


class ApiKeyCreate(BaseModel):
    name: str


class ApiKeyInDb(ApiKeyCreate):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    key_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class ApiKeyResponse(BaseModel):
    key: Optional[str] = None
    id: str
    name: str
    created_at: datetime
    is_active: bool
