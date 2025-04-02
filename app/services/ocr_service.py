from flask import Blueprint, render_template, request, jsonify, current_app
import os
import uuid
from werkzeug.utils import secure_filename

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
            pass  # Добавляем инструкцию pass, если блок был пустым
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


import os
import io  # Добавляем импорт модуля io
import cv2
import numpy as np
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import logging
from typing import List, Dict, Any, Optional

class OCRService:
    """
    Сервис для распознавания текста из изображений и PDF файлов
    """
    
    def __init__(self, tesseract_cmd: str = None):
        """
        Инициализирует сервис OCR
        
        Args:
            tesseract_cmd: Путь к исполняемому файлу Tesseract
        """
        # Настройка пути к Tesseract, если он предоставлен
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        # Настройка логирования
        self.logger = logging.getLogger(__name__)
    
    def process_image(self, image_data):
        """
        Обрабатывает изображение и распознает текст
        
        Args:
            image_data (bytes): Бинарные данные изображения
            
        Returns:
            str: Распознанный текст
        """
        try:
            # Преобразуем байты в объект Image
            img = Image.open(io.BytesIO(image_data))
            
            # Конвертируем в формат OpenCV
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            
            # Предобработка изображения для лучшего распознавания
            self.logger.info("Предобработка изображения для OCR")
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # Применяем адаптивное пороговое значение для улучшения контраста
            # для документов и печатного текста
            binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY, 11, 2)
            
            # Распознаем текст с поддержкой русского и английского языков
            self.logger.info("Выполнение OCR с pytesseract")
            text = pytesseract.image_to_string(binary, lang='rus+eng')
            
            # Проверка результата
            if not text or len(text.strip()) < 10:
                self.logger.warning("OCR дал короткий или пустой результат, повторная попытка с оригинальным изображением")
                # Если результат плохой, попробуем с оригинальным изображением
                text = pytesseract.image_to_string(img, lang='rus+eng')
            
            self.logger.info(f"OCR завершен, извлечено символов: {len(text)}")
            return text
        
        except Exception as e:
            self.logger.error(f"Ошибка при обработке OCR: {e}")
            import traceback
            self.logger.error(f"Стек ошибки: {traceback.format_exc()}")
            return None

    def some_method_with_cyclic_dependency(self, param):
        # Импортируем зависимость только внутри метода
        from app.services.some_other_service import SomeOtherService
        
        other_service = SomeOtherService()
        # использование other_service