import sqlite3
from _operator import and_
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, session, url_for, flash
from sqlalchemy import func
from sqlalchemy.exc import OperationalError

import celery_worker
import models
from database import init_db, db_session, engine
from models import User

app = Flask(__name__)
app.secret_key = 'your_secret_key'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:example@db:5432/postgres?client_encoding=utf8'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#db = SQLAlchemy(app)
#migrate = Migrate(app, db)

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

@app.route('/')
def home():
    return render_template('home.html')


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
        print("Користувач зареєстрований:", form_data)
        return redirect(url_for('home'))
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        error_text = request.args.get('error')
        return render_template('login.html', error_text=error_text)
    elif request.method == 'POST':
        username = request.form['login']
        password = request.form['password']
        init_db()

        user_data = db_session.query(models.User).filter_by(login=username).first()

        if user_data and user_data.password == password:
            session['user_id'] = user_data.id
            session['username'] = user_data.login
            return redirect('/profile')
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

@app.route('/items', methods=['GET', 'POST'])
@login_required
def items():
    if request.method == 'GET':
        init_db()
        items_list = db_session.query(models.Item, models.Contract). \
            outerjoin(models.Contract,
                      (models.Item.id == models.Contract.item_contract) &
                      (and_(func.current_date() >= models.Contract.start_date,
                            func.current_date() <= models.Contract.end_date))).all()

        render_items = []
        for item in items_list:
            render_items.append(dict(name = item.Item.name, avaiable = True if item.Contract is not None else False,
                                     id = item.Item.id, description = item.Item.description, price_hour= item.Item.price_hour))
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
    item = models.Item.query.get(item_id)
    if item:
        db_session.query(models.Complaint).filter_by(item_id=item_id).delete()
        db_session.delete(item)
        db_session.commit()
        return redirect('/items')
    return 'Item not found', 404

@app.route('/leasers', methods=['GET'])
@login_required
def leasers():
    if request.method == 'GET':
        contracts = db_session.query(models.Contract).filter_by(leaser_id=session['user_id']).all()
        leasers = []
        for contract in contracts:
            leaser = db_session.query(User).get(contract.taker_id)
            leasers.append({
                'id': contract.taker_id,
                'login': leaser.login,
                'full_name': leaser.full_name,
                'contract_id': contract.id
            })
    return render_template('leasers.html', leasers=leasers)


@app.route('/leasers/<leaser_id>', methods=['GET'])
@login_required
def get_leaser(leaser_id):
    if request.method == 'GET':
        leaser = db_session.query(User).get(leaser_id)
        contracts = db_session.query(models.Contract).filter_by(taker_id=leaser_id).all()
        return render_template('leaser_detail.html', leaser=leaser, contracts=contracts)

@app.route('/takers', methods=['GET'])
@login_required
def takers():
    if request.method == 'GET':
        contracts = db_session.query(models.Contract).filter_by(taker_id=session['user_id']).all()
        takers = []
        for contract in contracts:
            taker = db_session.query(User).get(contract.leaser_id)
            takers.append({
                'id': contract.leaser_id,
                'login': taker.login,
                'full_name': taker.full_name,
                'contract_id': contract.id
            })
    return render_template('takers.html', takers=takers)


@app.route('/takers/<taker_id>', methods=['GET'])
@login_required
def get_taker(taker_id):
    if request.method == 'GET':
        taker = db_session.query(User).get(taker_id)
        contracts = db_session.query(models.Contract).filter_by(leaser_id=taker_id).all()
        return render_template('taker_detail.html', taker=taker, contracts=contracts)


