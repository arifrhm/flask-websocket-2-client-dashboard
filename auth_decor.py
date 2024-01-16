from functools import wraps
import jwt
from users import users
from flask import request

def authenticate_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Avoid circular import
        from main import app

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