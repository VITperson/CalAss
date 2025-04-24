# GPT Calendar Planner

Интеллектуальный планировщик календаря с поддержкой естественного языка, использующий GPT-4 для понимания команд и CalDAV для синхронизации с календарем.

## Возможности

- Создание событий с помощью естественного языка
- Просмотр расписания на день
- Интеграция с любым CalDAV-совместимым календарем
- Поддержка временных зон
- Веб-интерфейс для удобного управления

## Требования

- Python 3.9+
- CalDAV-совместимый календарь
- OpenAI API ключ

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/GPT-planner-assistant.git
cd GPT-planner-assistant
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/macOS
# или
venv\Scripts\activate  # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` на основе `.env.example` и заполните его своими данными:
```bash
cp .env.example .env
```

## Настройка

1. Откройте файл `.env` и укажите свои параметры:
```env
# OpenAI settings
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4-1106-preview
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=1000

# CalDAV settings
CALDAV_URL=https://your-caldav-server.com/calendar/
CALDAV_USERNAME=your-username
CALDAV_PASSWORD=your-password
```

2. Настройте временную зону в файле `gpt_calendar_planner/openai_client.py` и `gpt_calendar_planner/caldav_client.py`:
```python
USER_TIMEZONE = ZoneInfo("Your/Timezone")  # например, "Asia/Dubai" для UTC+4
```

## Запуск

1. Запустите веб-сервер:
```bash
python run_web.py
```

2. Откройте браузер и перейдите по адресу `http://localhost:8000`

## Использование

### Примеры команд:

1. Просмотр расписания:
```
что у нас сегодня по расписанию?
```

2. Создание события:
```
создай встречу завтра в 15:00 на 1 час
добавь событие обед сегодня в 14:00 на 30 минут
запланируй совещание в понедельник в 10:00
```

## Разработка

1. Установите зависимости для разработки:
```bash
pip install -e ".[dev]"
```

2. Настройте pre-commit хуки:
```bash
pre-commit install
```

3. Запустите тесты:
```bash
pytest
```

## Безопасность

- Не храните чувствительные данные (API ключи, пароли) в репозитории
- Используйте `.env` файл для локального хранения конфиденциальных данных
- Убедитесь, что `.env` добавлен в `.gitignore`

## Лицензия

MIT License

## Автор

Ваше имя 