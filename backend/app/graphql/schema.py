import strawberry
from typing import List, Optional
from app.graphql.types import LogType, TraceNodeType
from app.graphql.resolvers import resolve_logs, resolve_trace, resolve_services


@strawberry.type
class Query:
    logs: List[LogType] = strawberry.field(resolver=resolve_logs)
    trace: Optional[TraceNodeType] = strawberry.field(resolver=resolve_trace)
    services: List[str] = strawberry.field(resolver=resolve_services)


schema = strawberry.Schema(query=Query)
