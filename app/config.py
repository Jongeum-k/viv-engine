import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env: str = "dev"
    debug: bool = False
    log_level: str = "info"
    database_url: str

    class Config:
        env_file = {
            "prod": ".env.prod",
            "demo": ".env.demo"
        }.get(os.getenv("ENV", "dev"), ".env")
        extra = "ignore"

    @property
    def db_url(self) -> str:
        return self.database_url

settings = Settings()