from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import json
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from .openai_client import OpenAIClient
from .caldav_client import CalDAVClient

app = FastAPI()

# Настраиваем шаблоны и статические файлы
templates = Jinja2Templates(directory="gpt_calendar_planner/templates")
app.mount("/static", StaticFiles(directory="gpt_calendar_planner/static"), name="static")

# Инициализируем клиентов
openai_client = OpenAIClient()
caldav_client = CalDAVClient()

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process-command")
async def process_command(command: str = Form(...)):
    try:
        result = openai_client.process_command(command)
        if "error" in result:
            return JSONResponse({"status": "error", "message": result["error"]})
            
        function_name = result["function"]
        arguments = json.loads(result["arguments"])
        
        if function_name == "create_event":
            # Преобразуем dt_start/dt_end в start/end с сохранением временной зоны
            event_args = {
                "title": arguments["title"],
                "start": datetime.fromisoformat(arguments["dt_start"]),  # Сохраняем оригинальную временную зону
                "end": datetime.fromisoformat(arguments["dt_end"]),  # Сохраняем оригинальную временную зону
                "location": arguments.get("location"),
                "notes": arguments.get("notes")
            }
            response = caldav_client.create_event(**event_args)
            return JSONResponse({"status": "success", "message": "Событие создано"})
        elif function_name == "delete_event":
            response = caldav_client.delete_event(**arguments)
            return JSONResponse({"status": "success", "message": "Событие удалено"})
        elif function_name == "get_events":
            # Преобразуем строковые даты в datetime объекты
            events_args = {
                "start_date": datetime.fromisoformat(arguments["start_date"]),  # Сохраняем оригинальную временную зону
                "end_date": datetime.fromisoformat(arguments["end_date"])  # Сохраняем оригинальную временную зону
            }
            events = caldav_client.get_events(**events_args)
            return JSONResponse({"status": "success", "events": events})
            
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})

@app.get("/test-events")
async def test_events():
    try:
        # Получаем события на ближайшие 24 часа
        now = datetime.now(ZoneInfo("UTC"))
        end = now + timedelta(days=1)
        
        events = caldav_client.get_events(now, end)
        return JSONResponse({
            "status": "success",
            "message": f"Found {len(events)} events",
            "events": events
        })
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }) 