from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.models.alert import AlertRule, AlertTrigger
from typing import Optional, List


class AlertRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.rules = db["alert_rules"]
        self.triggers = db["alert_triggers"]

    async def create_rule(self, rule: AlertRule) -> AlertRule:
        rule_dict = rule.model_dump(by_alias=True, exclude={"id"})
        res = await self.rules.insert_one(rule_dict)
        rule.id = str(res.inserted_id)
        return rule

    async def get_all_rules(self) -> List[AlertRule]:
        cursor = self.rules.find()
        res = await cursor.to_list(length=100)
        return [AlertRule(**r) for r in res]

    async def get_active_rules(self) -> List[AlertRule]:
        cursor = self.rules.find({"is_active": True})
        res = await cursor.to_list(length=100)
        return [AlertRule(**r) for r in res]

    async def get_rule_by_id(self, id: str) -> Optional[AlertRule]:
        rule_dict = await self.rules.find_one({"_id": ObjectId(id)})
        if not rule_dict:
            return None
        return AlertRule(**rule_dict)

    async def delete_rule(self, rule_id: str) -> bool:
        res = await self.rules.delete_one({"_id": ObjectId(rule_id)})
        return res.deleted_count > 0

    async def create_trigger(self, trigger: AlertTrigger) -> AlertTrigger:
        trig_dict = trigger.model_dump(by_alias=True, exclude={"id"})
        res = await self.triggers.insert_one(trig_dict)
        trigger.id = str(res.inserted_id)
        return trigger

    async def get_all_triggers(self) -> List[AlertTrigger]:
        cursor = self.triggers.find().sort("triggered_at", -1)
        res = await cursor.to_list(length=100)
        return [AlertTrigger(**t) for t in res]
