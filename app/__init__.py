from flask import Flask
import os
import logging

def create_app(config_object=None):
    """Фабрика приложений Flask"""
    app = Flask(__name__, instance_relative_config=True)
    
    # Загрузка конфигурации
    if config_object is None:
        # Импортируем здесь, чтобы избежать циклических импортов
        from config import get_config
        config = get_config()
        app.config.from_object(config)
    else:
        app.config.from_object(config_object)
    
    # Убедимся, что папки существуют
    os.makedirs(app.config.get("UPLOAD_FOLDER", "uploads"), exist_ok=True)
    
    # Создаем директорию для логов
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Настройка логирования Flask
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(logs_dir, 'flask.log'), encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # Регистрация маршрутов
    from app.main import main_bp
    app.register_blueprint(main_bp)
    
    # Регистрация blueprint для API логов
    try:
        from app.routes.log_routes import log_bp
        app.register_blueprint(log_bp)
    except ImportError:
        app.logger.warning("Blueprint для логов не зарегистрирован (файл не найден)")
    
    # Если ALLOWED_EXTENSIONS не определено в конфигурации, добавим значение по умолчанию
    if 'ALLOWED_EXTENSIONS' not in app.config:
        app.config['ALLOWED_EXTENSIONS'] = {"png", "jpg", "jpeg", "gif", "pdf"}
    
    return app