from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime
from app.models.user import PyObjectId


class SpanDocument(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")

    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    service_name: str
    operation_name: str
    start_time: datetime
    end_time: datetime
    duration_ms: float
    status_code: int = 0
    attributes: Dict[str, Any] = {}

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class TraceNode(BaseModel):
    span_id: str
    parent_span_id: Optional[str]
    service_name: str
    operation_name: str
    start_time: datetime
    duration_ms: float
    status_code: int
    children: List["TraceNode"] = []


TraceNode.model_rebuild()


class OtelAttributeValue(BaseModel):
    stringValue: Optional[str] = None
    intValue: Optional[str] = None
    boolValue: Optional[bool] = None


class OtelKeyValue(BaseModel):
    key: str
    value: OtelAttributeValue


class OtelSpan(BaseModel):
    traceId: str
    spanId: str
    parentSpanId: Optional[str] = ""
    name: str
    startTimeUnixNano: str
    endTimeUnixNano: str
    attributes: Optional[List[OtelKeyValue]] = []
    status: Optional[Dict[str, Any]] = {}


class OtelScopeSpans(BaseModel):
    spans: List[OtelSpan]


class OtelResource(BaseModel):
    attributes: Optional[List[OtelKeyValue]] = []


class OtelResourceSpan(BaseModel):
    resource: OtelResource
    scopeSpans: List[OtelScopeSpans]


class OtelSpanBatch(BaseModel):
    resourceSpans: List[OtelResourceSpan]
