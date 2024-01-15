from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from datetime import datetime, timedelta
import jwt
import os

app = Flask(__name__, template_folder=os.curdir)
cors = CORS(app)

app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a secure secret key
socketio = SocketIO(app, cors_allowed_origins="*")

# Mock user data for JWT authentication
users = {
    'your_username': {'username': 'your_username', 'password': 'your_password'}
}

# JWT configuration
def authenticate(username, password):
    user = users.get(username, None)
    if user and user['password'] == password:
        return user

def generate_token(user_id):
    payload = {
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

# Routes

@app.route('/smartband')
def smartband():
    return render_template('smartband.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# JWT configuration
def authenticate(username, password):
    user = users.get(username, None)
    if user and user['password'] == password:
        return user

def generate_token(user_id):
    payload = {
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

@app.route('/authenticate', methods=['POST'])
def handle_authentication():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = authenticate(username, password)

    if user:
        user_id = username
        token = generate_token(user_id)
        return jsonify({'token': token})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@socketio.on('connect', namespace='/dashboard')
def handle_connect():
    token = request.args.get('token')
    try:
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded['sub']
        print(f'{users[user_id]["username"]} connected to /dashboard')
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False

@socketio.on('smartband_data', namespace='/dashboard')
def handle_smartband_data(data):
    token = request.args.get('token')
    try:
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded['sub']
        print(f'Received data from {users[user_id]["username"]}: {data}')
        emit('update_dashboard', data, broadcast=True, namespace='/dashboard')
    except:
        pass

if __name__ == '__main__':
    socketio.run(app, debug=True)
