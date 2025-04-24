import pytest
from unittest.mock import Mock, patch, PropertyMock
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from gpt_calendar_planner.openai_client import OpenAIClient

@pytest.fixture
def mock_openai():
    with patch('gpt_calendar_planner.openai_client.OpenAI') as mock:
        client = Mock()
        mock.return_value = client
        yield client

def test_process_command_create_event(mock_openai):
    client = OpenAIClient()
    
    # Мокаем ответ от OpenAI
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    
    function_call = Mock()
    type(function_call).name = PropertyMock(return_value="create_event")
    type(function_call).arguments = PropertyMock(
        return_value='{"title": "Test Event", "dt_start": "2024-03-20T10:00:00Z", "dt_end": "2024-03-20T11:00:00Z"}'
    )
    
    mock_response.choices[0].message.function_call = function_call
    mock_openai.chat.completions.create.return_value = mock_response
    
    result = client.process_command("Создай встречу завтра в 10:00")
    
    assert result["function"] == "create_event"
    assert "title" in result["arguments"]
    assert "dt_start" in result["arguments"]
    assert "dt_end" in result["arguments"]

def test_process_command_error(mock_openai):
    client = OpenAIClient()
    
    # Мокаем ответ без function_call
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.function_call = None
    mock_openai.chat.completions.create.return_value = mock_response
    
    result = client.process_command("Непонятная команда")
    
    assert "error" in result

def test_get_advice(mock_openai):
    client = OpenAIClient()
    
    # Мокаем ответ от OpenAI для метода chat.completions.create
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = "Test advice"
    mock_openai.chat.completions.create.return_value = mock_response
    
    events = [{
        'title': 'Test Event',
        'start': datetime.now(ZoneInfo("UTC")),
        'end': datetime.now(ZoneInfo("UTC")) + timedelta(hours=1)
    }]
    
    advice = client.get_advice(events)
    
    assert advice == "Test advice" 