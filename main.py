from fastapi import FastAPI, Request
from dotenv import load_dotenv
from database.database import DB
from settings import settings
from supabase import create_client, Client

load_dotenv()


db:Client = create_clinet(settings.database_url, settings.databse_key)

app = FastAPI()

@app.middleware("http")
async def add_session(request: Request, call_next):
    request.session =  supabase.auth.get_session()
    response = await call_next(request)



@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
