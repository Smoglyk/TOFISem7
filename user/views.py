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

@userroute.get('/kind/transactions')
def view_kinds_transactions(request: Request):

    return templates.TemplateResponse("kind_transactions.html", {"request": request})

@userroute.get('/kind/process/transaction', dependencies=[Depends(verify_token)])
def view_process_transaction(request: Request, type_trans: str = Query(), db = Depends(get_db)):
    user_email = request.scope["email"]
    if not user_email:
        return templates.TemplateResponse("enter.html", {"request": request})

    if type_trans == "payment":
        return templates.TemplateResponse("make_payment.html", {"request": request, "error_frek": False, "error_balance": False, "success": False})

    if type_trans == "credit":
        return templates.TemplateResponse("make_credit.html", {"request": request, "error_finaly": False, "error_credit": False,
                                                        "error_balance": False,
                                                        "success": False})

    if type_trans == "remittance":
        return templates.TemplateResponse("make_remittance.html", {"request": request})


@userroute.post('/process/payment', dependencies=[Depends(verify_token)])
def view_process_payment(request: Request, payment_name: str = Form(...), receiver_email: str = Form(...), count: str = Form(...),db = Depends(get_db)):
    user_email = request.scope["email"]
    if not user_email:
        return templates.TemplateResponse("enter.html", {"request": request})

    user = db.query(User).filter(User.email == user_email).first()
    account_user = db.query(Account).filter(Account.user_id == user.id).first()
    if account_user.balance < int(count):
        return templates.TemplateResponse("make_payment.html", {"request": request, "error_frek": False, "error_balance": True, "success": False})
    payment = db.query(Payment).filter(Payment.name == payment_name).first()
    receiver = db.query(User).filter(User.email == receiver_email).first()
    if not receiver:
        return templates.TemplateResponse("make_payment.html", {"request": request, "error_frek": True, "error_balance": False, "success": False})
    account_receiver = db.query(Account).filter(Account.user_id == receiver.id).first()
    payment_trans = PaymentTransaction(payment=payment, sender=account_user, receiver=account_receiver, count=int(count), date=func.now())
    db.add(payment_trans)
    db.commit()

    return templates.TemplateResponse("make_payment.html", {"request": request, "error_frek": False, "error_balance": False, "success": True})

@userroute.post('/process/credit', dependencies=[Depends(verify_token)])
def view_process_credit(request: Request, sum_payment: int=Form(...), db=Depends(get_db)):
    user_email = request.scope["email"]
    if not user_email:
        return templates.TemplateResponse("enter.html", {"request": request})

    user = db.query(User).filter(User.email == user_email).first()
    account = db.query(Account).filter(Account.user_id == user.id).first()
    if account.balance < sum_payment:
        return templates.TemplateResponse("make_credit.html", {"request": request, "error_finaly":False, "error_credit": False, "error_balance": True, "success": False})

    credit = db.query(Credit).filter(Credit.borrower_id == account.id).first()
    if not credit:
        return templates.TemplateResponse("make_credit.html", {"request": request, "error_finaly":False, "error_credit": True, "error_balance": False,
                                           "success": False})
    if credit.finaly:
        return tempaltes.TemplateResponse("make_credit.html", {"request": request, "error_finaly":True, "error_credit": True, "error_balance": False,
                                           "success": False})

    credit_trans = CreditTransaction(sum_payment=sum_payment, borrower=account, credit=credit)
    credit.remainder_sum -= sum_payment

    if credit.remainder_sum == 0:
        credit.finaly = True

    db.add(credit_trans)
    db.commit()

    return templates.TemplateResponse("make_credit.html",  {"request": request, "error_finaly":False, "error_credit": False, "error_balance": False,
                                       "success": True})

@userroute.get('/process/remittance', dependencies=[Depends(verify_token)])
def view_process_remittance(request: Request, db=Depends(get_db)):
    user_email = request.scope["email"]
    if not user_email:
        return templates.TemplateResponse("enter.html", {"request": request})


