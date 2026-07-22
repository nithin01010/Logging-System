from app.core.database import db_instance
from app.core.config import settings


async def init_database():
    db = db_instance.db
    if db is None:
        return

    # Seed Admin User
    await db["users"].update_one(
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

    # 1. Compound Index for Log Queries
    await db["logs"].create_index([("service", 1), ("level", 1), ("timestamp", -1)])

    # 2. TTL Index: Expire logs after 30 days (2,592,000 seconds)
    await db["logs"].create_index("timestamp", expireAfterSeconds=2592000)

    # 3. Span Indexes for Trace Trees & Recent Traces
    await db["spans"].create_index([("trace_id", 1)])
    await db["spans"].create_index([("service_name", 1), ("start_time", -1)])

    # 4. Alert Triggers & API Keys Indexes
    await db["alert_triggers"].create_index([("timestamp", -1)])
    await db["api_keys"].create_index([("hashed_key", 1)])
