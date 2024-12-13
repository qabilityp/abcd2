from _operator import and_
from datetime import datetime

from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
from functools import wraps
from dateutil import parser
from sqlalchemy.exc import OperationalError
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from select import select
from sqlalchemy import create_engine, func

import models
from database import init_db, db_session, engine
from models import User, Item

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database_3_.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class Dblocal(object):
    def __init__(self, file_name):
        self.file_name = file_name
        self.con = sqlite3.connect(file_name)
        self.con.row_factory = dict_factory
        self.cur = self.con.cursor()

    def __enter__(self):
        return self.con.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.commit()
        self.con.close()


class Dbhandle:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def select(self, table, columns='*', where=None, single=False):
            query = f"SELECT {columns} FROM {table}"

            if where:
                query += f" WHERE " + " AND ".join([f"{key} = ?" for key in where])
                self.cursor.execute(query, tuple(where.values()))
            else:
                self.cursor.execute(query)

            return self.cursor.fetchone() if single else self.cursor.fetchall()

    def insert(self, table, data):
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?'] * len(data))
            query = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
            self.cursor.execute(query, tuple(data.values()))

@app.route('/register', methods=['GET', 'POST'])
def register(form_data=None):
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        form_data = request.form.to_dict()
        init_db()
        existing_user = db_session.query(models.User).filter_by(ipn=form_data['ipn']).first()
        if existing_user:
            return "Користувач із таким IPN вже існує."
        user = models.User(**form_data)
        db_session.add(user)
        db_session.commit()
        print(form_data)
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['login']
        password = request.form['password']
        init_db()

        query = models.User.query.filter_by(login=username)
        result = db_session.execute(query)
        user_data = result.scalars().first()

        if user_data and user_data.password == password:
            session['user_id'] = user_data.id
            session['username'] = user_data.login
            return redirect('/dashboard')
        else:
            return "Невірні дані, спробуйте ще раз"

@app.route('/dashboard')
@login_required
def dashboard():
    if 'user_id' in session:
        return f"Вітаю, {session['username']}! Ви увійшли в систему."
    else:
        return redirect('/login')

@app.route('/logout', methods=['GET', 'POST', 'DELETE'])
@login_required
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect('/login')

@app.route('/profile', methods=['GET', 'PUT', 'DELETE'])
@login_required
def profile():
    if request.method == 'GET':
        user_id = session['user_id']
        user = db_session.query(User).get(user_id)
        print(user)
        return render_template('profile.html', user=user)
    elif request.method == 'PUT':
        data = request.form
        user_id = session['user_id']
        user = db_session.query(User).get(user_id)
        user.login = data.get('login', user.login)
        user.password = data.get('password', user.password)
        user.ipn = data.get('ipn', user.ipn)
        user.full_name = data.get('full_name', user.full_name)
        user.contacts = data.get('contacts', user.contacts)
        user.photo = data.get('photo', user.photo)
        user.passport = data.get('passport', user.passport)
        db_session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect('/profile')
    elif request.method == 'DELETE':
        user_id = session['user_id']
        user = db_session.query(User).get(user_id)
        db_session.delete(user)
        db_session.commit()
        session.clear()
        flash('Your account has been deleted.', 'info')
        return redirect('/login')

@app.route('/profile/user', methods=['GET', 'PUT', 'DELETE'])
@login_required
def profile_user():
    if request.method == 'GET':
        return 'GET'
    elif request.method == 'PUT':
        return 'PUT'
    elif request.method == 'DELETE':
        return 'DELETE'

@app.route('/profile/me', methods=['GET', 'PUT', 'DELETE'])
def profile_me():
    if request.method == 'GET':
        return 'GET'
    elif request.method == 'PUT':
        return 'PUT'
    elif request.method == 'DELETE':
        return 'DELETE'

@app.route('/profile/favorites', methods=['GET', 'POST', 'DELETE', 'PATCH'])
def favorites():
    if request.method == 'GET':
        return 'GET'
    elif request.method == 'POST':
        return 'POST'
    elif request.method == 'DELETE':
        return 'DELETE'
    elif request.method == 'PATCH':
        return 'PATCH'

