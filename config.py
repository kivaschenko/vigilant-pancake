import os
from pathlib import Path

from dotenv import load_dotenv
dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path)

def get_postgres_url():
    host = os.environ.get("DB_HOST", "localhost")
    port = 54321 if host == "localhost" else 5432
    password = os.environ.get("DB_PASSWORD", "abc123")
    user = os.environ.get("DB_USER")
    db_name = os.environ.get("DB_NAME")
    uri = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    return uri


def get_api_url():
    host = os.environ.get("API_HOST", "localhost")
    port = 5005 if host == "localhost" else 80
    return f"http://{host}:{port}"
