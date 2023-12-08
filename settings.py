from pydantic import BaseSettings
from database.database import DB


class Settings(BaseSettings):
    database_url: str = os.environ.get("SUPABASE_URL")
    databse_key: str = os.environ.get("SUPABASE_KEY")

settings = Settings()