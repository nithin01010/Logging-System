import secrets
import hashlib
from typing import Optional, List, Tuple
from app.models.api_key import ApiKeyInDb
from app.repositories.api_key_repository import ApiKeyRepository


class ApiKeyService:
    def __init__(self, key_repo) -> None:
        self.key_repo = key_repo

    def hash_key(self, api_key: str) -> str:
        return hashlib.sha256(api_key.encode()).hexdigest()

    async def create_key(self, name: str) -> Tuple[str, ApiKeyInDb]:
        raw_key = f"ls_{secrets.token_urlsafe(32)}"
        key_hash = self.hash_key(raw_key)

        api_key_db = ApiKeyInDb(name=name, key_hash=key_hash)
        created_key = await self.key_repo.create(api_key_db)
        return raw_key, created_key

    async def get_active_keys(self) -> List[ApiKeyInDb]:
        return await self.key_repo.get_all()

    async def verify_key(self, raw_key: str) -> Optional[ApiKeyInDb]:
        key_hash = self.hash_key(raw_key)
        return await self.key_repo.get_by_hash(key_hash)

    async def revoke_key(self, key_id: str) -> bool:
        return await self.key_repo.delete(key_id)
