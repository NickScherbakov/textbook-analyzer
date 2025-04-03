import os
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

class Config:
    # Secret keys
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key-for-dev')
    API_KEY = os.environ.get('API_KEY', 'default-api-key-for-dev')
    
    # Database configuration
    DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///textbook_analyzer.db')
    
    # File upload configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads'))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf", "tiff", "bmp"}
    
    # OCR configuration
    TESSERACT_PATH = os.environ.get('TESSERACT_PATH', None)
    
    # Yandex Cloud configuration
    YANDEX_FOLDER_ID = os.environ.get('YANDEX_FOLDER_ID', '')
    YANDEX_OAUTH_TOKEN = os.environ.get('YANDEX_OAUTH_TOKEN', '')  # OAuth token for getting IAM token
    IAM_TOKEN = os.environ.get('YANDEX_IAM_TOKEN', '')  # For backwards compatibility
    YANDEX_IAM_TOKEN = IAM_TOKEN  # For compatibility
    YANDEX_VISION_URL = 'https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze'
    YANDEX_GPT_URL = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
    YANDEX_GPT_MODEL = f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite"
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'app.log'))
    
    @classmethod
    def validate_required_settings(cls):
        """Проверяет наличие обязательных настроек"""
        required_settings = {
            'YANDEX_FOLDER_ID': cls.YANDEX_FOLDER_ID,
            'YANDEX_OAUTH_TOKEN': cls.YANDEX_OAUTH_TOKEN
        }
        
        missing = []
        for name, value in required_settings.items():
            if not value:
                missing.append(name)
        
        if missing:
            logging.error(f"Отсутствуют обязательные настройки: {', '.join(missing)}")
            return False
        
        return True
