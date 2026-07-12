from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.models.api_key import ApiKeyInDb
from typing import Optional


class ApiKeyRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.api_keys = db["api_keys"]

    async def create(self, api_key: ApiKeyInDb) -> ApiKeyInDb:
        key_dict = api_key.model_dump(by_alias=True, exclude={"id"})
        res = await self.api_keys.insert_one(key_dict)
        api_key.id = str(res.inserted_id)
        return api_key

    async def get_all(self) -> list[ApiKeyInDb]:
        res = await self.api_keys.find({"is_active": True}).to_list(length=100)
        return [ApiKeyInDb(**k) for k in res]

    async def get_by_hash(self, key_hash) -> Optional[ApiKeyInDb]:
        key = await self.api_keys.find_one({"key_hash": key_hash, "is_active": True})
        if not key:
            return None
        return ApiKeyInDb(**key)

    async def delete(self, key_id: str) -> bool:
        res = await self.api_keys.update_one(
            {"_id": ObjectId(key_id)},
            {"$set": {"is_active": False}}
        )
        return res.modified_count > 0
