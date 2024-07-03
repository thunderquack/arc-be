from functools import wraps
import threading
from flask import Flask, request, jsonify, current_app
import jwt
import datetime
import os
from flask_cors import CORS
import redis
from consumer import consume_events, login_events_callback
from producer import send_login_event

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')

# Invalid! 
redis_client = redis.StrictRedis(host='host.docker.internal', port=6379, db=1, decode_responses=True)

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
    redis_client.set(token, 'revoked', ex=3600)  # токен в черном списке в течение часа

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username == 'user' and password == 'password':
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
