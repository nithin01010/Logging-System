from datetime import date, datetime, timedelta
from app.repositories.alert_repository import AlertRepository
from app.repositories.log_repository import LogRepository
from app.repositories.span_repository import SpanRepository
from app.models.alert import AlertRule, AlertTrigger
from app.models.log import LogFilter
from typing import List


class AlertService:
    def __init__(
        self,
        alert_repo: AlertRepository,
        log_repo: LogRepository,
        span_repo: SpanRepository,
    ) -> None:
        self.alert_repo = alert_repo
        self.log_repo = log_repo
        self.span_repo = span_repo

    async def create_rule(self, rule: AlertRule) -> AlertRule:
        return await self.alert_repo.create_rule(rule)

    async def get_all_rules(self) -> List[AlertRule]:
        return await self.alert_repo.get_all_rules()

    async def get_active_rules(self) -> List[AlertRule]:
        return await self.alert_repo.get_active_rules()

    async def get_rule_by_id(self, rule_id: str) -> AlertRule:
        return await self.alert_repo.get_rule_by_id(rule_id)

    async def delete_rule(self, rule_id: str) -> bool:
        return await self.alert_repo.delete_rule(rule_id)

    async def get_all_triggers(self) -> List[AlertTrigger]:
        return await self.alert_repo.get_all_triggers()

    async def evaluate_rules(self) -> None:
        active_rules = await self.alert_repo.get_active_rules()
        now = datetime.utcnow()

        for rule in active_rules:
            start_time = now - timedelta(minutes=rule.window_minutes)
            actual_value = 0.0
            triggered = False
            message = ""

            if rule.metric == "error_rate":
                filters = LogFilter(
                    service=rule.service,
                    start_time=start_time,
                    end_time=now,
                    limit=1000,
                )
                logs = await self.log_repo.get_logs(filters)
                if logs:
                    error_log = [
                        l
                        for l in logs
                        if l.level.upper() in ("ERROR", "FATAL", "CRITICAL")
                    ]
                    actual_value = (len(error_log) / len(logs)) * 100
                    if actual_value >= rule.threshold:
                        triggered = 1
                        message = (
                            "Error rate of" + rule.service + "is" + str(actual_value)
                        )

            elif rule.metric == "latency":
                spans = await self.span_repo.get_spans_by_time(rule.service, start_time)
                if spans:
                    tot = sum(s.duration_ms for s in spans)
                    actual_value = tot / len(spans)
                    if actual_value >= rule.threshold:
                        triggered = True
                        message = f"Average latency of {rule.service} is {actual_value:.2f}ms (threshold: {rule.threshold}ms) over the last {rule.window_minutes} minutes."
            if triggered:
                triggered = AlertTrigger(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    triggered_at=now,
                    actual_value=actual_value,
                    message=message,
                )
                await self.alert_repo.create_trigger(triggered)
                print(f"[ALERT TRIGGERED] {message}")
