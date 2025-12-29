from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
from pydantic import field_validator

class Settings(BaseSettings):
    # _instance: Optional["Settings"] = None

    DATABASE_URL: str
    DEBUG: bool
    ALLOWED_ORIGINS: str
    OPENAI_API_KEY: str
    GOOGLE_API_KEY: str
    PPLX_API_KEY: str
    API_PREFIX: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # @staticmethod
    # def get_instance() -> "Settings":
    #     if not Settings._instance:
    #         Settings._instance = Settings()
    #     return Settings._instance

    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def parse_origins(cls, value: str) -> List[str]:
        return value.split(",") if value else []
    

instance = None

def get_settings() -> Settings:
    global instance
    if not instance:
        instance = Settings()
    return instance