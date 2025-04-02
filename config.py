import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

class Config:
    # Базовые настройки приложения
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-in-production")
    
    # Папка для загрузки файлов
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    
    # Настройки Yandex Cloud
    YANDEX_IAM_TOKEN = os.environ.get("YANDEX_IAM_TOKEN")
    YANDEX_FOLDER_ID = os.environ.get("YANDEX_FOLDER_ID")
    YANDEX_VISION_URL = "https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze"
    YANDEX_GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    YANDEX_GPT_MODEL = "gpt://b1gvmob95yysaplct532/yandexgpt-lite"
    
    # Формат файлов, которые можно загружать
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf"}

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    DEBUG = True

class ProductionConfig(Config):
    # В производственной среде должен быть настоящий секретный ключ
    SECRET_KEY = os.environ.get("SECRET_KEY")
    
    # Дополнительные настройки безопасности для production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True

# Выбор конфигурации в зависимости от окружения
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}

def get_config():
    """Получение конфигурации в зависимости от окружения"""
    config_name = os.environ.get("FLASK_ENV", "default")
    return config.get(config_name, config["default"])