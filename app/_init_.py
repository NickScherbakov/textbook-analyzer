from flask import Flask
import os

def create_app(config_object=None):
    """Фабрика приложений Flask"""
    app = Flask(__name__, instance_relative_config=True)
    
    # Загрузка конфигурации
    if config_object is None:
        # Импортируем здесь, чтобы избежать циклических импортов
        from config import get_config
        app.config.from_object(get_config())
    else:
        app.config.from_object(config_object)
    
    # Убедимся, что папка uploads существует
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    
    # Регистрация маршрутов
    from app.main import main_bp
    app.register_blueprint(main_bp)
    
    return app