from typing import List
from app.repositories.log_repository import LogRepository
from app.models.log import LogEntry, LogFilter


class LogService:
    def __init__(self, log_repo: LogRepository) -> None:
        self.log_repo = log_repo

    async def ingest_logs(self, logs: List[LogEntry]) -> bool:
        return await self.log_repo.create_batch(logs)

    async def query_logs(self, filters: LogFilter) -> List[LogEntry]:
        return await self.log_repo.get_logs(filters)
