import strawberry
from typing import Optional, List
from datetime import datetime
from strawberry.scalars import JSON

@strawberry.type
class LogType:
    id: Optional[str]
    service: str
    level: str
    message: str
    timestamp: datetime
    trace_id: Optional[str]
    span_id: Optional[str]
    raw: Optional[JSON]

@strawberry.type
class SpanType:
    id: Optional[str]
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    service_name: str
    operation_name: str
    start_time: datetime
    end_time: datetime
    duration_ms: float
    status_code: int
    attributes: Optional[JSON]

@strawberry.type
class TraceNodeType:
    span_id: str
    parent_span_id: Optional[str]
    service_name: str
    operation_name: str
    start_time: datetime
    duration_ms: float
    status_code: int
    children: List["TraceNodeType"]

@strawberry.type
class AlertRuleType:
    id: str
    name: str
    metric: str
    threshold: float
    window_minutes: int
    service: str
