
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import random

from utils.smpt import send_email
from utils.password import hash_password, verify_password
from models.base import User, Account, Currency, Role
from utils.token import generate_token
from datetime import datetime, timedelta


def registration_user(username, email, password, db: Session):
    existing_user = db.query(User).filter(User.email == email).first()
    if not existing_user:
        hashed_password = hash_password(password)
        random_numbers = ''.join(str(random.randint(0, 9)) for _ in range(4))
        user = User(name=username, email=email, password=hashed_password, code=random_numbers)
        currency = db.query(Currency).filter(Currency.name == "ruble").first()
        role = db.query(Role).filter(Role.name == "user").first()
        account = Account(balance=10000, currency=currency, user=user, role=role)
        db.add(user)
        db.add(account)
        db.commit()
        db.refresh(user)
    else:
        raise Exception

    send_email(email, "Confirm account pls",random_numbers)


def login_user(email, password, db: Session):
    user = db.query(User).filter(User.email == email).first()
    hashed_pas = hash_password
    try:
        if user and verify_password(password,user.password):
            random_numbers = ''.join(str(random.randint(0, 9)) for _ in range(4))
            user.code = random_numbers
            send_email(email, "Confirm account pls", random_numbers)
            db.commit()

        else:
            return Exception
    except Exception as e:
        print(e)

def verify_user(email, code, db: Session):
    try:
        user = db.query(User).filter(User.email == email).first()
    except e:
        print(e)
    if user and user.code == code:
        access_token_expires = timedelta(minutes= 30)
        user.token = generate_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        db.commit()
        db.refresh(user)

        return user.token

    return None