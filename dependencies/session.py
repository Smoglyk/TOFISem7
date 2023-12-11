from fastapi import Depends
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.security import OAuth2PasswordBearer

DATABASE_URL =  "postgresql://fakfmvqwierceq:4ad6817b8ee7404866e423af9e0b6ddc13b46695be8a63bfb232bc9a28fd3bf6@ec2-52-215-68-14.eu-west-1.compute.amazonaws.com:5432/d8k4ktc5c2tv9p"
#os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



