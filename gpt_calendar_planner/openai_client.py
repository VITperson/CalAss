from openai import OpenAI
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import List, Dict, Any, Optional
from .config import settings
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

USER_TIMEZONE = ZoneInfo("Asia/Dubai")  # UTC+4

class OpenAIClient:
    def __init__(self):
        try:
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_model
            self.temperature = settings.openai_temperature
            self.max_tokens = settings.openai_max_tokens
            self.functions = [
                {
                    "name": "create_event",
                    "description": "Создать событие в календаре в локальной временной зоне пользователя (Asia/Dubai, UTC+4)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Название события"
                            },
                            "dt_start": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Время начала события в ISO формате с учетом временной зоны Asia/Dubai (UTC+4)"
                            },
                            "dt_end": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Время окончания события в ISO формате с учетом временной зоны Asia/Dubai (UTC+4)"
                            },
                            "location": {
                                "type": "string",
                                "description": "Место проведения события"
                            },
                            "notes": {
                                "type": "string",
                                "description": "Заметки к событию"
                            }
                        },
                        "required": ["title", "dt_start", "dt_end"]
                    }
                },
                {
                    "name": "delete_event",
                    "description": "Удалить событие из календаря",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "event_id": {"type": "string"}
                        },
                        "required": ["event_id"]
                    }
                },
                {
                    "name": "get_events",
                    "description": "Получить список событий за период в локальной временной зоне пользователя (Asia/Dubai, UTC+4). Использовать ТОЛЬКО для запросов о существующих событиях, НЕ для создания новых.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Начало периода в ISO формате с учетом временной зоны Asia/Dubai (UTC+4)"
                            },
                            "end_date": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Конец периода в ISO формате с учетом временной зоны Asia/Dubai (UTC+4)"
                            }
                        },
                        "required": ["start_date", "end_date"]
                    }
                }
            ]
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise

    def process_command(self, command: str) -> Dict[str, Any]:
        try:
            # Получаем текущую дату в локальной временной зоне пользователя
            current_time = datetime.now(USER_TIMEZONE)
            
            # Если запрос про "сегодня" и не содержит слов создания события
            create_keywords = ["создай", "добавь", "запланируй", "назначь"]
            is_create_command = any(keyword in command.lower() for keyword in create_keywords)
            
            if "сегодня" in command.lower() and not is_create_command:
                start_of_day = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
                end_of_day = current_time.replace(hour=23, minute=59, second=59, microsecond=999999)
                
                logger.info(f"Processing 'today' request in timezone {USER_TIMEZONE}")
                logger.info(f"Start of day: {start_of_day.isoformat()}")
                logger.info(f"End of day: {end_of_day.isoformat()}")
                
                return {
                    "function": "get_events",
                    "arguments": json.dumps({
                        "start_date": start_of_day.isoformat(),
                        "end_date": end_of_day.isoformat()
                    })
                }
            
            # Для других запросов используем OpenAI
            context = f"""
            Текущая дата и время: {current_time.isoformat()}
            Временная зона пользователя: {USER_TIMEZONE} (UTC+4)
            
            ВАЖНО: 
            1. Все даты и время должны быть в локальной временной зоне пользователя (UTC+4).
            2. Для создания событий используйте функцию create_event.
            3. Для просмотра событий используйте функцию get_events.
            4. При создании события, если длительность не указана, используйте 30 минут по умолчанию.
            
            Примеры запросов на создание:
            - "создай встречу завтра в 15:00" -> create_event с dt_start="2025-04-24T15:00:00+04:00" и dt_end="2025-04-24T15:30:00+04:00"
            - "добавь событие сегодня в 18:00 на 2 часа" -> create_event с dt_start="2025-04-23T18:00:00+04:00" и dt_end="2025-04-23T20:00:00+04:00"
            
            Запрос пользователя: {command}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": context}],
                functions=self.functions,
                function_call="auto"
            )
            
            message = response.choices[0].message
            if message.function_call:
                logger.info(f"Function call detected: {message.function_call.name}")
                logger.info(f"Arguments: {message.function_call.arguments}")
                return {
                    "function": message.function_call.name,
                    "arguments": message.function_call.arguments
                }
            logger.warning("No function call detected in OpenAI response")
            return {"error": "Не удалось определить команду"}
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            return {"error": str(e)}

    def get_advice(self, events: List[Dict[str, Any]]) -> str:
        try:
            prompt = f"""
            Проанализируй следующие события в календаре и дай рекомендации по тайм-менеджменту:
            {events}
            
            Учти:
            1. Распределение времени
            2. Возможные конфликты
            3. Рекомендации по оптимизации
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            advice = response.choices[0].message.content
            logger.info("Generated time management advice")
            return advice
        except Exception as e:
            logger.error(f"Error getting advice: {e}")
            raise

    def create_event(self, title: str, start: datetime, end: datetime, 
                    location: Optional[str] = None, notes: Optional[str] = None) -> str:
        try:
            # Убеждаемся, что даты в локальной временной зоне пользователя
            if start.tzinfo is None:
                start = start.replace(tzinfo=USER_TIMEZONE)
            elif start.tzinfo != USER_TIMEZONE:
                start = start.astimezone(USER_TIMEZONE)
                
            if end.tzinfo is None:
                end = end.replace(tzinfo=USER_TIMEZONE)
            elif end.tzinfo != USER_TIMEZONE:
                end = end.astimezone(USER_TIMEZONE)

            logger.info(f"Creating event in local timezone ({USER_TIMEZONE})")
            logger.info(f"Start: {start}, End: {end}")
            
            # Остальной код функции остается без изменений
            return "success"
        except Exception as e:
            logger.error(f"Failed to create event: {e}")
            raise

    def get_events(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        try:
            # Убеждаемся, что даты в локальной временной зоне пользователя
            if start_date.tzinfo is None:
                start_date = start_date.replace(tzinfo=USER_TIMEZONE)
            elif start_date.tzinfo != USER_TIMEZONE:
                start_date = start_date.astimezone(USER_TIMEZONE)
                
            if end_date.tzinfo is None:
                end_date = end_date.replace(tzinfo=USER_TIMEZONE)
            elif end_date.tzinfo != USER_TIMEZONE:
                end_date = end_date.astimezone(USER_TIMEZONE)

            logger.info(f"Getting events in local timezone ({USER_TIMEZONE})")
            logger.info(f"Start date: {start_date}, End date: {end_date}")
            
            # Здесь будет код для получения событий
            return []
        except Exception as e:
            logger.error(f"Failed to get events: {e}")
            raise 