from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .user_models import UserBase, User, Role
from .document_models import DocumentBase

def setup_database(database_url):
    engine = create_engine(database_url)
    UserBase.metadata.create_all(engine)
    DocumentBase.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()