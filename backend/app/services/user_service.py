from typing import Optional

from pydantic import EmailStr
from app.models.user import UserInDb
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user: UserRepository):
        self.user = user

    async def auth(self, email: EmailStr, password: str):
        result = await self.user.get_by_email(email)
        if not result:
            return None
        if result.hashed_password != password:
            return None
        return result
