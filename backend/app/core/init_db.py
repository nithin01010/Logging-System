from app.core.database import db_instance
from app.core.config import settings


async def init_database():
    await db_instance.db["users"].update_one(
        {"email": settings.ADMIN_EMAIL},
        {
            "$setOnInsert": {
                "email": settings.ADMIN_EMAIL,
                "username": settings.ADMIN_NAME,
                "hashed_password": settings.ADMIN_PASSWORD,
            }
        },
        upsert=True,
    )
