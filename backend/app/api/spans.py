
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from app.models.span import OtelSpanBatch, TraceNode
from app.core.security import get_current_api_key
from app.core.database import get_database
from app.repositories.span_repository import SpanRepository
from app.services.span_service import SpanService

router = APIRouter(tags=["spans"])


def get_span_service():

    db = get_database()
    repo = SpanRepository(db)
    return SpanService(repo)


@router.post("/v1/traces", status_code=status.HTTP_200_OK)
async def ingest_spans(
    batch: OtelSpanBatch,
    service: SpanService = Depends(get_span_service),
    _ = Depends(get_current_api_key),
):
    result = await service.ingest_spans(batch)
    if not result:
        raise HTTPException(status_code=500)
    return {"message": "spans ingested"}


@router.get("/traces/{trace_id}", response_model=Optional[TraceNode])
async def get_trace(trace_id: str, service: SpanService = Depends(get_span_service)):
    trace = await service.get_trace_tree(trace_id)
    if not trace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trace not found")
    return trace
