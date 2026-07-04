from fastapi import Fastapi
from fast.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager


@asynccontextmanager
asyn def lifespan(app: Fastapi):
    print("Starting up service")
    yield
    print("Shutting down service")

app = Fastapi(
        title="Logging System",
        description="The logging system is built with Graphql along with Next js"
        )

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
        )

@app.get('/health', tags=["Health"])
async def health_check():
    return {
            "status": "healthy",
            "database": "disconnected"
            }
