from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash
import jwt
import datetime
from database.setup import setup_database
from database.config import DATABASE_URL
from database.base import User, Role
from messaging.producer import send_login_event
from routes.utils import roles_required, token_required

auth_bp = Blueprint('auth', __name__)
Session = setup_database(DATABASE_URL)
session = Session()

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = session.query(User).filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        roles = [role.name for role in user.roles]
        token = jwt.encode({
            'user': username,
            'roles': roles,
            'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1)
        }, current_app.config['SECRET_KEY'], algorithm="HS256")

        send_login_event(username)
        return jsonify({'token': token})

    return jsonify({'message': 'Invalid credentials'}), 401

@auth_bp.route('/api/logout', methods=['POST'])
@token_required
def logout(data):
    token = request.headers['x-access-token']
    # revoke_token(token)
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/api/protected', methods=['GET'])
@token_required
@roles_required('user')
def protected_route(data):
    return jsonify({'message': f'Hello, {data["user"]}! This is a protected route accessible only to users with the "user" role.'})

@auth_bp.route('/api/admin', methods=['GET'])
@token_required
@roles_required('admin')
def admin_route(data):
    return jsonify({'message': f'Hello, {data["user"]}! This is a protected route accessible only to users with the "admin" role.'})