from functools import wraps
import threading
from flask import Flask, request, jsonify, current_app
import jwt
import datetime
import os
from flask_cors import CORS
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, User
from werkzeug.security import check_password_hash
from producer import send_login_event
from consumer import consume_events, login_events_callback

import ptvsd

app = Flask(__name__)

# Настройка CORS: Разрешить все источники (для разработки)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://arcuser:password@arc-db/arcdb')

# Enable ptvsd on 0.0.0.0 address and port 5678 that we'll connect later with our IDE
ptvsd.enable_attach(address=('0.0.0.0', 5678))
print("ptvsd enabled and waiting for attach...")

# Настройка Redis для хранения черного списка токенов
redis_client = redis.StrictRedis(host='redis', port=6379, db=1, decode_responses=True)

# Создаем подключение к базе данных
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
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
            if redis_client.get(token):
                return jsonify({'message': 'Token has been revoked!'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        
        return f(data['user'], *args, **kwargs)
    return decorated

def revoke_token(token):
    try:
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        exp = data['exp']
        current_time = datetime.datetime.now(datetime.UTC).timestamp()
        ttl = exp - current_time
        redis_client.set(token, 'revoked', ex=int(ttl))
    except jwt.InvalidTokenError:
        pass  # Если токен недействителен, мы просто игнорируем его

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = session.query(User).filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        token = jwt.encode({
            'user': username,
            'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm="HS256")

        send_login_event(username)
        return jsonify({'token': token})

    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
@token_required
def logout(user):
    token = request.headers['x-access-token']
    revoke_token(token)
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/protected', methods=['GET'])
@token_required
def protected_route(user):
    return jsonify({'message': f'Hello, {user}! This is a protected route.'})

if __name__ == '__main__':
    threading.Thread(target=lambda: consume_events('login_events', login_events_callback), daemon=True).start()
    app.run(host='0.0.0.0', port=3000)
