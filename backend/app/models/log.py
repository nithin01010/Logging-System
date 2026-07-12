from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.user import PyObjectId


class LogEntry(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    service: str
    level: str

    message: str
    timestamp: datetime
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    raw: Optional[dict] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class LogBatch(BaseModel):
    logs: list[LogEntry]


class LogFilter(BaseModel):
    service: Optional[str] = None
    level: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = 100
    skip: int = 0
