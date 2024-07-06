import datetime
from functools import wraps
from flask import request, jsonify, current_app
import jwt
from sqlalchemy.orm import sessionmaker
from database.config import DATABASE_URL
from database.base import User

Session = sessionmaker(bind=DATABASE_URL)
session = Session()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = session.query(User).filter_by(username=data['user']).first()
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

def roles_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            data = args[0]  # Данные из декодированного токена
            user_roles = data.get('roles', [])
            if not any(role in user_roles for role in roles):
                return jsonify({'message': 'You do not have the required role to access this resource.'}), 403
            return f(*args, **kwargs)
        return decorated
    return wrapper

def revoke_token(token):
    try:
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        exp = data['exp']
        current_time = datetime.datetime.now(datetime.UTC).timestamp()
        ttl = exp - current_time
#        redis_client.set(token, 'revoked', ex=int(ttl))
    except jwt.InvalidTokenError:
        pass  # Если токен недействителен, мы просто игнорируем его