@app.route('/contracts', methods=['GET', 'POST'])
@login_required
def contracts():
    if request.method == 'GET':
        init_db()
        contracts = db_session.query(models.Contract).all()
        my_contracts = db_session.query(models.Contract).filter_by(taker_id=session['user_id']).all()
        contracts_by_my_items = db_session.query(models.Contract).filter_by(leaser_id=session['user_id']).all()
        items = db_session.query(models.Item).all()

        contract_info = []
        for contract in contracts:
            item = db_session.query(models.Item).get(contract.item_contract)
            if item:
                item_name = item.name
            else:
                item_name = "Элемент не найден"
            contract_info.append({
                'id': contract.id,
                'contract_num': contract.contract_num,
                'item_contract': item_name,
                'status': contract.status
            })

        users = db_session.query(models.User).all()
        return render_template('contracts.html', contracts=contract_info, my_contracts=my_contracts,
                               contracts_by_my_items=contracts_by_my_items, items=items, users=users)
    elif request.method == 'POST':
        print(request.form)

        form_data = request.form.to_dict()

        if 'start_date' in form_data:
            form_data['start_date'] = datetime.strptime(form_data['start_date'], '%Y-%m-%d').date()
        if 'end_date' in form_data:
            form_data['end_date'] = datetime.strptime(form_data['end_date'], '%Y-%m-%d').date()

        item = db_session.query(models.Item).filter_by(id=form_data['item_id']).scalar()
        if 'item_id' not in form_data:
            return "Error: Missing item_id in the form data", 400

        leaser = db_session.query(models.User).filter_by(login=form_data['leaser']).scalar()
        taker = db_session.query(models.User).filter_by(login=form_data['taker']).scalar()

        if leaser is None or taker is None:
            return "Error: Арендодатель или арендатор не найден", 400

        contract_num=f"Контракт №{len(db_session.query(models.Contract).all()) + 1}",
        contract = models.Contract(
            text_contract=form_data['text_contract'],
            start_date=form_data['start_date'],
            end_date=form_data['end_date'],
            contract_num=contract_num,
            leaser_id=leaser.id,
            taker_id=taker.id,
            item_contract=item.id,
            status='Активен'
        )

        db_session.add(contract)
        db_session.commit()
        celery_worker.send_email(contract.id)
        return redirect('/contracts')

@app.route('/contracts/<contract_id>', methods=['GET', 'PUT', 'PATCH'])
def contract_detail(contract_id):
    if request.method == 'GET':
        contract = db_session.query(models.Contract).filter_by(id=contract_id).scalar()
        item = db_session.query(models.Item).get(contract.item_contract)
        leaser = db_session.query(models.User).filter_by(id=contract.leaser_id).scalar()
        taker = db_session.query(models.User).filter_by(id=contract.taker_id).scalar()
        print("user_id:", session['user_id'])
        return render_template('contract_detail.html', contract=contract, item=item, leaser=leaser,
                               taker=taker, user_id=session['user_id'])

@app.route('/contracts/<contract_id>/status', methods=['POST'])
def contract_status(contract_id):
    contract = db_session.query(models.Contract).filter_by(id=contract_id).scalar()
    if contract:
        contract.status = request.form['status']
        db_session.commit()
        return redirect('/contracts')
    else:
        return "Error: Контракт не найден", 404

@app.route('/contracts/delete/<int:contract_id>', methods=['POST'])
def delete_contract(contract_id):
    contract = models.Contract.query.get(contract_id)
    db_session.delete(contract)
    db_session.commit()

    return redirect(url_for('contracts'))


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return render_template('search.html')
    elif request.method == 'POST':
        query = request.form['query']
        items = db_session.query(models.Item).filter(models.Item.name.like(f'%{query}%')).all()
        return render_template('search_results.html', items=items, query=query)


@app.route('/complain', methods=['GET', 'POST'])
@login_required
def complain():
    if request.method == 'GET':
        items = db_session.query(models.Item).all()
        users = db_session.query(models.User).all()
        return render_template('complain.html', items=items, users=users)
    elif request.method == 'POST':
        complain_type = request.form['complain_type']
        message = request.form['message']
        user_id = request.form['user_id']
        item_id = request.form['item_id']

        if complain_type == 'user':
            complaint = models.Complaint(
                user_id=user_id,
                message=message,
            )
        else:
            complaint = models.Complaint(
                item_id=item_id,
                message=message,
            )

        db_session.add(complaint)
        db_session.commit()

        return redirect(url_for('complain_success'))
@app.route('/complain/success')
@login_required
def complain_success():
    return render_template('complain_success.html')


conn = sqlite3.connect('database_3_.db')
db_cur = conn.cursor()

try:
    User.__table__.create(engine, checkfirst=True)
    print("Таблица user создана.")
except OperationalError:
    print("Таблица user уже существует.")

@app.route('/add_task', methods=['GET'])
def set_task():
    celery_worker.add.delay(1, 2)
    return "Task Sent"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
