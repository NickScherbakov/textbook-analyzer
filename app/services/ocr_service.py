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
                vision_url=current_app.config['YANDEX_VISION_URL'],
                folder_id=current_app.config['YANDEX_FOLDER_ID'],
                iam_token=current_app.config['YANDEX_IAM_TOKEN']
            )
            
            gpt_service = GPTService(
                gpt_url=current_app.config['YANDEX_GPT_URL'],
                folder_id=current_app.config['YANDEX_FOLDER_ID'],
                iam_token=current_app.config['YANDEX_IAM_TOKEN'],
                model_uri=current_app.config['YANDEX_GPT_MODEL']
            )
            
            # Распознавание текста
            extracted_text = ocr_service.recognize_text(filepath)
            
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


import requests
import base64
import json

class OCRService:
    """Сервис для распознавания текста из изображений с помощью Yandex Vision"""
    
    def __init__(self, vision_url, folder_id, iam_token):
        """
        Инициализация сервиса OCR
        
        Args:
            vision_url (str): URL API Yandex Vision
            folder_id (str): Идентификатор каталога в Yandex Cloud
            iam_token (str): IAM-токен для авторизации
        """
        self.vision_url = vision_url
        self.headers = {
            "Authorization": f"Bearer {iam_token}",
            "Content-Type": "application/json",
            "x-folder-id": folder_id
        }
    
    def recognize_text(self, image_path):
        """
        Распознавание текста из изображения
        
        Args:
            image_path (str): Путь к файлу изображения
            
        Returns:
            str: Распознанный текст
        """
        # Чтение изображения и кодирование в base64
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Формирование запроса к API
        payload = {
            "folderId": self.headers["x-folder-id"],
            "analyze_specs": [{
                "content": encoded_image,
                "features": [{
                    "type": "TEXT_DETECTION",
                    "text_detection_config": {
                        "language_codes": ["ru", "en"]
                    }
                }]
            }]
        }
        
        # Отправка запроса
        response = requests.post(self.vision_url, headers=self.headers, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"Ошибка при обращении к Yandex Vision: {response.text}")
        
        result = response.json()
        
        # Извлечение распознанного текста из ответа
        try:
            # Проверяем наличие результатов распознавания
            pages = result["results"][0]["results"][0]["textDetection"]["pages"]
            if not pages:
                return ""
                
            # Извлекаем текст из блоков
            text = ""
            for page in pages:
                for block in page.get("blocks", []):
                    for line in block.get("lines", []):
                        for word in line.get("words", []):
                            text += word.get("text", "") + " "
            
            return text.strip()
        except (KeyError, IndexError) as e:
            raise Exception(f"Ошибка при обработке ответа от Yandex Vision: {str(e)}")