from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config.settings import settings
from api.routes import router
from services.database_service import db_service

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events: startup and shutdown"""
    # Startup
    logger.info("🚀 Starting Voice Assistant Backend...")
    logger.info(f"📊 Database: {settings.database_url}")
    logger.info("✅ SQLite database initialized")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down Voice Assistant Backend...")


# Создаём FastAPI приложение
app = FastAPI(
    title="Voice Assistant API",
    description="AI-powered voice assistant for cargo drivers",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware (должен быть ПЕРЕД роутами!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Подключаем роуты
app.include_router(router)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Voice Assistant API",
        "version": "2.0.0",
        "database": "SQLite"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "ok",
        "database": "SQLite",
        "database_url": settings.database_url,
        "settings": {
            "free_requests_limit": settings.free_requests_limit,
            "paid_access_price": settings.paid_access_price,
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
