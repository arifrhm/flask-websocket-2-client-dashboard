import os
from datetime import datetime, timedelta

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import jwt

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

### WRAPPER BLOCK ###

from functools import wraps

def authenticate_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.args.get('token')
        try:
            decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = decoded['sub']
            print(f'{users[user_id]["username"]} connected to /dashboard')
            return func(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False
    return wrapper

### WRAPPER BLOCK ###


@socketio.on('connect', namespace='/dashboard')
@authenticate_token
def handle_connect():
    print(f"{request.sid} Connected !!!!!!!")

@socketio.on('smartband_data', namespace='/dashboard')
@authenticate_token
def handle_smartband_data(data):
    print("Emitting to update_dashboard listeners with namespace /dashboard")
    emit('update_dashboard', data, broadcast=True, namespace='/dashboard')
    print("Emitted !!!!")

if __name__ == '__main__':
    socketio.run(app, debug=True)
