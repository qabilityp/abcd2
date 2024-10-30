from flask import Flask, request

app = Flask(__name__)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return 'GET'
    if request.method == 'POST':
        return 'POST'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return 'GET'
    if request.method == 'POST':
        return 'POST'

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
        return 'GET'
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
        return 'GET '
    elif request.method == 'POST':
        return 'POST'
    elif request.method == 'DELETE':
        return 'DELETE'
    elif request.method == 'PATCH':
        return 'PATCH'

@app.route('/items', methods=['GET', 'POST'])
def items():
    if request.method == 'GET':
        return 'GET'
    elif request.method == 'POST':
        return 'POST'

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


if __name__ == '__main__':
    app.run(debug=True)
