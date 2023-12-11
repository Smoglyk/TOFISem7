from fastapi import APIRouter, Depends, Request, Response, Form, Query
from pydantic import BaseModel, EmailStr, validator
import supabase
from settings import settings
from dependencies.session import get_db
from services.auth_user import registration_user, verify_user, login_user
from fastapi.templating import Jinja2Templates
from utils.token import verify_token
from models.base import User, Account,Currency, PaymentTransaction, RemittanceTransaction, CreditTransaction
from sqlalchemy.orm import joinedload
import os

userroute = APIRouter()
templates = Jinja2Templates(directory="templates")

@userroute.post('/registration')
def view_registration(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...), db = Depends(get_db)):
    try:
        registration_user(username, email, password, db)
    except Exception as e:
        return templates.TemplateResponse("enter.html", {"request": request, "show_error": True})

    return templates.TemplateResponse("verify.html", {"request": request,  "show_error": False})

@userroute.post('/verify')
def view_verify(request: Request, response: Response, email: str = Form(...), code: str = Form(...), db = Depends(get_db)):
    access_token = verify_user(email, code, db)
    if access_token:
        res = templates.TemplateResponse("preview.html", {"request": request})
        res.headers["Set-Cookie"] = f"token={access_token}; Max-Age=3600; Path=/"
        return res

    return templates.TemplateResponse("verify.html", {"request": request,  "show_error": True})

@userroute.post('/login')
def view_log_in(request: Request, email: str = Form(...), password: str = Form(...), db = Depends(get_db)):
    login_user(email, password, db)

    return templates.TemplateResponse("verify.html", {"request": request, "show_error": False})

@userroute.get('/account', dependencies=[Depends(verify_token)])
def view_account(request: Request, db = Depends(get_db)):
    user_email = request.scope.get("email")
    if not user_email:
        return templates.TemplateResponse("enter.html", {"request": request})
    user = db.query(User).filter(User.email == user_email).first()
    account = db.query(Account).options(joinedload(Account.currency), joinedload(Account.user)).filter(Account.user_id == user.id).first()

    return templates.TemplateResponse("account.html", {"request": request, "user_email": account.user.email, "user_name": account.user.name,
                                                       "account_balance": account.balance, "currency": account.currency.name, "show_error": False})


@userroute.get('/list/transactions', dependencies=[Depends(verify_token)])
def view_list_transactions(request: Request, db = Depends(get_db)):
    user_email = request.scope.get("email")
    if not user_email:
        return templates.TemplateResponse("enter.html", {"request": request})

    return templates.TemplateResponse("list_transaction.html", {"request": request})



@userroute.get('/list/item', dependencies=[Depends(verify_token)])
def view_take_transactions(request: Request, type_item: str = Query(), db = Depends(get_db)):
    user_email = request.scope["email"]
    if not user_email:
        return templates.TemplateResponse("enter.html", {"request": request})

    user = db.query(User).filter(User.email == user_email).first()
    account = db.query(Account).options(joinedload(Account.currency), joinedload(Account.user)).filter(
        Account.user_id == user.id).first()
    if type_item == "payment":
        transactions = db.query(PaymentTransaction).options(joinedload(PaymentTransaction.receiver), joinedload(PaymentTransaction.sender),
                                                            joinedload(PaymentTransaction.payment)).filter(PaymentTransaction.sender_id == account.user_id).all()
        return  templates.TemplateResponse("payment_transactions.html", {"request": request, "transactions": transactions})

    if type_item == "remittance":
        transactions = db.query(RemittanceTransaction).options(joinedload(RemittanceTransaction.receiver),
                                                            joinedload(RemittanceTransaction.sender),
                                                            joinedload(RemittanceTransaction.currency)).filter(
                                                            RemittanceTransaction.sender_id == account.user_id).all()
        return templates.TemplateResponse("remittance_transactions.html", {"request": request, "transactions": transactions})

    if type_item == "credit":
        transactions = db.query(CreditTransaction).options(joinedload(CreditTransaction.borrower),
                                                        joinedload(CreditTransaction.credit)).filter(
                                                        CreditTransaction.borrower_id == account.user_id).all()
        return templates.TemplateResponse("credit_transactions.html", {"request": request, "transactions": transactions})
