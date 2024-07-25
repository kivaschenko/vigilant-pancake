import os
from pathlib import Path
from pydantic_settings import BaseSettings

from dotenv import load_dotenv
dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path)


def get_postgres_uri():
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", 5432)
    password = os.environ.get("DB_PASSWORD")
    user = os.environ.get("DB_USER")
    db_name = os.environ.get("DB_NAME")
    uri = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    return uri


def get_api_url():
    host = os.environ.get("API_HOST", "localhost")
    port = 8000 if host == "localhost" else 80
    return f"http://{host}:{port}"


class Settings(BaseSettings):
    app_name: str = "Inventory Management"
    admin_email: str = os.environ.get("ADMIN_EMAIL")
    testing: bool = False
    db_uri: str = get_postgres_uri()
    api_url: str = get_api_url()
