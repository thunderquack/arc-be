import time
import pika

RABBITMQ_URL = 'amqp://guest:guest@rabbitmq:5672/'
LOGIN_EVENTS_QUEUE = 'login_events'
PAGE_UPDATE_EVENTS = 'page_update_events'
TESSERACT_URL = 'http://tesseract:8884/tesseract'

def get_rabbitmq_connection():
    parameters = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    return connection, channel

def declare_queues(channel):
    channel.queue_declare(queue=LOGIN_EVENTS_QUEUE)
    channel.queue_declare(queue=PAGE_UPDATE_EVENTS)

def wait_for_rabbitmq(timeout):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
            connection.close()
            print("RabbitMQ is up and running.")
            return True
        except pika.exceptions.AMQPConnectionError:
            print("Waiting for RabbitMQ...")
            time.sleep(5)
    print("Timeout waiting for RabbitMQ.")
    return False