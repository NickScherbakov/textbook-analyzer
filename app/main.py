import io
import os
from flask import Flask, request, jsonify, send_file, render_template, Blueprint
from werkzeug.utils import secure_filename
from app.models.document import Document
from app.services.ocr_service import OCRService
from app.services.file_service import FileService
from app.database.db import init_db, db_session, get_db
from app.config import Config
from flask import Blueprint
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH

# Initialize services
ocr_service = OCRService(Config.TESSERACT_PATH)
file_service = FileService()

# Initialize database
init_db()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/api/documents', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save file and get file path
    file_path = file_service.save_file(file)
    if not file_path:
        return jsonify({'error': 'Error saving file'}), 500

    file_type = file_service.get_file_type(file.filename)
    content = None
    
    # Process file based on type
    if file_type in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
        # For images, perform OCR
        with open(file_path, 'rb') as f:
            content = ocr_service.process_image(f.read())
    elif file_type in ['.txt', '.pdf', '.docx']:
        # For text documents, add appropriate handling here
        # This is a placeholder for future implementation
        content = "Text extracted from document"

    # Create document record
    document = Document(
        title=os.path.basename(file.filename),
        content=content,
        file_path=file_path,
        file_type=file_type,
    )

    # Save to database
    db_session.add(document)
    db_session.commit()

    return jsonify(document.to_dict()), 201

@app.route('/api/documents', methods=['GET'])
def get_documents():
    documents = db_session.query(Document).all()
    return jsonify([doc.to_dict() for doc in documents])

@app.route('/api/documents/<uuid>', methods=['GET'])
def get_document(uuid):
    document = db_session.query(Document).filter_by(uuid=uuid).first()
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    return jsonify(document.to_dict())

@app.route('/api/documents/<uuid>/download', methods=['GET'])
def download_document(uuid):
    document = db_session.query(Document).filter_by(uuid=uuid).first()
    if not document or not document.file_path:
        return jsonify({'error': 'Document not found'}), 404
    return send_file(document.file_path, 
                     as_attachment=True, 
                     download_name=document.title)

@app.route('/api/documents/<uuid>', methods=['DELETE'])
def delete_document(uuid):
    document = db_session.query(Document).filter_by(uuid=uuid).first()
    if not document:
        return jsonify({'error': 'Document not found'}), 404

    # Delete file if exists
    if document.file_path:
        file_service.delete_file(document.file_path)

    # Delete from database
    db_session.delete(document)
    db_session.commit()

    return jsonify({'message': 'Document deleted successfully'})

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)