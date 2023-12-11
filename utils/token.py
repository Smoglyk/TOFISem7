import secrets
from datetime import datetime
import jwt
from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
templates = Jinja2Templates(directory="templates")

def generate_token(data: dict, expires_delta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(request: Request):
    try:
        token = request.headers.get("Cookie").split("=")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expire = payload.get("exp")
        if expire is None or expire < datetime.utcnow().timestamp():
            return
    except Exception as err:
        return

    request.scope["email"] = payload.get("sub")