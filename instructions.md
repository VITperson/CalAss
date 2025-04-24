# Проект: Интеграция OpenAI API ↔ Apple Calendar (iCloud CalDAV)

> **Назначение файла** — быть системной инструкцией для думающей LLM и чек‑листом для разработчика.

---

## 1 Общее описание
Локальное Python‑приложение, работающее с вашим OpenAI API‑ключом и календарём iCloud через CalDAV. Возможности:
* создание / удаление / просмотр событий по естественному языку;
* генерация персональных советов по тайм‑менеджменту исходя из занятости и привычек;
* динамические рекомендации по оптимальному расписанию.

---

## 2 Стек технологий
| Слой            | Выбор                                      |
|-----------------|---------------------------------------------|
| Язык            | **Python 3.11+**                            |
| NLP             | `openai>=1.0` (GPT‑4o с function‑calling)   |
| CalDAV          | `caldav`, `icalendar`                       |
| CLI / API       | `typer` (оболочка) / `fastapi` (опц.)       |
| Хранение        | `sqlite3` или JSON + `cryptography`         |
| Планировщик     | `apscheduler`                               |
| Dev‑инструменты | `black`, `mypy`, `pre‑commit`, `python-dotenv`

---

## 3 Подготовка окружения
```bash
python -m venv venv && source venv/bin/activate
pip install openai caldav icalendar typer python-dotenv apscheduler cryptography
```

### .env (не коммитить!)
```env
OPENAI_API_KEY=sk-…
ICLOUD_USER=you@icloud.com
ICLOUD_APP_PW=xxxx-xxxx-xxxx-xxxx
ICLOUD_CAL=https://caldav.icloud.com/…/calendars/private/
```

Права файла `.env` — `chmod 600 .env`.

---

## 4 Архитектура слоёв
1. **NLP‑слой** — Chat Completions → функции (`create_event`, `delete_event`, `get_events`, `get_advice`).
2. **CalDAV‑слой** — низкоуровневые HTTP PUT / DELETE / REPORT к iCloud.
3. **Бизнес‑логика** — трансформация JSON ↔ VEVENT, агрегация расписания.
4. **Интерфейс** — CLI («Бронируй йогу завтра в 17:00») или REST‑эндпойнт для бота.

### Пример описаний функций для GPT
```json
[
  {
    "name": "create_event",
    "description": "Создать событие в календаре",
    "parameters": {
      "type": "object",
      "properties": {
        "title": {"type": "string"},
        "dt_start": {"type": "string", "format": "date-time"},
        "dt_end":   {"type": "string", "format": "date-time"},
        "location": {"type": "string"},
        "notes":    {"type": "string"}
      },
      "required": ["title", "dt_start", "dt_end"]
    }
  },
  …
]
```

---

## 5 Сводка API‑действий
| Команда      | Действие OpenAI                       | Действие CalDAV                                    |
|--------------|---------------------------------------|----------------------------------------------------|
| create_event | функция `create_event` → JSON         | `PUT <calendar>/<uuid>.ics` с VEVENT               |
| delete_event | `delete_event(event_id)`              | `DELETE <event>.ics`                               |
| get_events   | `get_events(date_range)`              | `REPORT calendar-query` + `time-range`             |
| get_advice   | pass events + правила → GPT‑4o ответ   | —                                                |

---

## 6 Поток данных (ASCII‑диаграмма)
```
User ⟶ GPT (NLP) ⟶ Orchestrator ⟶ CalDAV ⟶ iCloud
 ↑                                          ↓
 └──────────── tips  <──────── schedule ─────┘
```

---

## 7 Пошаговый план разработки
1. **PoC CLI** \- 1 скрипт `planner.py` на Typer.
2. Добавить функции GPT + Pydantic‑валидацию JSON.
3. Реализовать CalDAV‑клиент (create / list / delete).
4. Соединить всё в Orchestrator, вернуть советы пользователю.
5. Писать PyTest‑юнит‑тесты, мокая OpenAI и CalDAV.
6. (Опционально) обернуть в FastAPI + Telegram‑бот.

---

## 8 Безопасность
* **Ключи** — только локально, `.env`, 0600.
* **App‑Specific PW** — можно быстро отозвать в iCloud.
* **TLS** — CalDAV уже под HTTPS; проверять cert.
* **Шифрация кэша** — `cryptography.fernet`.
* **Минимизация логов** — без личных данных.

---

## 9 Проблемы & решения
| Риск                         | Митигировать                                      |
|------------------------------|---------------------------------------------------|
| Неправильный TZ / DST        | Хранить UTC, локализовать вывод.                 |
| 2FA‑циклы iCloud             | Использовать App‑Specific PW; повторить login.   |
| Высокие затраты OpenAI       | Кэшировать, использовать GPT‑4o‑mini для рутин.  |
| Неоднозначные даты («вечером»)| Правило в prompt: возвращать ISO 8601.           |

---

## 10 Дорожная карта
* **v0.1** — CLI, создание / удаление / просмотр ± тесты.
* **v0.2** — Советы и автоматический re‑scheduler.
* **v0.3** — FastAPI + Telegram Webhook.
* **v1.0** — UI (menubar macOS) + шифрование базы.

---

> **Готово к использованию в качестве system‑prompt или технической спецификации.**

