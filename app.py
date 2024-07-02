from flask import Flask, request, jsonify
import jwt
import datetime
import os
from flask_cors import CORS
from consumer import consume_login_events, RABBITMQ_URL
import threading
import pika

rabbitmq_connection = None
rabbitmq_channel = None

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}}) 
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')

def get_rabbitmq_connection():
    global rabbitmq_connection, rabbitmq_channel
    if not rabbitmq_connection or rabbitmq_connection.is_closed:
        parameters = pika.URLParameters(RABBITMQ_URL)
        rabbitmq_connection = pika.BlockingConnection(parameters)
        rabbitmq_channel = rabbitmq_connection.channel()
        rabbitmq_channel.queue_declare(queue='login_events')
    return rabbitmq_connection, rabbitmq_channel

def send_login_event(username):
    try:
        _, channel = get_rabbitmq_connection()
        message = f'User {username} logged in at {datetime.datetime.utcnow()}'
        channel.basic_publish(exchange='', routing_key='login_events', body=message)
    except Exception as e:
        print(f'Failed to send message to RabbitMQ: {str(e)}')

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

if __name__ == '__main__':
    threading.Thread(target=consume_login_events, daemon=True).start()
    app.run(host='0.0.0.0', port=3000, debug=True)