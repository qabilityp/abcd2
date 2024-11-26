from sqlalchemy import Column, Integer, REAL, Date, Text, String
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

    def __init__(self, login=None, password=None, ipn=None, full_name=None, contacts=None, photo=None, passport=None):
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

    def __init__(self, **kwargs):
            self.photo = kwargs.get('photo')
            self.name = kwargs.get('name')
            self.description = kwargs.get('description')
            self.price_hour = kwargs.get('price_hour')
            self.price_day = kwargs.get('price_day')
            self.price_week = kwargs.get('price_week')
            self.price_month = kwargs.get('price_month')

    def __repr__(self):
        return f"<Item(photo={self.photo}, name={self.name}, description={self.description}, price_hour={self.price_hour}, price_day={self.price_day}, price_week={self.price_week}, price_month={self.price_month})>"

class Contract(Base):
    __tablename__ = 'contract'
    id = Column(Integer, primary_key=True, autoincrement=True)
    text_contract = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    contract_num = Column(Text)
    leaser = Column(Integer)
    taker = Column(Integer)
    item_contract = Column(Integer)
    status = Column(String(50))
    leaser_id = Column(Integer, unique=True)
    taker_id = Column(Integer, unique=True)


    def __init__(self, **kwargs):
        self.text_contract = kwargs.get('text_contract')
        self.start_date = parser.parse(kwargs.get('start_date'))
        self.end_date = parser.parse(kwargs.get('end_date'))
        self.contract_num = kwargs.get('contract_num')
        self.leaser = kwargs.get('leaser')
        self.taker = kwargs.get('taker')
        self.item_contract = kwargs.get('item_contract')
        self.status = kwargs.get('status')
        self.leaser_id = kwargs.get('leaser_id')
        self.taker_id = kwargs.get('taker_id')

    def __repr__(self):
        return f"<Contract(text_contract={self.text_contract}, start_date={self.start_date}, end_date={self.end_date}, contract_num={self.contract_num}, status={self.status}, leaser_id={self.leaser_id}, taker_id={self.taker_id})>"

