import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, User
from werkzeug.security import generate_password_hash

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://arcuser:password@arc-db/arcdb')

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def create_user(username, password):
    password_hash = generate_password_hash(password)
    new_user = User(username=username, password_hash=password_hash)
    session.add(new_user)
    session.commit()
    print(f'User {username} was created.')

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: create_user.py <username> <password>")
    else:
        create_user(sys.argv[1], sys.argv[2])
