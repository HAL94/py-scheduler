from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: str = "6379"
    
settings = AppSettings()
