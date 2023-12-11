from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    database_url: str = os.environ.get("SUPABASE_URL")
    databse_key: str = os.environ.get("SUPABASE_KEY")

settings = Settings()