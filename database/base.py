import datetime
import uuid
from sqlalchemy import UUID, Column, DateTime, ForeignKey, Integer, LargeBinary, String, Table, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Document
class Document(Base):
    __tablename__ = 'documents'
    
    # Unique document identifier
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Document title
    title = Column(String(255), nullable=False)
    
    # Document creation date
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))
    
    # Document update date
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))

    # Relationship with pages
    pages = relationship('Page', order_by='Page.page_number', back_populates='document')
    
    # Relationship with attributes
    attributes = relationship('DocumentAttribute', back_populates='document')
    
    # Relationship with roles
    roles = relationship('Role', secondary='document_roles', back_populates='documents')

# Document page
class Page(Base):
    __tablename__ = 'pages'
    
    # Unique page identifier
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Document identifier
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id', ondelete='CASCADE'))
    
    # Page number
    page_number = Column(Integer, nullable=False)
    
    # Page image data
    image_data = Column(LargeBinary, nullable=False)
    
    # Page creation date
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))

    # Relationship with document
    document = relationship('Document', back_populates='pages')

    __table_args__ = (
        UniqueConstraint('document_id', 'page_number', name='unique_document_page'),
    )

# Document attribute
class Attribute(Base):
    __tablename__ = 'attributes'
    
    # Unique attribute identifier
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Attribute name
    name = Column(String(255), nullable=False)
    
    # Attribute description
    description = Column(Text)

    # Relationship with document attributes
    document_attributes = relationship('DocumentAttribute', back_populates='attribute')

# Document attribute value
class DocumentAttribute(Base):
    __tablename__ = 'document_attributes'
    
    # Unique document attribute identifier
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Document identifier
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id', ondelete='CASCADE'))
    
    # Attribute identifier
    attribute_id = Column(UUID(as_uuid=True), ForeignKey('attributes.id', ondelete='CASCADE'))
    
    # Attribute value
    value = Column(Text)

    # Relationship with document
    document = relationship('Document', back_populates='attributes')
    
    # Relationship with attribute
    attribute = relationship('Attribute', back_populates='document_attributes')

    __table_args__ = (
        UniqueConstraint('document_id', 'attribute_id', name='unique_document_attribute'),
    )

# Linking table for documents and roles
document_roles = Table('document_roles', Base.metadata,
    # Document identifier
    Column('document_id', UUID(as_uuid=True), ForeignKey('documents.id'), primary_key=True),
    
    # Role identifier
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True)
)


# User
class User(Base):
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
class Role(Base):
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
class Permission(Base):
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
user_roles = Table('user_roles', Base.metadata,
    # User identifier
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    
    # Role identifier
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True)
)

# Linking table for roles and permissions
role_permissions = Table('role_permissions', Base.metadata,
    # Role identifier
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True),
    
    # Permission identifier
    Column('permission_id', UUID(as_uuid=True), ForeignKey('permissions.id'), primary_key=True)
)