@app.route('/items', methods=['GET', 'POST'])
@login_required
def items():
    if request.method == 'GET':
        init_db()
        items_query = db_session.query(models.Item, models.Contract).\
            outerjoin(models.Contract,
            (models.Item.id == models.Contract.item_contract) &
                      (and_(func.current_date() >= models.Contract.start_date,
                       func.current_date() <= models.Contract.end_date)))
        print(str(items_query.statement))
        items_list = items_query.all()

        render_items = []
        for item in items_list:
            render_items.append(dict(name = item.Item.name, avaiable = True if item.Contract is not None else False,
                                     id = item.Item.id, description = item.Item.description))
        return render_template('item.html', items=render_items)


    elif request.method == 'POST':
        form_data = request.form
        item = models.Item(**form_data)
        db_session.add(item)
        db_session.commit()
    return redirect('/items')


@app.route('/items/<item_id>', methods=['GET'])
@login_required
def item(item_id):
    if request.method == 'GET':
        item = db_session.query(models.Item).filter_by(id=item_id).scalar()
        return render_template('item_detail.html', item_id=item_id, photo=item.photo, name=item.name,
                               description=item.description, price_hour=item.price_hour, price_week=item.price_week,
                               price_month=item.price_month, owner_id=item.owner_id, current_user=session['user_id']
)

@app.route('/items/<item_id>/delete', methods=['POST'])
@login_required
def delete_item(item_id):
    item = db_session.query(models.Item).filter_by(id=item_id).scalar()
    if item:
        db_session.delete(item)
        db_session.commit()
        return redirect('/items')
    return 'Item not found', 404

@app.route('/leasers', methods=['GET'])
def leasers():
    if request.method == 'GET':
        return 'GET'

@app.route('/leasers/<leaser_id>', methods=['GET'])
def get_leaser(leaser_id):
    if request.method == 'GET':
        return f'GET {leaser_id}'


@app.route('/contracts', methods=['GET', 'POST'])
@login_required
def contracts():
    if request.method == 'GET':
        init_db()
        my_contracts = db_session.query(models.Contract).filter_by(taker_id=session['user_id']).all()
        contracts_by_my_items = db_session.query(models.Contract).filter_by(leaser_id=session['user_id']).all()
        return render_template('contracts.html', contracts=contracts, my_contracts=my_contracts, contracts_by_my_items=contracts_by_my_items)
    elif request.method == 'POST':

        print(request.form)

        form_data = request.form.to_dict()

        if 'start_date' in form_data:
            form_data['start_date'] = datetime.strptime(form_data['start_date'], '%Y-%m-%d').date()
        if 'end_date' in form_data:
            form_data['end_date'] = datetime.strptime(form_data['end_date'], '%Y-%m-%d').date()

        contract = models.Contract(**form_data)
        taker_id = session['user_id']
        item = db_session.query(models.Item).filter_by(id=form_data['item_id']).scalar()
        if 'item_id' not in form_data:
            return "Error: Missing item_id in the form data", 400
        contract.taker_id = taker_id
        contract.leaser_id = item.owner_id
        contract.item_contract = item.id
        db_session.add(contract)
        db_session.commit()
        return redirect('/contracts')

@app.route('/contracts/<contract_id>', methods=['GET', 'PUT', 'PATCH'])
def contract_detail(contract_id):
    if request.method == 'GET':
        contract = db_session.query(models.Contract).filter_by(id=contract_id).scalar()
        return render_template('contract_detail.html', contract=contract)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return 'GET'
    elif request.method == 'POST':
        return 'POST'


@app.route('/complain', methods=['POST'])
def complain():
    if request.method == 'POST':
        return 'POST'

@app.route('/compare', methods=['GET', 'PUT', 'PATCH'])
def compare():
    if request.method == 'GET':
        return 'GET'
    elif request.method in ['PUT', 'PATCH']:
        return 'UPDATE'

conn = sqlite3.connect('database_3_.db')
db_cur = conn.cursor()

try:
    User.__table__.create(engine)
    print("Таблица user создана.")
except OperationalError:
    print("Таблица user уже существует.")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
