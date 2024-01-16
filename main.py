import os
from datetime import datetime, timedelta

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import jwt

from users import users
from auth_decor import authenticate_token
from auth_helpers import authenticate, generate_token

app = Flask(__name__, template_folder=os.curdir)
cors = CORS(app)

app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a secure secret key
socketio = SocketIO(app, cors_allowed_origins="*")

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


@socketio.on('connect', namespace='/report')
@authenticate_token
def handle_connect():
    print(f"{request.sid} Connected !!!!!!!")

@socketio.on('smartband_data', namespace='/report')
@authenticate_token
def handle_smartband_data(data):
    print("Emitting to update_dashboard listeners with namespace /report")
    print(data)
    emit('update_dashboard', data, broadcast=True, namespace='/report')
    print("Emitted !!!!")

if __name__ == '__main__':
    socketio.run(app, debug=True)
