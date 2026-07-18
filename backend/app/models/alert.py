from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from app.models.user import PyObjectId


class AlertRule(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str
    service: str
    metric: str
    threshold: float
    window_minutes: int
    is_active: bool = True

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class AlertTrigger(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    rule_id: PyObjectId
    rule_name: str
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    actual_value: float
    message: str

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
