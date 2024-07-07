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