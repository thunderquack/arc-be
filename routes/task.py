from flask import Blueprint, jsonify, request
import redis
import uuid

task_bp = Blueprint('task', __name__)
redis_client = redis.StrictRedis(host='redis', port=6379, db=0)

@task_bp.route('/api/task_status/<task_id>', methods=['GET'])
def task_status(task_id):
    status = redis_client.get(f'task_{task_id}_status')
    if status:
        return jsonify({'status': status.decode('utf-8')})
    else:
        return jsonify({'error': 'Task not found'}), 404

@task_bp.route('/api/task_result/<task_id>', methods=['GET'])
def task_result(task_id):
    result = redis_client.get(f'task_{task_id}_process_text_ai')
    if result:
        return jsonify({'result': result.decode('utf-8')})
    else:
        return jsonify({'error': 'Task not found'}), 404