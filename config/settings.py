from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # BotHub API
    bothub_api_key: str
    bothub_base_url: str = "https://bothub.chat/api/v2/openai/v1"
    
    # Database (SQLite)
    database_url: str = "sqlite:///./voice_assistant.db"
    
    # Limits
    free_requests_limit: int = 1_000_000
    paid_access_price: int = 1000
    
    # CORS
    allowed_origins: str = "https://localhost:5173,https://localhost:3000,http://localhost:5173,http://localhost:3000,https://localhost:3002,http://localhost:3002"
    
    # Audio limits
    max_audio_duration_seconds: int = 60
    max_audio_size_mb: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def allowed_origins_list(self):
        """Преобразуем строку CORS origins в список"""
        return [origin.strip() for origin in self.allowed_origins.split(',')]


settings = Settings()
