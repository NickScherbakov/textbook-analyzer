import io
import os
import uuid
from flask import Flask, request, jsonify, send_file, render_template, Blueprint, session
from werkzeug.utils import secure_filename
from app.models.document import Document
from app.services.ocr_service import OCRService
from app.services.file_service import FileService
from app.services.log_service import LogService
from app.database.db import init_db, db_session, get_db
from app.config import Config
from flask import Blueprint

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Initialize services
ocr_service = OCRService(Config.TESSERACT_PATH)
file_service = FileService()
log_service = LogService()

# Initialize database
init_db()

@app.before_request
def create_session():
    """
    Создает сессию для пользователя, если она еще не создана,
    и генерирует уникальный идентификатор сессии
    """
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/api/documents', methods=['POST'])
def upload_document():
    session_id = session.get('session_id')
    log_service.info('Получен запрос на загрузку документа', session_id)
    
    if 'file' not in request.files:
        log_service.error('Отсутствует часть файла в запросе', session_id)
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        log_service.error('Не выбран файл', session_id)
        return jsonify({'error': 'No selected file'}), 400

    # Save file and get file path
    log_service.info(f'Сохранение файла {file.filename}', session_id)
    file_path = file_service.save_file(file)
    if not file_path:
        log_service.error('Ошибка сохранения файла', session_id)
        return jsonify({'error': 'Error saving file'}), 500

    file_type = file_service.get_file_type(file.filename)
    content = None
    
    # Process file based on type
    if file_type in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
        # For images, perform OCR
        log_service.info('Начало OCR обработки изображения', session_id)
        with open(file_path, 'rb') as f:
            content = ocr_service.process_image(f.read())
        log_service.success('OCR обработка завершена успешно', session_id)
    elif file_type in ['.txt', '.pdf', '.docx']:
        # For text documents, add appropriate handling here
        log_service.info('Извлечение текста из документа', session_id)
        content = "Text extracted from document"

    # Create document record
    log_service.info('Создание записи в базе данных', session_id)
    document = Document(
        title=os.path.basename(file.filename),
        content=content,
        file_path=file_path,
        file_type=file_type,
    )

    # Save to database
    db_session.add(document)
    db_session.commit()
    log_service.success('Документ успешно создан и сохранен', session_id)

    return jsonify(document.to_dict()), 201

@app.route('/api/documents', methods=['GET'])
def get_documents():
    session_id = session.get('session_id')
    log_service.info('Получен запрос на список документов', session_id)
    documents = db_session.query(Document).all()
    log_service.info(f'Найдено {len(documents)} документов', session_id)
    return jsonify([doc.to_dict() for doc in documents])

@app.route('/api/documents/<uuid>', methods=['GET'])
def get_document(uuid):
    session_id = session.get('session_id')
    log_service.info(f'Получен запрос на документ с UUID: {uuid}', session_id)
    document = db_session.query(Document).filter_by(uuid=uuid).first()
    if not document:
        log_service.warning(f'Документ с UUID {uuid} не найден', session_id)
        return jsonify({'error': 'Document not found'}), 404
    log_service.success('Документ найден и возвращен', session_id)
    return jsonify(document.to_dict())

@app.route('/api/documents/<uuid>/download', methods=['GET'])
def download_document(uuid):
    session_id = session.get('session_id')
    log_service.info(f'Получен запрос на скачивание документа с UUID: {uuid}', session_id)
    document = db_session.query(Document).filter_by(uuid=uuid).first()
    if not document or not document.file_path:
        log_service.error(f'Документ с UUID {uuid} не найден или отсутствует файл', session_id)
        return jsonify({'error': 'Document not found'}), 404
    log_service.success('Начало скачивания документа', session_id)
    return send_file(document.file_path, 
                     as_attachment=True, 
                     download_name=document.title)

