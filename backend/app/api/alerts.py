from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.alert import AlertRule, AlertTrigger
from app.core.database import get_database
from app.repositories.alert_repository import AlertRepository
from app.repositories.log_repository import LogRepository
from app.repositories.span_repository import SpanRepository
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["alerts"])


def get_alert_service():
    db = get_database()
    alert_repo = AlertRepository(db)
    log_repo = LogRepository(db)
    span_repo = SpanRepository(db)
    return AlertService(alert_repo, log_repo, span_repo)


@router.post("/rules", response_model=AlertRule, status_code=status.HTTP_201_CREATED)
async def create_rule(
    rule: AlertRule, service: AlertService = Depends(get_alert_service)
):
    return await service.create_rule(rule)


@router.get("/rules", response_model=List[AlertRule])
async def get_rules(service: AlertService = Depends(get_alert_service)):
    return await service.get_all_rules()


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: str, service: AlertService = Depends(get_alert_service)
):
    success = await service.delete_rule(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rule not found")


@router.get("/triggers", response_model=List[AlertTrigger])
async def get_triggers(service: AlertService = Depends(get_alert_service)):
    return await service.get_all_triggers()
