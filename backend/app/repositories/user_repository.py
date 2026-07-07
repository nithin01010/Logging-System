from pydantic import EmailStr
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.user import UserInDb
from typing import Optional

class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.Users = db["users"]

    async def get_by_email(self, email: EmailStr) -> Optional[UserInDb]:
        user_dict = await self.Users.find_one({"email": email})
        if user_dict:
            return UserInDb(**user_dict)
        return None

    async def create(self, user_data: UserInDb) -> UserInDb:
        user_dict = user_data.model_dump(by_alias=True, exclude={"id"})
        result = await self.Users.insert_one(user_dict)
        user_data.id = result.inserted_id
        return user_data
