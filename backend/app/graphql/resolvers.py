from typing import List, Optional
from app.graphql.types import LogType, TraceNodeType

from app.core.database import get_database
from app.repositories.log_repository import LogRepository
from app.repositories.span_repository import SpanRepository
from app.services.log_service import LogService
from app.models.log import LogFilter
from app.services.span_service import SpanService


async def resolve_logs(
    service: Optional[str] = None,
    level: Optional[str] = None,
    limit: int = 100
) -> List[LogType]:
    db = get_database()
    repo = LogRepository(db)
    log_service = LogService(repo)

    filter1 = LogFilter(service=service, level=level, limit=limit)
    log_entries = await log_service.query_logs(filter1)

    return [
        LogType(
            id=str(log.id) if log.id else None,
            service=log.service,
            level=log.level,
            message=log.message,
            timestamp=log.timestamp,
            trace_id=log.trace_id,
            span_id=log.span_id,
            raw=log.raw
        )
        for log in log_entries
    ]


async def resolve_trace(trace_id: str) -> Optional[TraceNodeType]:
    db = get_database()
    repo = SpanRepository(db)
    span_service = SpanService(repo)

    tree = await span_service.get_trace_tree(trace_id)
    if not tree:
        return None

    def convert_node(node) -> TraceNodeType:
        return TraceNodeType(
            span_id=node.span_id,
            parent_span_id=node.parent_span_id,
            service_name=node.service_name,
            operation_name=node.operation_name,
            start_time=node.start_time,
            duration_ms=node.duration_ms,
            status_code=node.status_code,
            children=[convert_node(c) for c in node.children]
        )

    return convert_node(tree)


async def resolve_services() -> List[str]:
    db = get_database()
    if db is None:
        return []
    return await db["logs"].distinct("service")


from app.graphql.types import AlertRuleType, AlertTriggerType
from app.repositories.alert_repository import AlertRepository
from app.services.alert_service import AlertService


def get_graphql_alert_service() -> AlertService:
    db = get_database()
    alert_repo = AlertRepository(db)
    return AlertService(alert_repo, None, None)


async def resolve_alert_rules() -> List[AlertRuleType]:
    service = get_graphql_alert_service()
    rules = await service.get_all_rules()
    return [
        AlertRuleType(
            id=str(r.id) if r.id else "",
            name=r.name,
            service=r.service,
            metric=r.metric,
            threshold=r.threshold,
            window_minutes=r.window_minutes,
        )
        for r in rules
    ]


async def resolve_alert_triggers() -> List[AlertTriggerType]:
    service = get_graphql_alert_service()
    triggers = await service.get_all_triggers()
    return [
        AlertTriggerType(
            id=str(t.id) if t.id else None,
            rule_id=str(t.rule_id),
            rule_name=t.rule_name,
            triggered_at=t.triggered_at,
            actual_value=t.actual_value,
            message=t.message,
        )
        for t in triggers
    ]

