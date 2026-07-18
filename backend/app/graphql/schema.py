import strawberry
from typing import List, Optional
from app.graphql.types import LogType, TraceNodeType, AlertRuleType, AlertTriggerType
from app.graphql.resolvers import (
    resolve_logs,
    resolve_trace,
    resolve_services,
    resolve_alert_rules,
    resolve_alert_triggers
)


@strawberry.type
class Query:
    logs: List[LogType] = strawberry.field(resolver=resolve_logs)
    trace: Optional[TraceNodeType] = strawberry.field(resolver=resolve_trace)
    services: List[str] = strawberry.field(resolver=resolve_services)
    alert_rules: List[AlertRuleType] = strawberry.field(resolver=resolve_alert_rules)
    alert_triggers: List[AlertTriggerType] = strawberry.field(resolver=resolve_alert_triggers)


schema = strawberry.Schema(query=Query)

