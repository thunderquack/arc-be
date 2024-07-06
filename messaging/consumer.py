from messaging.utils import get_rabbitmq_connection, declare_queues

def consume_events(queue_name, callback):
    connection, channel = get_rabbitmq_connection()
    declare_queues(channel)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print(f'Waiting for {queue_name} events. To exit press CTRL+C')
    channel.start_consuming()

def login_events_callback(ch, method, properties, body):
    print(f"Received login event: {body}")
