from database.config import DATABASE_URL
from messaging.utils import get_rabbitmq_connection, declare_queues, PAGE_UPDATE_EVENTS, LOGIN_EVENTS_QUEUE
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
    message = f'User {username} logged in at {datetime.datetime.now(datetime.UTC)}'
    send_message_to_queue(LOGIN_EVENTS_QUEUE, message)

def send_page_update_event(page_id):
    message = f'{page_id}'
    send_message_to_queue(PAGE_UPDATE_EVENTS, message)