from fastapi import FastAPI, Request, Depends, Form
# from settings import settings
import supabase
from user.views import userroute
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from models.base import Base
from dependencies.session import engine
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(userroute, prefix="/user")

# Путь к шаблонам
templates = Jinja2Templates(directory="templates")



# Определение пути /enter с методом GET
@app.get("/enter", response_class=HTMLResponse)
def enter_form(request: Request):
    # Возвращает HTML-страницу с формой регистрации
    return templates.TemplateResponse("enter.html", {"request": request, "show_error": False})


