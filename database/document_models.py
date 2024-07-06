import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, LargeBinary, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

DocumentBase = declarative_base()

class Document(DocumentBase):
    __tablename__ = 'documents'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))

    pages = relationship('Page', order_by='Page.page_number', back_populates='document')
    attributes = relationship('DocumentAttribute', back_populates='document')

class Page(DocumentBase):
    __tablename__ = 'pages'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id', ondelete='CASCADE'))
    page_number = Column(Integer, nullable=False)
    image_data = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))

    document = relationship('Document', back_populates='pages')

    __table_args__ = (
        UniqueConstraint('document_id', 'page_number', name='unique_document_page'),
    )

class Attribute(DocumentBase):
    __tablename__ = 'attributes'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)

    document_attributes = relationship('DocumentAttribute', back_populates='attribute')

class DocumentAttribute(DocumentBase):
    __tablename__ = 'document_attributes'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id', ondelete='CASCADE'))
    attribute_id = Column(UUID(as_uuid=True), ForeignKey('attributes.id', ondelete='CASCADE'))
    value = Column(Text)

    document = relationship('Document', back_populates='attributes')
    attribute = relationship('Attribute', back_populates='document_attributes')

    __table_args__ = (
        UniqueConstraint('document_id', 'attribute_id', name='unique_document_attribute'),
    )
