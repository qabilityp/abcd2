from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class db_local(object):
    def __init__(self, file_name):
        self.con = sqlite3.connect(file_name)
        self.con.row_factory = dict_factory
        self.cur = self.con.cursor()
    def __enter__(self):
        return self.cur
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.commit()
        self.con.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return 'GET'
    if request.method == 'POST':
        return 'POST'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        with db_local('database_3.db') as db_cur:
            form_data = request.form
            db_cur.execute('''INSERT INTO user (login, password, ipn, full_name, contracts, photo, passport)
                           VALUES (?, ?, ?, ?, ?, ?, ?)''',
                           (form_data['login'], form_data['password'], form_data['ipn'], form_data['full_name'], form_data['contracts'], form_data['photo'], form_data['passport']))
        return redirect('/login')

@app.route('/logout', methods=['GET', 'POST', 'DELETE'])
def logout():
    if request.method == 'GET':
        return 'GET'
    if request.method == 'POST':
        return 'POST'
    if request.method == 'DELETE':
        return 'DELETE'

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'GET':
        return render_template('user.html')
    if request.method == 'POST':
        return 'POST'

@app.route('/profile/user', methods=['GET', 'PUT', 'DELETE'])
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
def items():
    if request.method == 'GET':
        with db_local('database_3.db') as db_cur:
            db_cur.execute('SELECT * FROM item')
            items = db_cur.fetchall()
        return render_template('item.html', items=items)
    elif request.method == 'POST':
        with db_local('database_3.db') as db_cur:
            form_data = request.form
            db_cur.execute('''INSERT INTO item (photo, name, description, price_hour, price_day, price_week, price_month)
                              VALUES (:photo, :name, :description, :price_hour, :price_day, :price_week, :price_month)''',
                           form_data)
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
def contracts():
    if request.method == 'GET':
        return 'GET'
    elif request.method == 'POST':
        return 'POST'


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
