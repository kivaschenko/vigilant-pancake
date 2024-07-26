from pydantic_settings import BaseSettings
from typing import Optional, Any


class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_name: str
    db_port: int
    db_host: str
    pgadmin_email: str
    pgadmin_password: str
    redis_host: str
    redis_port: int
    redis_password: str
    jwt_secret: str
    jwt_expires_in: str
    mail_host: str
    mail_port: int
    mail_user: str
    mail_password: str
    app_name: str = "Inventory Management"
    DATABASE_URL: Optional[str] = None
    api_url: str = "http://localhost:8000"

    def model_post_init(self, __context: Any) -> None:
        """Override this method to perform additional initialization after `__init__` and `model_construct`.
        This is useful if you want to do some validation that requires the entire model to be initialized.
        """
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
