from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.span import SpanDocument
from typing import List


class SpanRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.span_rep = db["spans"]

    async def insert_batch(self, spans: List[SpanDocument]) -> bool:
        doc = [s.model_dump(by_alias=True, exclude={"id"}) for s in spans]
        if not doc:
            return False
        res = await self.span_rep.insert_many(doc)
        return len(res.inserted_ids) > 0

    async def get_by_trace_id(self, trace_id: str) -> List[SpanDocument]:
        query = {"trace_id": trace_id}

        cursor = self.span_rep.find(query)
        res = await cursor.to_list(length=1000)
        return [SpanDocument(**r) for r in res]
