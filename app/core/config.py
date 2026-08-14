from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AlHilo API"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    # BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:4200"]
    BACKEND_CORS_ORIGINS: List[str] = ["*", "http://localhost:4200", "http://192.168.1.194:4200"]

    # Twilio WhatsApp
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_FROM: str = "whatsapp:+14155238886"  # Twilio sandbox default

    # Vercel BLOB
    BLOB_READ_WRITE_TOKEN: str 

    # Biometric Service
    BIOMETRIC_SERVICE_URL: str = "http://localhost:5004"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
