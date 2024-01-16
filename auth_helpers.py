from datetime import datetime, timedelta
from users import users
import jwt

# JWT configuration
def authenticate(username, password):
    user = users.get(username, None)
    if user and user['password'] == password:
        return user

def generate_token(user_id):
    # Avoid circular import
    from main import app

    payload = {
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')