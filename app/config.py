import os
from dotenv import load_dotenv

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
    
    # OCR configuration
    TESSERACT_PATH = os.environ.get('TESSERACT_PATH', None)
    
    # IAM Token
    IAM_TOKEN = "your-iam-token-here"  # Replace with the actual token or environment variable
