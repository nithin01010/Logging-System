from typing import List, Dict, Optional
from datetime import date, datetime, timezone
from app.repositories.span_repository import SpanRepository
from app.models.span import SpanDocument, OtelSpanBatch, TraceNode


class SpanService:
    def __init__(self, repo: SpanRepository) -> None:
        self.repo = repo

    async def ingest_span(self, batch: OtelSpanBatch) -> bool:
        spans = []

        for resource_span in batch.resourceSpans:
            service_name = "unknown"
            for kv in resource_span.resource.attributes:
                if kv.key == "service.name":
                    service_name = kv.value.stringValue
                    break
            for scope_span in resource_span.scopeSpans:
                for otel_span in scope_span.spans:

                    start_time = datetime.fromtimestamp(
                            int(otel_span.startTimeUnixNano) / 1_000_000_000,
                            tz=timezone.utc
                            )
                    end_time = datetime.fromtimestamp(
                            int(otel_span.endTimeUnixNano) / 1_000_000_000,
                            tz=timezone.utc
                            )
                    duration_ms = (end_time - start_time).total_seconds() * 1000
                    status_code = (otel_span.status or {}).get("code", 0)
                    attributes = {kv.key: kv.value.stringValue for kv in (otel_span.attributes or [])}

                    spans.append(SpanDocument(
                        trace_id=otel_span.traceId,
                        span_id=otel_span.spanId,
                        parent_span_id=otel_span.parentSpanId or None,
                        service_name=service_name,
                        operation_name=otel_span.name,
                        start_time=start_time,
                        end_time=end_time,
                        duration_ms=duration_ms,
                        status_code=status_code,
                        attributes=attributes
                        ))
        return await self.repo.insert_batch(spans)
    async def get_trace_tree(self, trace_id: str) -> Optional[TraceNode]:
        spans = await self.repo.get_by_trace_id(trace_id)
        if not spans:
            return None

        nodes: Dict[str, TraceNode] = {}
        for s in spans:
            nodes[s.span_id] = TraceNode(
                    span_id=s.span_id,
                    parent_span_id=s.parent_span_id,
                    service_name=s.service_name,
                    operation_name=s.operation_name,
                    status_code=s.status_code,
                    start_time=s.start_time,
                    duration_ms=s.duration_ms
                    )
        root = None
        for s in spans:
            node = nodes[s.span_id]
            if s.parent_span_id and s.parent_span_id in nodes:
                nodes[s.parent_span_id].children.append(node)
            else:
                root = node
        return root
