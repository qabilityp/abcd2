from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from functools import wraps
from dateutil import parser


from select import select
from sqlalchemy import create_engine

import models
from database import init_db, db_session
from models import User, Item

app = Flask(__name__)
app.secret_key = 'your_secret_key'

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

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'GET':
        db = Dbhandle('database_3.db')
        conditions = {'id': session['user_id']}
        full_name = db.select('user', conditions)
        print(session)
        if full_name is None:
            return "Користувач не знайдений"
        return render_template('user.html', full_name=full_name)
    if request.method == 'POST':
        return 'POST'

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
        items_query = db_session.query(models.Item)
        items = items_query.all()
        return render_template('item.html', items=items)
    elif request.method == 'POST':
        form_data = request.form
        item = models.Item(**form_data)
        db_session.add(item)
        db_session.commit()
    return redirect('/items')


@app.route('/items/<item_id>', methods=['GET', 'DELETE'])
def item(item_id):
    if request.method == 'GET':
        return f'GET {item_id}'
    elif request.method == 'DELETE':
        return f'DELETE {item_id}'

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
        contracts_query = db_session.query(models.Contract)
        contracts = contracts_query.all()
        return render_template('contracts.html', contracts=contracts)
    elif request.method == 'POST':

        print(request.form)

        form_data = request.form
        contract = models.Contract(**form_data)
        db_session.add(contract)
        db_session.commit()
        return redirect('/contracts')

@app.route('/contracts/<contract_id>', methods=['GET', 'PUT', 'PATCH'])
def get_contract(contract_id):
    if request.method == 'GET':
        return f'GET {contract_id}'
    elif request.method in ['PUT', 'PATCH']:
        return f'UPDATE {contract_id}'


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

conn = sqlite3.connect('database_3.db')
db_cur = conn.cursor()

db_cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="user"')
result = db_cur.fetchone()
if result is None:
    print("Таблица user не существует")
else:
    print("Таблица user существует")


if __name__ == '__main__':
    app.run(debug=True)
