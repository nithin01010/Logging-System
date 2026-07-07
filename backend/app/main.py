from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import connect_to_mongo, close_mongo_connection, get_database
from app.api.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    print("Starting up service")
    yield
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

app.include_router(auth_router)


@app.get("/health", tags=["Health"])
async def health_check():
    db = get_database()
    db_status = "connected" if db is not None else "disconnected"
    return {"status": "healthy", "database": db_status}
