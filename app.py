import threading
from flask import Flask, request, jsonify
import jwt
import datetime
import os
from flask_cors import CORS
from consumer import consume_events, login_events_callback
from producer import send_login_event

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')

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

        # Отправка сообщения в RabbitMQ
        send_login_event(username)

        return jsonify({'token': token})

    return jsonify({'message': 'Invalid credentials'}), 401

if __name__ == '__main__':
    threading.Thread(target=lambda: consume_events('login_events', login_events_callback), daemon=True).start()
    app.run(host='0.0.0.0', port=3000)