@app.route('/api/documents/<uuid>', methods=['DELETE'])
def delete_document(uuid):
    session_id = session.get('session_id')
    log_service.info(f'Получен запрос на удаление документа с UUID: {uuid}', session_id)
    document = db_session.query(Document).filter_by(uuid=uuid).first()
    if not document:
        log_service.warning(f'Документ с UUID {uuid} не найден', session_id)
        return jsonify({'error': 'Document not found'}), 404

    # Delete file if exists
    if document.file_path:
        log_service.info('Удаление файла документа', session_id)
        file_service.delete_file(document.file_path)

    # Delete from database
    log_service.info('Удаление документа из базы данных', session_id)
    db_session.delete(document)
    db_session.commit()
    log_service.success('Документ успешно удален', session_id)

    return jsonify({'message': 'Document deleted successfully'})

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Получить логи для текущей сессии"""
    session_id = session.get('session_id')
    limit = request.args.get('limit', 50, type=int)
    logs = log_service.get_logs(session_id=session_id, limit=limit)
    return jsonify({'logs': logs})

@app.route('/api/logs/all', methods=['GET'])
def get_all_logs():
    """Получить все логи (только для администраторов)"""
    # Здесь в будущем можно добавить проверку прав администратора
    limit = request.args.get('limit', 100, type=int)
    logs = log_service.get_logs(limit=limit)
    return jsonify({'logs': logs})

@app.route('/api/logs/clear', methods=['POST'])
def clear_logs():
    """Очистить логи для текущей сессии"""
    session_id = session.get('session_id')
    log_service.clear_logs(session_id=session_id)
    return jsonify({'status': 'success'})

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    session_id = session.get('session_id')
    log_service.info('Посещение главной страницы', session_id)
    return render_template('index.html')

@main_bp.route('/upload', methods=['POST'])
def upload_file():
    session_id = session.get('session_id')
    log_service.info('Начало обработки загрузки файла', session_id)
    
    try:
        if 'file' not in request.files:
            log_service.error('Файл не найден в запросе', session_id)
            return jsonify({'error': 'Файл не найден'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            log_service.warning('Пустое имя файла', session_id)
            return jsonify({'error': 'Файл не выбран'}), 400
        
        # Проверяем допустимые расширения файлов
        allowed_extensions = app.config.get('ALLOWED_EXTENSIONS', {"png", "jpg", "jpeg", "gif", "pdf"})
        
        def allowed_file(filename):
            """Проверка допустимого расширения файла"""
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
        
        if file and allowed_file(file.filename):
            log_service.info(f'Файл {file.filename} принят к обработке', session_id)
            
            # Создаем безопасное имя файла
            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            
            # Проверяем наличие папки для загрузки
            upload_folder = app.config.get('UPLOAD_FOLDER')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder, exist_ok=True)
                log_service.info(f'Создана директория для загрузки: {upload_folder}', session_id)
            
            filepath = os.path.join(upload_folder, filename)
            log_service.info(f'Сохранение файла по пути: {filepath}', session_id)
            file.save(filepath)
            log_service.success(f'Файл сохранен: {filepath}', session_id)
            
            try:
                # Инициализация OCR сервиса
                log_service.info('Инициализация сервиса OCR', session_id)
                tesseract_path = app.config.get('TESSERACT_PATH')
                ocr_service = OCRService(tesseract_cmd=tesseract_path)
                
                # Распознавание текста
                log_service.info('Начало распознавания текста (OCR)', session_id)
                with open(filepath, "rb") as image_file:
                    image_data = image_file.read()
                
                extracted_text = ocr_service.process_image(image_data)
                if not extracted_text:
                    log_service.warning('Не удалось распознать текст в изображении', session_id)
                    extracted_text = "Не удалось распознать текст. Пожалуйста, загрузите изображение лучшего качества."
                else:
                    log_service.success('Текст успешно распознан', session_id)
                
                # Создание документа
                log_service.info('Создание документа', session_id)
                document = Document(
                    title=filename,
                    content=extracted_text,
                    file_path=filepath
                )
                
                # Проверка наличия необходимых конфигураций для GPT-сервиса
                required_configs = ['YANDEX_GPT_URL', 'YANDEX_FOLDER_ID', 'YANDEX_IAM_TOKEN', 'YANDEX_GPT_MODEL']
                missing_configs = [config for config in required_configs if not app.config.get(config)]
                
                if missing_configs:
                    log_service.warning(f'Отсутствуют необходимые конфигурации GPT: {", ".join(missing_configs)}', session_id)
                    explanation = "Объяснение недоступно. Пожалуйста, настройте необходимые параметры GPT-сервиса."
                else:
                    # Генерация объяснения через GPT-сервис
                    try:
                        from app.services.gpt_service import GPTService
                        log_service.info('Инициализация сервиса GPT', session_id)
                        gpt_service = GPTService(
                            gpt_url=app.config['YANDEX_GPT_URL'],
                            folder_id=app.config['YANDEX_FOLDER_ID'],
                            iam_token=app.config['YANDEX_IAM_TOKEN'],
                            model_uri=app.config['YANDEX_GPT_MODEL']
                        )
                        
                        log_service.info('Запрос объяснения от YandexGPT', session_id)
                        explanation = gpt_service.explain_content(extracted_text)
                        log_service.success('Получено объяснение от YandexGPT', session_id)
                    except Exception as gpt_error:
                        log_service.error(f'Ошибка при работе с GPT: {str(gpt_error)}', session_id)
                        explanation = f"Не удалось получить объяснение: {str(gpt_error)}"
                
                return jsonify({
                    'status': 'success',
                    'extracted_text': extracted_text,
                    'explanation': explanation,
                    'document_id': getattr(document, 'id', None)
                })
            except Exception as e:
                log_service.error(f'Ошибка при обработке файла: {str(e)}', session_id)
                import traceback
                error_details = traceback.format_exc()
                log_service.error(f'Детали ошибки: {error_details}', session_id)
                return jsonify({'error': str(e), 'details': error_details}), 500
        else:
            log_service.error(f'Недопустимый формат файла: {file.filename}', session_id)
            return jsonify({'error': f'Недопустимый формат файла. Разрешены только: {", ".join(allowed_extensions)}'}), 400
    except Exception as outer_e:
        log_service.error(f'Критическая ошибка при обработке запроса: {str(outer_e)}', session_id)
        import traceback
        error_details = traceback.format_exc()
        log_service.error(f'Детали критической ошибки: {error_details}', session_id)
        return jsonify({'error': 'Внутренняя ошибка сервера', 'details': str(outer_e)}), 500

@main_bp.route('/ask', methods=['POST'])
def ask_question():
    """Обработка вопроса по содержанию"""
    session_id = session.get('session_id')
    log_service.info('Получен запрос на ответ по вопросу', session_id)
    
    data = request.json
    if not data or 'text' not in data or 'question' not in data:
        log_service.error('Недостаточно данных для ответа на вопрос', session_id)
        return jsonify({'error': 'Необходимо предоставить текст и вопрос'}), 400
    
    log_service.info(f'Обработка вопроса: "{data["question"][:50]}..."', session_id)
    
    try:
        from app.services.gpt_service import GPTService
        gpt_service = GPTService(
            gpt_url=app.config['YANDEX_GPT_URL'],
            folder_id=app.config['YANDEX_FOLDER_ID'],
            iam_token=app.config['YANDEX_IAM_TOKEN'],
            model_uri=app.config['YANDEX_GPT_MODEL']
        )
        
        # Получаем ответ на вопрос
        log_service.info('Отправка запроса к YandexGPT', session_id)
        answer = gpt_service.answer_question(data['text'], data['question'])
        log_service.success('Получен ответ от YandexGPT', session_id)
        return jsonify({'answer': answer})
    except Exception as e:
        log_service.error(f'Ошибка при получении ответа: {str(e)}', session_id)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.register_blueprint(main_bp)
    app.run(debug=True)