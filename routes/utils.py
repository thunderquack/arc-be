# routes/utils.py

import datetime
from functools import wraps
from flask import request, jsonify, current_app
import jwt

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
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        
        return f(data, *args, **kwargs)
    return decorated

def revoke_token(token):
    try:
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        exp = data['exp']
        current_time = datetime.datetime.now(datetime.UTC).timestamp()
        ttl = exp - current_time
        # redis_client.set(token, 'revoked', ex=int(ttl))
    except jwt.InvalidTokenError:
        pass  # Если токен недействителен, мы просто игнорируем его