from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """Модель пользователя"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String(100), unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Лимиты
    requests_used = Column(Integer, default=0)
    requests_limit = Column(Integer, default=5)
    has_paid_access = Column(Boolean, default=False)
    paid_until = Column(DateTime, nullable=True)
    
    # Связи
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, requests={self.requests_used}/{self.requests_limit})>"


class Message(Base):
    """Модель сообщения в истории разговора"""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user' или 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Дополнительные данные (JSON)
    action_type = Column(String(50), nullable=True)
    action_data = Column(Text, nullable=True)  # JSON string
    
    # Связи
    user = relationship("User", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(role={self.role}, content={self.content[:50]}...)>"


# Создание движка и сессии
def get_engine(database_url: str = "sqlite:///./voice_assistant.db"):
    """Создать SQLAlchemy engine"""
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},  # Для SQLite
        echo=False
    )
    return engine


def get_session_maker(engine):
    """Создать session maker"""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db(engine):
    """Инициализировать базу данных (создать таблицы)"""
    Base.metadata.create_all(bind=engine)
