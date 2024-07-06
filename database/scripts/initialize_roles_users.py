# Creates default admin with password admin amd user with password user
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy.orm import sessionmaker
from database.setup import setup_database
from database.models import Role, User
from werkzeug.security import generate_password_hash

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://arcuser:password@arc-db/arcdb')

session = setup_database(DATABASE_URL)

# Создание ролей
roles = ['user', 'admin']
for role_name in roles:
    role = session.query(Role).filter_by(name=role_name).first()
    if not role:
        print(f'Role {role_name} does not exist, creating it')
        role = Role(name=role_name)
        session.add(role)

session.commit()  # Коммитим изменения после добавления ролей

# Создание пользователей
users = [
    {'username': 'admin', 'password': 'admin', 'roles': ['admin', 'user']},
    {'username': 'user', 'password': 'user', 'roles': ['user']}
]

for user_data in users:
    user = session.query(User).filter_by(username=user_data['username']).first()
    if not user:
        print(f'User {user_data["username"]} does not exist, creating it')
        user = User(username=user_data['username'], password_hash=generate_password_hash(user_data['password']))
        session.add(user)
        session.commit()  # Коммитим, чтобы получить ID пользователя для дальнейших операций

    for role_name in user_data['roles']:
        role = session.query(Role).filter_by(name=role_name).first()
        if role and role not in user.roles:
            print(f'Adding role {role_name} to user {user_data["username"]}')
            user.roles.append(role)

    session.commit()  # Коммитим изменения после добавления ролей

session.close()