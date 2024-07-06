import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash
from database.setup import setup_database
from database.user_models import User, Role
from database.config import DATABASE_URL

def create_user(username, password, roles):
    Session = setup_database(DATABASE_URL)
    session = Session()

    # Проверка, существует ли пользователь
    existing_user = session.query(User).filter_by(username=username).first()
    if existing_user:
        print(f"User {username} already exists.")
        session.close()
        return

    user = User(username=username, password_hash=generate_password_hash(password))
    for role_name in roles:
        role = session.query(Role).filter_by(name=role_name).first()
        if role:
            user.roles.append(role)
        else:
            print(f"Role {role_name} does not exist and will not be assigned to user {username}.")
    session.add(user)
    session.commit()
    print(f"User {username} created with roles: {', '.join(roles)}")
    session.close()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: create_user.py <username> <password> <roles>")
        print("Example: python create_user.py newuser password user admin")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    roles = sys.argv[3:]
    create_user(username, password, roles)
