from fastapi import APIRouter, Depends, Request, Response, Form, Query
from pydantic import BaseModel, EmailStr, validator
import supabase
#from settings import settings
from dependencies.session import get_db
from services.auth_user import registration_user, verify_user, login_user
from fastapi.templating import Jinja2Templates
from utils.token import verify_token
from models.base import User, Account,Currency, PaymentTransaction, RemittanceTransaction, CreditTransaction, Payment, Credit
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import func
from services.credit import calculate_annuity_payment
from datetime import datetime, timedelta
import os

creditroute = APIRouter()
templates = Jinja2Templates(directory="templates")

@creditroute.get('/status', dependencies=[Depends(verify_token)])
def view_credit_status(request: Request,  db= Depends(get_db)):
    user_email = request.scope.get("email")
    if not user_email:
        return templates.TemplateResponse("enter.html", {"request": request})

    user = db.query(User).filter(User.email == user_email).first()
    account = db.query(Account).filter(Account.user_id == user.id).first()
    credit = account.credit
    return templates.TemplateResponse("current_credit.html", {"request": request, "currency": credit.currency.name,
                                                              "data_start": credit.data_start.strftime("%d-%m-%Y"), "data_end": credit.data_end.strftime("%d-%m-%Y"),
                                                              "finaly": credit.finaly, "amount_loan": credit.total_sum,
                                                              "remainder_sum": credit.remainder_sum, "procent": credit.procent})

@creditroute.get('')
def view_kinds_transactions(request: Request):

    return templates.TemplateResponse("apply_loan.html", {"request": request, "user_has_not_credit": True})

@creditroute.post('/apply', dependencies=[Depends(verify_token)])
def view_make_credit(request: Request, currency: str = Form(...),
    loan_amount: int = Form(...),
    loan_term: int = Form(...),
    monthly_payment: int = Form(...),
    loan_purpose: str = Form(...),
    email: str = Form(...), db= Depends(get_db)):
    user_email = request.scope.get("email")
    if not user_email:
        return templates.TemplateResponse("enter.html", {"request": request})

    interest_rate = int(os.getenv("INTEREST_RATE"))
    annuity_payment = calculate_annuity_payment(loan_amount, interest_rate, loan_term)

    current_date = datetime.now()
    one_year_later = current_date + timedelta(days=loan_term)

    inst_currency = db.query(Currency).filter(Currency.name == currency).first()
    user = db.query(User).filter(User.email == user_email).first()
    account = db.query(Account).filter(Account.user_id == user.id).first()
    if account.credit and not account.credit.finaly:
        return templates.TemplateResponse("apply_loan.html", {"request":request, "user_has_not_credit": False})

    cr = Credit(procent=interest_rate, currency=inst_currency, data_end=one_year_later, borrower=account, total_sum=loan_amount,
                    remainder_sum=loan_amount, mounth_payment=int(annuity_payment))
    db.add(cr)
    db.commit()

    return templates.TemplateResponse("success_apply_loan.html", {"request":request})
