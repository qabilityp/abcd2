from collections import defaultdict
from datetime import datetime

from sqlalchemy import Column, Integer, REAL, Date, Text, String, DateTime, ForeignKey
from database import Base
from dateutil import parser


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(50), unique=True)
    password = Column(String(50))
    ipn = Column(Integer, unique=True)
    full_name = Column(String(150))
    contacts = Column(String(150))
    photo = Column(String(150))
    passport = Column(String(150))

    def __init__(self, login, password, ipn, full_name, contacts, photo, passport):
        self.login = login
        self.password = password
        self.ipn = ipn
        self.full_name = full_name
        self.contacts = contacts
        self.photo = photo
        self.passport = passport

    def __repr__(self):
        return f"<User(id={self.id}, login={self.login}, full_name={self.full_name}, ipn={self.ipn})>"

class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True, autoincrement=True)
    photo = Column(String(150))
    name = Column(String(50), unique=True)
    description = Column(String(250))
    price_hour = Column(REAL)
    price_day = Column(REAL)
    price_week = Column(REAL)
    price_month = Column(REAL)
    owner_id = Column(Integer)

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.photo = kwargs.get('photo')
        self.name = kwargs.get('name')
        self.description = kwargs.get('description')
        self.price_hour = kwargs.get('price_hour')
        self.price_day = kwargs.get('price_day')
        self.price_week = kwargs.get('price_week')
        self.price_month = kwargs.get('price_month')

    def __repr__(self):
        return (f"<Item(id={self.id} photo={self.photo}, name={self.name}, description={self.description}, price_hour={self.price_hour},"
                f" price_day={self.price_day}, price_week={self.price_week}, price_month={self.price_month})>")

class Contract(Base):
    __tablename__ = 'contract_new'
    id = Column(Integer, primary_key=True, autoincrement=True)
    text_contract = Column(Text, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    contract_num = Column(String(20), unique=True, nullable=False)
    leaser_id = Column(Integer, ForeignKey('user.id'))
    taker_id = Column(Integer, ForeignKey('user.id'))
    item_contract = Column(Integer, ForeignKey('item.id'))
    status = Column(String(50), nullable=False)

    def __init__(self, text_contract, start_date, end_date, contract_num, leaser_id, taker_id, item_contract, status):
        self.text_contract = text_contract
        self.start_date = start_date
        self.end_date = end_date
        self.contract_num = contract_num
        self.leaser_id = leaser_id
        self.taker_id = taker_id
        self.item_contract = item_contract
        self.status = status

    def __repr__(self):
        return (f"<Contract(text_contract={self.text_contract}, start_date={self.start_date}, end_date={self.end_date}, "
                f"contract_num={self.contract_num}, status={self.status}, leaser_id={self.leaser_id}, taker_id={self.taker_id})>")

class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(Integer, primary_key=True, autoincrement=True)
    author = Column(Integer)
    user_feedback = Column(Integer)
    text_feedback = Column(String(500))
    grade = Column(Integer)
    contract_feedback = Column(Integer)
    timestamp = Column(DateTime, default=datetime.now().date(), nullable=True)

    def __init__(self, author, user_feedback, text_feedback, grade, contract_feedback):
        self.author = author
        self.user_feedback = user_feedback
        self.text_feedback = text_feedback
        self.grade = grade
        self.contract_feedback = contract_feedback

    def __repr__(self):
        return (
            f"<Feedback(id={self.id}, author={self.author}, user_feedback={self.user_feedback}, "
            f"grade={self.grade})>"
        )


class Complaint(Base):
    __tablename__ = 'complaint'
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('item.id'))
    contract_id = Column(Integer, ForeignKey('contract_new.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self, item_id=None, contract_id=None, user_id=None, message=None):
        self.item_id = item_id
        self.contract_id = contract_id
        self.user_id = user_id
        self.message = message

    def __repr__(self):
        return (
            f"<Complaint(id={self.id}, item_id={self.item_id}, contract_id={self.contract_id}, user_id={self.user_id}, message={self.message})>"
        )