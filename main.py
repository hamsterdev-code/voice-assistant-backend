import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from api.routes import router
from services.database_service import db_service

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)



# Создаём FastAPI приложение
app = FastAPI(
    title="Voice Assistant API",
    description="AI-powered voice assistant for cargo drivers",
    version="2.0.0",
)

# CORS middleware (должен быть ПЕРЕД роутами!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Подключаем роуты
app.include_router(router)


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Voice Assistant API",
        "version": "2.0.0",
        "database": "SQLite"
    }


@app.get("/health")
def health():
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


