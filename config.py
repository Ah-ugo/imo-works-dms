import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from functools import lru_cache

# Load environment variables from .env
load_dotenv()

print(f"MONGO_URL from env: {os.getenv('MONGO_URL')}")  # Test
print(f"CLOUD_NAME from env: {os.getenv('CLOUD_NAME')}")  # Test
print(f"SECRET_KEY from env: {os.getenv('SECRET_KEY')}")  # Test

class Settings(BaseSettings):
    # MongoDB settings
    MONGO_URL: str

    # JWT settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    # Cloudinary settings
    CLOUD_NAME: str
    API_KEY: str
    API_SECRET: str

    # Gmail settings
    GMAIL_PASS: str

    GMAIL_USER: str

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
