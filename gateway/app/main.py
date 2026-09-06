from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .config import settings
from .storage.database import init_db
from .api import endpoints, websockets

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="Digi-Chalk Gateway", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router)
app.include_router(websockets.router)

@app.get("/health/")
async def health_check():
    """Basic Liveness Check"""
    return {"status": "healthy"}

@app.get("/status/")
async def status_check():
    """Readiness and Status Check"""
    return {
        "status": "ready",
        "service": "digi-chalk-gateway",
        "simulate_hardware": settings.SIMULATE_HARDWARE,
        "backend_url": settings.BACKEND_URL
    }
