"""
Конфигурация приложения. Все настройки заданы здесь, .env не используется.
"""

class Settings:
    """Application configuration settings"""

    # BotHub API
    bothub_api_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImRhZDUzZDY5LTc5YTAtNGIzZS1hZWQ4LThmNWZkMTU2OGNiOSIsImlzRGV2ZWxvcGVyIjp0cnVlLCJpYXQiOjE3NzE2OTg1NDUsImV4cCI6MjA4NzI3NDU0NSwianRpIjoiSGhVMUE0bGdZV1lPLVZ0byJ9.dbErjm2BE9SYXbEnVTSl4Y_WEaMoSHSoilF7H9DQsks"
    bothub_base_url: str = "https://bothub.chat/api/v2/openai/v1"

    # Database (SQLite)
    database_url: str = "sqlite:///./voice_assistant.db"

    # Limits
    free_requests_limit: int = 1_000_000
    paid_access_price: int = 1000

    # Audio limits
    max_audio_duration_seconds: int = 60
    max_audio_size_mb: int = 10

settings = Settings()
