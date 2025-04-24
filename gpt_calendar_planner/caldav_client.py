import caldav
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Dict, Any, Optional
from .config import settings
from icalendar import Calendar

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

USER_TIMEZONE = ZoneInfo("Asia/Dubai")  # UTC+4

class CalDAVClient:
    def __init__(self):
        try:
            logger.info("Initializing CalDAV client...")
            self.client = caldav.DAVClient(
                url=settings.caldav_url,
                username=settings.caldav_username,
                password=settings.caldav_password,
                ssl_verify_cert=True
            )
            
            logger.info("Successfully connected to CalDAV server")
            principal = self.client.principal()
            calendars = principal.calendars()
            logger.info(f"Found {len(calendars)} calendars")
            
            if not calendars:
                raise Exception("No calendars found")
            
            self.calendar = calendars[0]
            logger.info(f"Using calendar: {self.calendar}")
            
            # Проверяем права доступа, создавая тестовое событие
            try:
                test_event = self.calendar.save_event(
"""BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
BEGIN:VEVENT
SUMMARY:Test Event
DTSTART:20240101T000000Z
DTEND:20240101T010000Z
END:VEVENT
END:VCALENDAR""")
                test_event.delete()
                logger.info("Successfully verified write access to calendar")
            except Exception as e:
                raise Exception(f"Failed to verify write access: {e}")
                
        except Exception as e:
            logger.error(f"Failed to initialize CalDAV client: {e}")
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
            
            # Форматируем даты в формате iCalendar с учетом временной зоны
            start_str = start.strftime("%Y%m%dT%H%M%S")
            end_str = end.strftime("%Y%m%dT%H%M%S")
            
            event_data = f"""BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
BEGIN:VEVENT
SUMMARY:{title}
DTSTART;TZID={USER_TIMEZONE}:{start_str}
DTEND;TZID={USER_TIMEZONE}:{end_str}
DTSTAMP:{datetime.now(USER_TIMEZONE).strftime("%Y%m%dT%H%M%S")}Z"""

            if location:
                event_data += f"\nLOCATION:{location}"
            if notes:
                event_data += f"\nDESCRIPTION:{notes}"
                
            event_data += "\nEND:VEVENT\nEND:VCALENDAR"

            logger.info(f"Generated iCalendar data:\n{event_data}")
            
            event = self.calendar.save_event(event_data)
            logger.info(f"Successfully created event: {event.url}")
            return str(event.url)
            
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
            
            events = self.calendar.search(start=start_date, end=end_date, event=True, expand=True)
            
            result = []
            for event in events:
                try:
                    cal = Calendar.from_ical(event.data)
                    for component in cal.walk('VEVENT'):
                        event_data = {
                            'title': str(component.get('summary', 'Без названия')),
                            'start': component.get('dtstart').dt.astimezone(USER_TIMEZONE).isoformat(),
                            'end': component.get('dtend').dt.astimezone(USER_TIMEZONE).isoformat(),
                            'location': str(component.get('location', '')),
                            'notes': str(component.get('description', ''))
                        }
                        result.append(event_data)
                except Exception as e:
                    logger.error(f"Failed to parse event {event.url}: {e}")
                    continue
                
            return result
            
        except Exception as e:
            logger.error(f"Failed to get events: {e}")
            raise 