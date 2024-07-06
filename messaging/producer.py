from database.config import DATABASE_URL
from messaging.utils import get_rabbitmq_connection, declare_queues
import datetime

def send_message_to_queue(queue_name, message):
    try:
        connection, channel = get_rabbitmq_connection()
        declare_queues(channel)
        channel.basic_publish(exchange='', routing_key=queue_name, body=message)
        connection.close()
    except Exception as e:
        print(f'Failed to send message to RabbitMQ: {str(e)}')

def send_login_event(username):
    message = f'User {username} logged in at {datetime.datetime.utcnow()}'
    send_message_to_queue('login_events', message)
