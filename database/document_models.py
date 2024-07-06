import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, LargeBinary, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

DocumentBase = declarative_base()

# Document
class Document(DocumentBase):
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

# Document page
class Page(DocumentBase):
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
class Attribute(DocumentBase):
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
class DocumentAttribute(DocumentBase):
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
