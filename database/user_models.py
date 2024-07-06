import uuid
from sqlalchemy import Column, String, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

UserBase = declarative_base()

# User
class User(UserBase):
    __tablename__ = 'users'

    # Unique user identifier
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Unique username
    username = Column(String(50), unique=True, nullable=False)
    
    # User's password hash
    password_hash = Column(String(256), nullable=False)
    
    # Relationship with roles
    roles = relationship('Role', secondary='user_roles', back_populates='users')

    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash

# User role
class Role(UserBase):
    __tablename__ = 'roles'

    # Unique role identifier
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Unique role name
    name = Column(String(50), unique=True, nullable=False)
    
    # Relationship with users
    users = relationship('User', secondary='user_roles', back_populates='roles')
    
    # Relationship with permissions
    permissions = relationship('Permission', secondary='role_permissions', back_populates='roles')

    def __init__(self, name):
        self.name = name

# Permission
class Permission(UserBase):
    __tablename__ = 'permissions'

    # Unique permission identifier
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Unique permission name
    name = Column(String(50), unique=True, nullable=False)
    
    # Relationship with roles
    roles = relationship('Role', secondary='role_permissions', back_populates='permissions')

    def __init__(self, name):
        self.name = name

# Linking table for users and roles
user_roles = Table('user_roles', UserBase.metadata,
    # User identifier
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    
    # Role identifier
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True)
)

# Linking table for roles and permissions
role_permissions = Table('role_permissions', UserBase.metadata,
    # Role identifier
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True),
    
    # Permission identifier
    Column('permission_id', UUID(as_uuid=True), ForeignKey('permissions.id'), primary_key=True)
)
