from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from models.schemas import (
    ProcessMessageRequest,
    ProcessMessageResponse,
    PaymentRequest,
    PaymentResponse
)
from services.ai_service import ai_service
from services.database_service import db_service
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice", tags=["voice-assistant"])


# Dependency для получения DB сессии
def get_db():
    db = db_service.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/process", response_model=ProcessMessageResponse)
async def process_message(request: ProcessMessageRequest, db: Session = Depends(get_db)):
    """
    Обработать текстовое сообщение через AI
    При первом запросе автоматически создается новый пользователь
    """
    try:
        # Проверяем лимит запросов (автоматически создает пользователя если нужно)
        can_request, requests_remaining = db_service.check_limit(db, request.user_id)
        
        if not can_request:
            raise HTTPException(
                status_code=429,
                detail={
                    "message": "Исчерпан лимит бесплатных запросов. Оплатите доступ для продолжения.",
                    "requests_remaining": 0,
                    "price": settings.paid_access_price
                }
            )
        
        # Обрабатываем сообщение через AI
        response_text, action = await ai_service.process_message(
            db=db,
            user_id=request.user_id,
            message=request.message,
            context=request.context
        )
        
        # Увеличиваем счётчик
        db_service.increment_usage(db, request.user_id)
        
        # Пересчитываем оставшиеся запросы
        _, requests_remaining = db_service.check_limit(db, request.user_id)
        
        return ProcessMessageResponse(
            response=response_text,
            action=action,
            requests_remaining=requests_remaining
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get("/history/{user_id}")
async def get_full_history(user_id: str, db: Session = Depends(get_db)):
    """
    Получить полную историю разговора пользователя
    """
    try:
        history = db_service.get_full_conversation_history(db, user_id)
        return {"messages": history}
        
    except Exception as e:
        logger.error(f"Ошибка при получении истории: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.post("/payment", response_model=PaymentResponse)
async def process_payment(request: PaymentRequest, db: Session = Depends(get_db)):
    """
    Обработать оплату доступа
    
    ВНИМАНИЕ: Это заглушка! В продакшене нужно интегрировать реальную платёжную систему
    """
    try:
        # TODO: Интеграция с реальной платёжной системой
        db_service.activate_paid_access(db, request.user_id, days=30)
        
        return PaymentResponse(
            success=True,
            message="Оплата прошла успешно! Доступ активирован на 30 дней.",
            requests_remaining=999
        )
        
    except Exception as e:
        logger.error(f"Ошибка при обработке платежа: {str(e)}")
        return PaymentResponse(
            success=False,
            message="Ошибка при обработке платежа. Попробуйте позже.",
            requests_remaining=0
        )


@router.get("/database/download")
async def download_database():
    """
    Скачать полную базу данных voice_assistant.db (все диалоги, пользователи).
    """
    # sqlite:///./voice_assistant.db -> ./voice_assistant.db
    db_url = settings.database_url
    if db_url.startswith("sqlite:///"):
        db_path = Path(db_url.replace("sqlite:///", ""))
    else:
        raise HTTPException(status_code=500, detail="Неподдерживаемый формат database_url")
    if not db_path.exists():
        raise HTTPException(status_code=404, detail="База данных не найдена")
    return FileResponse(
        path=str(db_path.resolve()),
        filename="voice_assistant.db",
        media_type="application/octet-stream",
    )


@router.delete("/conversation/{user_id}")
async def clear_conversation(user_id: str, db: Session = Depends(get_db)):
    """
    Очистить историю разговора пользователя
    """
    try:
        db_service.clear_conversation(db, user_id)
        return {"message": "История разговора очищена"}
        
    except Exception as e:
        logger.error(f"Ошибка при очистке истории: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
