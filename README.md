# Textbook Analyzer - Intelligent Learning Materials Assistant

An application for analyzing and explaining educational materials using Yandex Cloud artificial intelligence technologies.

## Features
- Text recognition from textbook images (OCR)
- Intelligent analysis and detailed explanation of educational material
- Answers to questions about textbook content
- Generation of examples and additional learning materials

## Technologies
- Python 3.9+
- Flask
- Yandex Cloud Vision API (OCR)
- YandexGPT API
- Bootstrap 5

## Installation and Launch

### Prerequisites
- Python 3.9 or higher
- Yandex Cloud account with a configured service account
- IAM token and Yandex Cloud folder ID

### Installation Steps

1. Clone the repository
```bash
git clone https://github.com/NickScherbakov/textbook-analyzer.git
cd textbook-analyzer
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set environment variables
```bash
export YANDEX_IAM_TOKEN=your_token
export YANDEX_FOLDER_ID=your_folder_id
```

4. Launch the application
```bash
flask run
```

After launching, the application will be available at http://localhost:5000
