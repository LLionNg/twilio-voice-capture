import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from loguru import logger

from app.api import routes, websocket
from app.api.deps import init_services, cleanup_services
from app.core.config import get_settings


logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    
    logger.info("Starting voice capture service")
    logger.info(f"Sample rate: {settings.sample_rate}Hz, Channels: {settings.audio_channels}")
    
    init_services()
    
    Path(settings.output_dir).mkdir(parents=True, exist_ok=True)
    
    logger.info("Services initialized")
    
    yield
    
    await cleanup_services()
    logger.info("Shutdown complete")


app = FastAPI(
    title="Voice Capture API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)
app.include_router(websocket.router)


@app.get("/")
async def root():
    frontend_path = Path("frontend/index.html")
    if frontend_path.exists():
        return FileResponse(frontend_path)
    
    return {
        "name": "Voice Capture API",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )