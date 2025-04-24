import pytest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from unittest.mock import Mock, patch
from gpt_calendar_planner.caldav_client import CalDAVClient

@pytest.fixture
def mock_calendar():
    calendar = Mock()
    calendar.name = "Test Calendar"
    return calendar

@pytest.fixture
def mock_client(mock_calendar):
    with patch('caldav.DAVClient') as mock_dav:
        client = Mock()
        principal = Mock()
        principal.calendars.return_value = [mock_calendar]
        client.principal.return_value = principal
        mock_dav.return_value = client
        yield client

def test_create_event(mock_client, mock_calendar):
    client = CalDAVClient()
    start = datetime.now(ZoneInfo("UTC"))
    end = start + timedelta(hours=1)
    
    event_id = client.create_event(
        title="Test Event",
        start=start,
        end=end,
        location="Test Location",
        notes="Test Notes"
    )
    
    assert event_id is not None
    mock_calendar.save_event.assert_called_once()

def test_delete_event(mock_client, mock_calendar):
    client = CalDAVClient()
    event_id = "test-event-id"
    
    # Мокаем event_by_uid
    mock_event = Mock()
    mock_calendar.event_by_uid.return_value = mock_event
    
    result = client.delete_event(event_id)
    
    assert result is True
    mock_event.delete.assert_called_once()

def test_get_events(mock_client, mock_calendar):
    client = CalDAVClient()
    start = datetime.now(ZoneInfo("UTC"))
    end = start + timedelta(days=1)
    
    # Мокаем date_search
    mock_event = Mock()
    mock_event.icalendar_component = {
        'uid': 'test-uid',
        'summary': 'Test Event',
        'dtstart': Mock(dt=start),
        'dtend': Mock(dt=end),
        'location': 'Test Location',
        'description': 'Test Notes'
    }
    mock_calendar.date_search.return_value = [mock_event]
    
    events = client.get_events(start, end)
    
    assert len(events) == 1
    assert events[0]['title'] == 'Test Event'
    assert events[0]['id'] == 'test-uid' 