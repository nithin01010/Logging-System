from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.log import LogEntry, LogFilter
from typing import List


class LogRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.logs_data = db["logs"]

    async def create_batch(self, logs: List[LogEntry]) -> bool:
        doc = [log.model_dump(by_alias=True, exclude={"id"}) for log in logs]
        if not doc:
            return None
        res = await self.logs_data.insert_many(doc)
        return len(res.inserted_ids) > 0

    async def get_logs(self, filters: LogFilter) -> List[LogEntry]:
        query = {}

        if filters.service:
            query["service"] = filters.service
        if filters.level:
            query["level"] = filters.level

        if filters.start_time or filters.end_time:
            query["timestamp"] = {}
            if filters.start_time:
                query["timestamp"]["$gte"] = filters.start_time
            if filters.end_time:
                query["timestamp"]["$lte"] = filters.end_time

        projection = None if filters.include_raw else {"raw": 0}

        cursor = (
            self.logs_data.find(query, projection)
            .sort("timestamp", -1)
            .skip(filters.skip)
            .limit(filters.limit)
        )

        res = await cursor.to_list(length=filters.limit)
        return [LogEntry(**r) for r in res]
