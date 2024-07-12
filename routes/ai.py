from flask import Blueprint, request, jsonify
import redis
import uuid

from messaging.producer import send_process_text_event
from routes.utils import token_required

ai_bp = Blueprint('ai', __name__)
redis_client = redis.StrictRedis(host='redis', port=6379, db=0)

@ai_bp.route('/api/process_text', methods=['POST'])
@token_required
def process_text(current_user):
    data = request.get_json()
    text = data.get('text')
    if not text:
        return jsonify({'error': 'Text is required'}), 400

    task_id = str(uuid.uuid4())
    redis_client.set(f'task_{task_id}_process_text_ai', text, ex=3600)
    redis_client.set(f'task_{task_id}_status', 'new', ex=3600)

    send_process_text_event(task_id)
    
    return jsonify({'task_id': task_id})