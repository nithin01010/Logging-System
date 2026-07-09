import time
import logging
from fastapi import Request

logger = logging.getLogger("app.middleware")


async def logging_middleware(req: Request, call_next):
    start_time = time.time()
    res = await call_next(req)

    process_time = (time.time() - start_time) * 1000

    logger.info(
        f"{req.method} {req.url.path} status={res.status_code} took={process_time:.2f}ms"
    )
    return res
