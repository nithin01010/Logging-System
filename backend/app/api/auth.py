from fastapi import APIRouter, Depends, HTTPException, status
from app.core.database import get_database
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.models.user import UserLogin

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_user_service():
    db = get_database()
    repo = UserRepository(db)
    return UserService(repo)


@router.post("/login")
async def login(cred: UserLogin, service: UserService = Depends(get_user_service)):
    user = await service.auth(cred.email, cred.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    return {
        "message": "Login successful",
        "user": {"email": user.email, "username": user.username},
    }
