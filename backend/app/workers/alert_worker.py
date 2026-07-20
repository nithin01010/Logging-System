from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.alert_service import AlertService

scheduler = AsyncIOScheduler()

def start_alert_worker(alert_service: AlertService) -> None:
    scheduler.add_job(
        alert_service.evaluate_rules,
        "interval",
        seconds=60,
        id="alert_evaluator",
        replace_existing=True
    )
    scheduler.start()

def stop_alert_worker() -> None:
    scheduler.shutdown()
