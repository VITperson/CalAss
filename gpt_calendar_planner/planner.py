import typer
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json
from typing import Optional
from .caldav_client import CalDAVClient
from .openai_client import OpenAIClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = typer.Typer()
caldav_client = CalDAVClient()
openai_client = OpenAIClient()

@app.command()
def create(command: str):
    """Создать событие в календаре через естественный язык"""
    try:
        result = openai_client.process_command(command)
        if "error" in result:
            logger.error(f"OpenAI error: {result['error']}")
            typer.echo(f"Ошибка: {result['error']}")
            return

        if result["function"] == "create_event":
            args = json.loads(result["arguments"])
            event_id = caldav_client.create_event(
                title=args["title"],
                start=datetime.fromisoformat(args["dt_start"]).replace(tzinfo=ZoneInfo("UTC")),
                end=datetime.fromisoformat(args["dt_end"]).replace(tzinfo=ZoneInfo("UTC")),
                location=args.get("location"),
                notes=args.get("notes")
            )
            typer.echo(f"Событие создано с ID: {event_id}")
        else:
            typer.echo("Команда не распознана как создание события")
    except Exception as e:
        logger.error(f"Error in create command: {e}")
        typer.echo(f"Произошла ошибка: {str(e)}")

@app.command()
def delete(command: str):
    """Удалить событие из календаря через естественный язык"""
    try:
        result = openai_client.process_command(command)
        if "error" in result:
            logger.error(f"OpenAI error: {result['error']}")
            typer.echo(f"Ошибка: {result['error']}")
            return

        if result["function"] == "delete_event":
            args = json.loads(result["arguments"])
            if caldav_client.delete_event(args["event_id"]):
                typer.echo("Событие успешно удалено")
            else:
                typer.echo("Не удалось удалить событие")
        else:
            typer.echo("Команда не распознана как удаление события")
    except Exception as e:
        logger.error(f"Error in delete command: {e}")
        typer.echo(f"Произошла ошибка: {str(e)}")

@app.command(name="list")
def list_events(command: str):
    """Показать события за период через естественный язык"""
    try:
        result = openai_client.process_command(command)
        if "error" in result:
            logger.error(f"OpenAI error: {result['error']}")
            typer.echo(f"Ошибка: {result['error']}")
            return

        if result["function"] == "get_events":
            args = json.loads(result["arguments"])
            events = caldav_client.get_events(
                start_date=datetime.fromisoformat(args["start_date"]).replace(tzinfo=ZoneInfo("UTC")),
                end_date=datetime.fromisoformat(args["end_date"]).replace(tzinfo=ZoneInfo("UTC"))
            )
            for event in events:
                typer.echo(f"""
                Событие: {event['title']}
                Начало: {event['start']}
                Конец: {event['end']}
                Место: {event['location']}
                Заметки: {event['notes']}
                ---
                """)
        else:
            typer.echo("Команда не распознана как запрос списка событий")
    except Exception as e:
        logger.error(f"Error in list_events command: {e}")
        typer.echo(f"Произошла ошибка: {str(e)}")

@app.command()
def advice():
    """Получить советы по тайм-менеджменту"""
    try:
        # Получаем события на ближайшую неделю
        start_date = datetime.now().replace(tzinfo=ZoneInfo("UTC"))
        end_date = start_date + timedelta(days=7)
        events = caldav_client.get_events(start_date, end_date)
        
        advice = openai_client.get_advice(events)
        typer.echo(advice)
    except Exception as e:
        logger.error(f"Error in advice command: {e}")
        typer.echo(f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    app() 