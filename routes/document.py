from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from database.config import DATABASE_URL
from database.base import Document, DocumentAttribute, Attribute, Page, Permission, User
from routes.utils import token_required

document_bp = Blueprint('document', __name__)
Session = sessionmaker(bind=DATABASE_URL)
session = Session()

@document_bp.route('/api/documents', methods=['POST'])
@token_required
def create_document(current_user):
    data = request.form
    title = data.get('title')
    permission_name = data.get('permission')
    file = request.files.get('file')

    if not title or not file or not permission_name:
        return jsonify({'message': 'Title, file, and permission are required'}), 400

    if not file.filename.endswith('.png'):
        return jsonify({'message': 'Only PNG files are allowed'}), 400

    document = Document(title=title, created_by=current_user.id)
    session.add(document)
    session.commit()

    page_number = 1
    page = Page(document_id=document.id, page_number=page_number, image_data=file.read())
    session.add(page)
    session.commit()

    permission = session.query(Permission).filter_by(name=permission_name).first()
    if permission:
        document.permissions.append(permission)
    session.commit()

    return jsonify({'document_id': str(document.id)}), 201