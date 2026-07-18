from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.database import connect_to_mongo, close_mongo_connection
from app.core.database import get_database
from app.api.auth import router as auth_router
from app.core.middleware import logging_middleware
from app.core.init_db import init_database
from app.api.keys import router as keys_router
from app.api.logs import router as logs_router
from app.api.spans import router as spans_router
from strawberry.fastapi import GraphQLRouter
from app.graphql.schema import schema
from app.api.alerts import router as alerts_router
from app.api.alerts import get_alert_service
from app.workers.alert_worker import start_alert_worker, stop_alert_worker



@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    await init_database()
    alert_service = get_alert_service()
    start_alert_worker(alert_service)
    print("Starting up service")
    yield
    stop_alert_worker()
    await close_mongo_connection()
    print("Shutting down service")


app = FastAPI(
    title="Logging System",
    description="The logging system is built with Graphql along with Next js",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(BaseHTTPMiddleware, dispatch=logging_middleware)

app.include_router(auth_router)
app.include_router(keys_router)
app.include_router(logs_router)
app.include_router(spans_router)
app.include_router(alerts_router)

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/health", tags=["Health"])
async def health_check():
    db = get_database()
    db_status = "connected" if db is not None else "disconnected"
    return {"status": "healthy", "database": db_status}
