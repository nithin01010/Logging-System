from fastapi import Security, HTTPException, status, Depends
from fastapi.security.api_key import APIKeyHeader

from app.core.config import settings
from app.core.database import get_database
from app.repositories.api_key_repository import ApiKeyRepository
from app.services.api_key_service import ApiKeyService

api_key_header_scheme = APIKeyHeader(name=settings.API_KEY_NAME, auto_error=True)


def get_api_key_service():
    db = get_database()
    repo = ApiKeyRepository(db)
    return ApiKeyService(repo)


async def get_current_api_key(
    api_key: str = Security(api_key_header_scheme),
    service: ApiKeyService = Depends(get_api_key_service),
):
    key_reco = await service.verify_key(api_key)
    if not key_reco:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API Key",
        )
    return key_reco
