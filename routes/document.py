import base64
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from database.config import DATABASE_URL
from database.base import Document, DocumentAttribute, Attribute, Permission, User, Page
from database.setup import setup_database
from routes.utils import token_required
from PIL import Image
import io
import datetime

document_bp = Blueprint('document', __name__)
Session = setup_database(DATABASE_URL)
session = Session()

@document_bp.route('/api/documents', methods=['POST'])
@token_required
def create_document(current_user):
    data = request.form
    title = data.get('title')
    attributes = data.getlist('attributes')
    permission_name = data.get('permission')

    document = Document(title=title, created_by=current_user.id)
    session.add(document)
    session.commit()

    for attribute in attributes:
        attr_name = attribute.get('name')
        attr_value = attribute.get('value')
        
        attr = session.query(Attribute).filter_by(name=attr_name).first()
        if not attr:
            attr = Attribute(name=attr_name)
            session.add(attr)
            session.commit()

        doc_attr = DocumentAttribute(document_id=document.id, attribute_id=attr.id, value=attr_value)
        session.add(doc_attr)
    
    permission = session.query(Permission).filter_by(name=permission_name).first()
    if permission:
        document.permissions.append(permission)
    session.commit()

    # Handle file upload
    file = request.files['file']
    if file:
        # Try to convert the image to PNG
        try:
            image = Image.open(file.stream)
            if image.format != 'PNG':
                image = image.convert('RGBA')
                png_image_io = io.BytesIO()
                image.save(png_image_io, format='PNG')
                png_image_data = png_image_io.getvalue()
            else:
                png_image_data = file.read()
        except Exception as e:
            return jsonify({'message': 'Invalid image file'}), 400

        page = Page(
            document_id=document.id,
            page_number=1,  # For simplicity, assigning page number 1
            image_data=png_image_data,
            created_at=datetime.datetime.now(datetime.UTC)
        )
        session.add(page)
        session.commit()

    return jsonify({'document_id': str(document.id)}), 201

@document_bp.route('/api/documents', methods=['GET'])
@token_required
def get_documents(current_user):
    documents = session.query(Document).all()
    document_list = []
    for doc in documents:
        document_list.append({
            'id': str(doc.id),
            'title': doc.title,
            'created_at': doc.created_at,
            'pages': len(doc.pages),
        })
    return jsonify(document_list), 200

@document_bp.route('/api/documents/<document_id>', methods=['GET'])
@token_required
def get_document(current_user, document_id):
    document = session.query(Document).filter_by(id=document_id).first()
    if not document:
        return jsonify({'message': 'Document not found'}), 404

    document_data = {
        'id': str(document.id),
        'title': document.title,
        'created_at': document.created_at,
        'creator': document.creator.username,  # Assuming User model has username field
        'pages': [{'page_number': page.page_number, 'image_data': 'data:image/png;base64,' + base64.b64encode(page.image_data).decode()} for page in document.pages],
        'summary': document.summary if hasattr(document, 'summary') else '',  # Adjust according to your actual attribute names
        'recognizedText': document.recognized_text if hasattr(document, 'recognized_text') else ''  # Adjust according to your actual attribute names
    }
    return jsonify(document_data), 200