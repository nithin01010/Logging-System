from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime

from app.models.log import LogEntry, LogFilter, LogBatch
from app.core.security import get_current_api_key
from app.core.database import get_database
from app.repositories.log_repository import LogRepository
from app.services.log_service import LogService

router = APIRouter(prefix="/logs", tags=["logs"])


def get_log_service():
    db = get_database()
    repo = LogRepository(db)
    return LogService(repo)


@router.post("/batch", status_code=status.HTTP_201_CREATED)
async def ingest_logs(
    batch: LogBatch,
    service: LogService = Depends(get_log_service),
    _ = Depends(get_current_api_key),
):
    su = await service.ingest_logs(batch.logs)
    if not su:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ingest logs",
        )
    return {"message": "Logs ingested", "count": len(batch.logs)}


@router.get("/", response_model=List[LogEntry])
async def get_logs(
    service: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    log_service: LogService = Depends(get_log_service),
):
    filters = LogFilter(
        service=service,
        level=level,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        skip=skip,
    )
    return await log_service.query_logs(filters)
