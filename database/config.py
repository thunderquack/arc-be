import os

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://arcuser:password@arc-db/arcdb')
SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
