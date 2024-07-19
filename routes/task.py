from flask import Blueprint, jsonify
import redis

task_bp = Blueprint('task', __name__)
redis_client = redis.StrictRedis(host='redis', port=6379, db=0)

@task_bp.route('/api/task_status/<task_id>', methods=['GET'])
def task_status(task_id):
    status = redis_client.get(f'task_{task_id}_status')
    if status is None:
        return jsonify({'error': 'Task not found'}), 404
    if status.decode('utf-8') == 'processed':
        text = redis_client.get(f'task_{task_id}_process_text_ai')
        return jsonify({'status': 'processed', 'text': text.decode('utf-8') if text else None})
    return jsonify({'status': status.decode('utf-8')})

@task_bp.route('/api/task_result/<task_id>', methods=['GET'])
def task_result(task_id):
    result = redis_client.get(f'task_{task_id}_process_text_ai')
    if result:
        return jsonify({'result': result.decode('utf-8')})
    else:
        return jsonify({'error': 'Task not found'}), 404
