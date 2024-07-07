import pika

RABBITMQ_URL = 'amqp://guest:guest@rabbitmq:5672/'

def get_rabbitmq_connection():
    parameters = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    return connection, channel

def declare_queues(channel):
    channel.queue_declare(queue='login_events')
