from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from database.config import DATABASE_URL
from database.base import Document, DocumentAttribute, Attribute, Permission, User
from routes.utils import token_required

document_bp = Blueprint('document', __name__)
Session = sessionmaker(bind=DATABASE_URL)
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

    return jsonify({'document_id': str(document.id)}), 201