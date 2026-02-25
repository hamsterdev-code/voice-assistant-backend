from openai import AsyncOpenAI
from config.settings import settings
from models.prompts import get_system_prompt, get_analysis_prompt
from models.schemas import AiAction, CargoSearchParams, ServiceRecommendation, CargoAnalysis
from services.database_service import db_service
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import json
import logging
import re

logger = logging.getLogger(__name__)


class AiService:
    """Сервис для работы с AI (GPT-4) через BotHub"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.bothub_api_key,
            base_url=settings.bothub_base_url
        )
    
    async def process_message(
        self,
        db: Session,
        user_id: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> tuple[str, Optional[AiAction]]:
        """
        Обработать сообщение пользователя через AI
        
        Args:
            db: Database session
            user_id: ID пользователя
            message: Текст сообщения
            context: Дополнительный контекст (результаты поиска и т.д.)
        
        Returns:
            (response_text, action)
        """
        try:
            # Получаем историю разговора из БД (последние 10 сообщений)
            history = db_service.get_conversation_history(db, user_id, limit=10)
            
            # Формируем сообщения для GPT
            messages = [
                {"role": "system", "content": get_system_prompt()}
            ]
            
            # Добавляем историю
            for msg in history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Добавляем текущее сообщение с контекстом
            user_message = message
            if context:
                user_message += f"\n\nДополнительный контекст: {json.dumps(context, ensure_ascii=False)}"
            
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            logger.info(f"Отправляем запрос к GPT-4 для пользователя {user_id}")
            
            # Вызываем GPT-4
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",  # Используем gpt-4o-mini (быстрая модель)
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            # Парсим ответ
            response_text = response.choices[0].message.content
            logger.info(f"Получен ответ от GPT-4: {response_text[:200]}...")
            
            # Парсим JSON
            try:
                response_data = json.loads(response_text)
                assistant_message = response_data.get("response", "").strip()
                # Убираем markdown-форматирование (**жирный** и т.д.)
                assistant_message = re.sub(r'\*\*([^*]+)\*\*', r'\1', assistant_message)
                assistant_message = re.sub(r'__([^_]+)__', r'\1', assistant_message)
                action_data = response_data.get("action")
                
                # Нормализация cargo_search_params: source/target — пустая строка вместо null
                if action_data and "cargo_search_params" in action_data:
                    params = action_data["cargo_search_params"]
                    if params.get("source") is None:
                        params["source"] = ""
                    if params.get("target") is None:
                        params["target"] = ""
                
                # Валидация: если ответ пустой, используем фоллбэк
                if not assistant_message:
                    logger.warning("⚠️ GPT вернул пустой response, используем фоллбэк")
                    assistant_message = "Понял. Что ещё могу для тебя сделать?"
                
                # Создаём объект действия
                action = None
                if action_data:
                    action = self._parse_action(action_data)
                
                # Сохраняем сообщения в БД
                db_service.save_message(db, user_id, "user", message)
                db_service.save_message(
                    db, user_id, "assistant", assistant_message,
                    action_type=action.type if action else None,
                    action_data=action_data if action else None
                )
                
                return assistant_message, action
                
            except json.JSONDecodeError as e:
                logger.error(f"Ошибка парсинга JSON ответа: {e}")
                logger.error(f"Текст ответа: {response_text}")
                # Возвращаем текст как есть, если это не JSON
                fallback_message = "Извини, получил некорректный ответ. Попробуй переформулировать вопрос."
                db_service.save_message(db, user_id, "user", message)
                db_service.save_message(db, user_id, "assistant", fallback_message)
                return fallback_message, None
            
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {str(e)}")
            return "Извини, произошла ошибка. Попробуй ещё раз.", None
    
    def _parse_action(self, action_data: dict) -> Optional[AiAction]:
        """Парсинг данных действия в объект AiAction"""
        try:
            action_type = action_data.get("type")
            parameters = action_data.get("parameters", {})
            
            # Парсим cargo_search_params
            cargo_search_params = None
            if "cargo_search_params" in action_data:
                cargo_search_params = CargoSearchParams(**action_data["cargo_search_params"])
            
            # Парсим service_recommendation
            service_recommendation = None
            if "service_recommendation" in action_data:
                service_recommendation = ServiceRecommendation(**action_data["service_recommendation"])
            
            # Парсим cargo_analysis
            cargo_analysis = None
            if "cargo_analysis" in action_data:
                cargo_analysis = CargoAnalysis(**action_data["cargo_analysis"])
            
            return AiAction(
                type=action_type,
                parameters=parameters,
                cargo_search_params=cargo_search_params,
                service_recommendation=service_recommendation,
                cargo_analysis=cargo_analysis
            )
        except Exception as e:
            logger.error(f"Ошибка парсинга действия: {e}")
            return None
    
    async def analyze_cargo_results(
        self,
        user_id: str,
        cargo_results: list
    ) -> tuple[str, Optional[CargoAnalysis]]:
        """
        Анализ результатов поиска грузов
        
        Args:
            user_id: ID пользователя
            cargo_results: Список найденных грузов
        
        Returns:
            (analysis_text, cargo_analysis)
        """
        try:
            # Формируем промпт для анализа
            analysis_prompt = get_analysis_prompt(cargo_results)
            
            messages = [
                {"role": "system", "content": get_system_prompt()},
                {"role": "user", "content": analysis_prompt}
            ]
            
            # Вызываем GPT-4
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.5,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            
            response_text = response.choices[0].message.content
            response_data = json.loads(response_text)
            
            # Валидация
            summary = response_data.get("summary", "").strip()
            if not summary:
                summary = "Вот результаты поиска. Выбери подходящий груз."
            
            # Извлекаем данные анализа
            cargo_analysis = CargoAnalysis(
                top_cargos=response_data.get("top_cargos", []),
                summary=summary,
                recommendations=response_data.get("recommendations", [])
            )
            
            return response_data.get("response", ""), cargo_analysis
            
        except Exception as e:
            logger.error(f"Ошибка при анализе результатов: {e}")
            return "Не удалось проанализировать результаты.", None


ai_service = AiService()
