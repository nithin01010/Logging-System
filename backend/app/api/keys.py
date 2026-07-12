from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.api_key import ApiKeyCreate, ApiKeyResponse
from app.core.security import get_api_key_service
from app.services.api_key_service import ApiKeyService

router = APIRouter(prefix='/keys', tags=["API keys"])


@router.post(
    '/',
    response_model=ApiKeyResponse,
    status_code=status.HTTP_201_CREATED
)
async def generate_key(
    key_in: ApiKeyCreate,
    service: ApiKeyService = Depends(get_api_key_service)
):
    raw_key, created_key = await service.create_key(key_in.name)

    return ApiKeyResponse(
        id=created_key.id,
        name=created_key.name,
        created_at=created_key.created_at,
        is_active=created_key.is_active,
        key=raw_key
    )


@router.get('/', response_model=List[ApiKeyResponse])
async def list_keys(service: ApiKeyService = Depends(get_api_key_service)):
    keys = await service.get_active_keys()
    return [
        ApiKeyResponse(
            id=k.id,
            name=k.name,
            created_at=k.created_at,
            is_active=k.is_active,
            key=None
        ) for k in keys
    ]


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_key(
    key_id: str,
    service: ApiKeyService = Depends(get_api_key_service)
):
    sus = await service.revoke_key(key_id)
    if not sus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API KEY NOT FOUND OR ALREADY INACTIVE"
        )
