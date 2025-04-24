from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # OpenAI settings
    openai_api_key: str
    openai_model: str = "gpt-4-1106-preview"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 1000

    # CalDAV settings
    caldav_url: str
    caldav_username: str
    caldav_password: str

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings() 