import pika
import os

RABBITMQ_URL = 'amqp://guest:guest@localhost:5672/'

def get_rabbitmq_connection():
    parameters = pika.URLParameters(RABBITMQ_URL)
    return pika.BlockingConnection(parameters)

def callback(ch, method, properties, body):
    print(f"Received login event: {body}")

def consume_login_events():
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    channel.queue_declare(queue='login_events')

    channel.basic_consume(queue='login_events', on_message_callback=callback, auto_ack=True)
    print('Waiting for login events. To exit press CTRL+C')
    channel.start_consuming()