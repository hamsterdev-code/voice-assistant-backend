from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from models.database import User, Message, get_engine, get_session_maker, init_db
from config.settings import settings
import json


class DatabaseService:
    """Сервис для работы с SQLite базой данных"""
    
    def __init__(self):
        self.engine = get_engine(settings.database_url)
        self.SessionLocal = get_session_maker(self.engine)
        init_db(self.engine)
    
    def get_db(self):
        """Получить сессию базы данных"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    # ============= USERS =============
    
    def get_or_create_user(self, db: Session, telegram_id: str) -> User:
        """Получить или создать пользователя"""
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        
        if not user:
            user = User(
                telegram_id=telegram_id,
                requests_used=0,
                requests_limit=settings.free_requests_limit,
                has_paid_access=False
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        return user
    
    def get_usage(self, db: Session, telegram_id: str) -> dict:
        """Получить статистику использования"""
        user = self.get_or_create_user(db, telegram_id)
        
        return {
            "user_id": user.telegram_id,
            "requests_used": user.requests_used,
            "requests_limit": user.requests_limit,
            "has_paid_access": user.has_paid_access,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "paid_until": user.paid_until.isoformat() if user.paid_until else None,
        }
    
    def increment_usage(self, db: Session, telegram_id: str) -> dict:
        """Увеличить счётчик использования"""
        user = self.get_or_create_user(db, telegram_id)
        user.requests_used += 1
        db.commit()
        
        return self.get_usage(db, telegram_id)
    
    def check_limit(self, db: Session, telegram_id: str) -> tuple[bool, int]:
        """
        Проверить лимит запросов.
        Сейчас безлимитный режим для всех пользователей.
        Returns:
            (can_request, requests_remaining)
        """
        _ = self.get_or_create_user(db, telegram_id)
        return True, 999  # Безлимит
    
    def activate_paid_access(self, db: Session, telegram_id: str, days: int = 30) -> dict:
        """Активировать платный доступ"""
        user = self.get_or_create_user(db, telegram_id)
        user.has_paid_access = True
        user.paid_until = datetime.utcnow() + timedelta(days=days)
        user.requests_used = 0  # Сбрасываем счётчик
        db.commit()
        
        return self.get_usage(db, telegram_id)
    
    # ============= MESSAGES =============
    
    def save_message(
        self, 
        db: Session, 
        telegram_id: str, 
        role: str, 
        content: str,
        action_type: Optional[str] = None,
        action_data: Optional[Dict] = None
    ) -> Message:
        """Сохранить сообщение в историю"""
        user = self.get_or_create_user(db, telegram_id)
        
        message = Message(
            user_id=user.id,
            role=role,
            content=content,
            action_type=action_type,
            action_data=json.dumps(action_data) if action_data else None
        )
        
        db.add(message)
        db.commit()
        db.refresh(message)
        
        return message
    
    def get_conversation_history(
        self, 
        db: Session, 
        telegram_id: str, 
        limit: int = 20
    ) -> List[Dict]:
        """Получить историю разговора (последние N сообщений)"""
        user = self.get_or_create_user(db, telegram_id)
        
        messages = (
            db.query(Message)
            .filter(Message.user_id == user.id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .all()
        )
        
        # Разворачиваем (чтобы старые были первыми)
        messages = list(reversed(messages))
        
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat() if msg.created_at else None,
                "action_type": msg.action_type,
                "action_data": json.loads(msg.action_data) if msg.action_data else None,
            }
            for msg in messages
        ]
    
    def get_full_conversation_history(
        self,
        db: Session,
        telegram_id: str
    ) -> List[Dict]:
        """Получить ВСЮ историю разговора (для отображения на фронте)"""
        user = self.get_or_create_user(db, telegram_id)
        
        messages = (
            db.query(Message)
            .filter(Message.user_id == user.id)
            .order_by(Message.created_at.asc())
            .all()
        )
        
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat() if msg.created_at else None,
                "action_type": msg.action_type,
                "action_data": json.loads(msg.action_data) if msg.action_data else None,
            }
            for msg in messages
        ]
    
    def clear_conversation(self, db: Session, telegram_id: str):
        """Очистить всю историю разговора"""
        user = self.get_or_create_user(db, telegram_id)
        
        db.query(Message).filter(Message.user_id == user.id).delete()
        db.commit()


# Глобальный экземпляр
db_service = DatabaseService()
