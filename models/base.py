from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    code = Column(String)
    account = relationship('Account', back_populates='user', uselist=False)

class Role(Base):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    account = relationship('Account', back_populates='role', uselist=False)


class Account(Base):
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True)
    balance = Column(Integer)
    currency_id = Column(Integer, ForeignKey('currency.id'))
    currency = relationship("Currency", back_populates='account')
    remittance_transaction_sender = relationship("RemittanceTransaction", back_populates='sender',
                                          foreign_keys='RemittanceTransaction.sender_id')
    remittance_transaction_receiver = relationship("RemittanceTransaction", back_populates='receiver',
                                                 foreign_keys='RemittanceTransaction.receiver_id')
    payment_transaction_sender = relationship("PaymentTransaction", back_populates='sender',
                                       foreign_keys='PaymentTransaction.sender_id')
    payment_transaction_receiver = relationship("PaymentTransaction", back_populates='receiver',
                                              foreign_keys='PaymentTransaction.receiver_id')
    credit_transaction = relationship("CreditTransaction", back_populates='borrower')
    credit = relationship('Credit', back_populates='borrower')
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='account')
    role_id = Column(Integer, ForeignKey('role.id'))
    role = relationship('Role', back_populates='account')

    __table_args__ = (
        CheckConstraint('balance > 0'),
    )

class Currency(Base):
    __tablename__ = 'currency'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)
    date = Column(DateTime)
    remittance_transaction = relationship('RemittanceTransaction', back_populates='currency', uselist=False)
    account = relationship('Account', back_populates='currency', uselist=False)
    credit = relationship('Credit', back_populates='currency', uselist=False)

class RemittanceTransaction(Base):
    __tablename__ = 'remittance_transaction'
    id = Column(Integer, primary_key=True)
    currency_id = Column(Integer, ForeignKey('currency.id'))
    currency = relationship('Currency', back_populates='remittance_transaction')
    sender_id = Column(Integer, ForeignKey('account.id'))
    sender = relationship('Account', back_populates='remittance_transaction_sender', foreign_keys=[sender_id])
    receiver_id = Column(Integer, ForeignKey('account.id'))
    receiver = relationship('Account', back_populates='remittance_transaction_receiver', foreign_keys=[receiver_id])
    count = Column(Integer)
    date = Column(DateTime(timezone=True), server_default=func.now())
    comission = Column(Integer)
    success = Column(Boolean)

    __table_args__ = (
        CheckConstraint('count > 0'),
        CheckConstraint('comission >= 0'),
    )

class PaymentTransaction(Base):
    __tablename__ = 'payment_transaction'
    id = Column(Integer, primary_key=True)
    payment_id = Column(Integer, ForeignKey('payment.id'))
    payment = relationship('Payment', back_populates='payment_transaction')
    sender_id = Column(Integer, ForeignKey('account.id'))
    sender = relationship('Account', back_populates='payment_transaction_sender', foreign_keys=[sender_id])
    receiver_id = Column(Integer, ForeignKey('account.id'))
    receiver = relationship('Account', back_populates='payment_transaction_receiver', foreign_keys=[receiver_id])
    count = Column(Integer, nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint('count > 0'),
    )

class Payment(Base):
    __tablename__ = 'payment'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    payment_transaction = relationship("PaymentTransaction", back_populates='payment')

class Credit(Base):
    __tablename__ = 'credit'
    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    procent = Column(Integer)
    currency_id = Column(Integer, ForeignKey('currency.id'))
    currency = relationship('Currency', back_populates='credit')
    data_start = Column(DateTime(timezone=True), server_default=func.now())
    data_end = Column(DateTime)
    borrower_id = Column(Integer, ForeignKey('account.id'))
    borrower = relationship('Account', back_populates='credit')
    finaly = Column(Boolean)
    total_sum = Column(Integer, nullable=False)
    remainder_sum = Column(Integer, nullable=False)
    credit_transaction = relationship('CreditTransaction', back_populates='credit')

    __table_args__ = (
        CheckConstraint('total_sum > 0'),
        CheckConstraint('remainder_sum > 0'),
    )

class CreditTransaction(Base):
    __tablename__ = 'credit_transaction'
    id = Column(Integer, primary_key=True)
    sum_payment = Column(Integer)
    date = Column(DateTime)
    borrower_id = Column(Integer, ForeignKey('account.id'))
    borrower = relationship('Account', back_populates='credit_transaction')
    credit_id = Column(Integer, ForeignKey('credit.id'))
    credit = relationship('Credit', back_populates='credit_transaction')
