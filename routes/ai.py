from flask import Blueprint, request, jsonify
import redis
import uuid
import json
import pika

ai_bp = Blueprint('ai', __name__)
redis_client = redis.StrictRedis(host='redis', port=6379, db=0)

@ai_bp.route('/api/process_text', methods=['POST'])
def process_text():
    data = request.get_json()
    text = data.get('text')
    if not text:
        return jsonify({'error': 'Text is required'}), 400

    task_id = str(uuid.uuid4())
    redis_client.set(f'task_{task_id}_process_text_ai', text, ex=3600)
    redis_client.set(f'task_{task_id}_status', 'new', ex=3600)

    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='ai_events')

    event = {'type': 'process_text', 'id': task_id}
    channel.basic_publish(exchange='', routing_key='ai_events', body=json.dumps(event))
    connection.close()

    return jsonify({'task_id': task_id})
