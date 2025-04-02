from flask import Blueprint, render_template, request, jsonify, current_app
import os
import uuid
from werkzeug.utils import secure_filename

from app.services.ocr_service import OCRService
from app.services.gpt_service import GPTService
from app.models.document import Document

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@main_bp.route('/upload', methods=['POST'])
def upload_file():
    """Обработка загруженного файла"""
    if 'file' not in request.files:
        return jsonify({'error': 'Файл не найден'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Инициализация сервисов
            ocr_service = OCRService(
                tesseract_path=current_app.config.get('TESSERACT_PATH')
            )
            
            gpt_service = GPTService(
                gpt_url=current_app.config['YANDEX_GPT_URL'],
                folder_id=current_app.config['YANDEX_FOLDER_ID'],
                iam_token=current_app.config['YANDEX_IAM_TOKEN'],
                model_uri=current_app.config['YANDEX_GPT_MODEL']
            )
            
            # Распознавание текста
            with open(filepath, "rb") as image_file:
                image_data = image_file.read()
            extracted_text = ocr_service.process_image(image_data)
            
            # Создание документа
            document = Document(
                filename=filename,
                content=extracted_text,
                file_path=filepath
            )
            
            # Генерация объяснения
            explanation = gpt_service.explain_content(extracted_text)
            
            return jsonify({
                'status': 'success',
                'extracted_text': extracted_text,
                'explanation': explanation,
                'document_id': document.id
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            # Удаляем временный файл, если не нужно сохранять
            # Раскомментировать, если файлы не нужно хранить
            # if os.path.exists(filepath):
            #    os.remove(filepath)
    else:
        return jsonify({'error': 'Недопустимый формат файла'}), 400

@main_bp.route('/ask', methods=['POST'])
def ask_question():
    """Обработка вопроса по содержанию"""
    data = request.json
    if not data or 'text' not in data or 'question' not in data:
        return jsonify({'error': 'Необходимо предоставить текст и вопрос'}), 400
    
    try:
        gpt_service = GPTService(
            gpt_url=current_app.config['YANDEX_GPT_URL'],
            folder_id=current_app.config['YANDEX_FOLDER_ID'],
            iam_token=current_app.config['YANDEX_IAM_TOKEN'],
            model_uri=current_app.config['YANDEX_GPT_MODEL']
        )
        
        # Получаем ответ на вопрос
        answer = gpt_service.answer_question(data['text'], data['question'])
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def allowed_file(filename):
    """Проверка допустимого расширения файла"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


import cv2
import numpy as np
import pytesseract
from PIL import Image
import io

class OCRService:
    def __init__(self, tesseract_path=None):
        """Initialize OCR service with optional Tesseract path configuration."""
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

    def process_image(self, image_data):
        """Extract text from an image using OCR."""
        try:
            # Convert bytes to PIL Image
            img = Image.open(io.BytesIO(image_data))
            
            # Convert to OpenCV format
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            
            # Preprocess the image for better OCR results
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
            
            # Perform OCR
            text = pytesseract.image_to_string(binary, lang='eng+rus')
            return text
        except Exception as e:
            print(f"OCR processing error: {e}")
            return None