from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


class TranscriptionRequest(BaseModel):
    """Запрос на транскрипцию аудио"""
    user_id: str = Field(..., description="ID пользователя Telegram")


class TranscriptionResponse(BaseModel):
    """Ответ с транскрипцией"""
    text: str = Field(..., description="Распознанный текст")
    duration: Optional[float] = Field(None, description="Длительность аудио в секундах")


class ProcessMessageRequest(BaseModel):
    """Запрос на обработку сообщения"""
    user_id: str = Field(..., description="ID пользователя Telegram")
    message: str = Field(..., description="Текст сообщения от пользователя")
    context: Optional[Dict[str, Any]] = Field(None, description="Дополнительный контекст")


class CargoSearchParams(BaseModel):
    """Параметры поиска груза"""
    source: Optional[str] = None
    target: Optional[str] = None
    date_start: Optional[str] = None
    date_end: Optional[str] = None
    vehicle_type: Optional[str] = None
    mass: Optional[float] = None
    volume: Optional[float] = None
    cost_per_km_min: Optional[float] = None
    cost_per_km_max: Optional[float] = None


class ServiceRecommendation(BaseModel):
    """Рекомендация услуги"""
    service_id: str
    service_title: str
    category_id: int
    category_title: str
    reason: str


class CargoAnalysis(BaseModel):
    """Анализ найденных грузов"""
    top_cargos: List[int] = Field(default_factory=list, description="ID топ-3 грузов")
    summary: str = Field(..., description="Краткое резюме по результатам")
    recommendations: List[str] = Field(default_factory=list)


class AiAction(BaseModel):
    """Действие, которое должен выполнить фронтенд"""
    type: Literal[
        "search_cargo",
        "open_service",
        "request_callback",
        "show_cargo_details",
        "analyze_results",
        "chat"
    ]
    parameters: Optional[Dict[str, Any]] = None
    cargo_search_params: Optional[CargoSearchParams] = None
    service_recommendation: Optional[ServiceRecommendation] = None
    cargo_analysis: Optional[CargoAnalysis] = None


class ProcessMessageResponse(BaseModel):
    """Ответ на обработку сообщения"""
    response: str = Field(..., description="Текстовый ответ ассистента")
    action: Optional[AiAction] = Field(None, description="Действие для выполнения")
    requests_remaining: int = Field(..., description="Оставшихся запросов")


class UsageStats(BaseModel):
    """Статистика использования"""
    user_id: str
    requests_used: int
    requests_limit: int
    has_paid_access: bool
    created_at: datetime
    paid_until: Optional[datetime] = None


class PaymentRequest(BaseModel):
    """Запрос на оплату доступа"""
    user_id: str
    amount: int = 1000


class PaymentResponse(BaseModel):
    """Ответ на запрос оплаты"""
    success: bool
    message: str
    requests_remaining: int
