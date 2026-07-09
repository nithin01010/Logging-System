from pydantic import BaseModel, EmailStr, Field, GetCoreSchemaHandler
from typing import Optional, Any
from bson import ObjectId
from pydantic_core import core_schema


class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler):
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserInDb(UserBase):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    hashed_password: str

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
