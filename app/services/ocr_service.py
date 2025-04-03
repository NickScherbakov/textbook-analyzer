import base64
import requests
import json
import os
from pathlib import Path
from typing import List, Dict, Any

class OCRService:
    def __init__(self, folder_id: str, iam_token: str):
        """
        Инициализация сервиса OCR.
        
        Args:
            folder_id: Идентификатор каталога в Яндекс.Облаке
            iam_token: IAM-токен для аутентификации
        """
        self.folder_id = folder_id
        self.iam_token = iam_token
        self.vision_url = 'https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze'
        
    @staticmethod
    def get_iam_token(oauth_token: str) -> str:
        """
        Получение IAM-токена по OAuth-токену.
        
        Args:
            oauth_token: OAuth-токен Яндекс.Паспорта
            
        Returns:
            IAM-токен
        """
        url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
        response = requests.post(
            url,
            json={'yandexPassportOauthToken': oauth_token}
        )
        
        if response.status_code == 200:
            return response.json().get('iamToken')
        else:
            raise Exception(f'Ошибка получения IAM-токена: {response.status_code} - {response.text}')
    
    def recognize_file(self, file_path: str) -> str:
        """
        Распознает текст из файла изображения.
        
        Args:
            file_path: Путь к файлу изображения
            
        Returns:
            Распознанный текст
        """
        # Чтение и кодирование изображения
        with open(file_path, 'rb') as image_file:
            image_content = base64.b64encode(image_file.read()).decode('utf-8')
        
        return self._perform_recognition(image_content)
    
    def recognize_bytes(self, image_bytes: bytes) -> str:
        """
        Распознает текст из байтов изображения.
        
        Args:
            image_bytes: Байты изображения
            
        Returns:
            Распознанный текст
        """
        image_content = base64.b64encode(image_bytes).decode('utf-8')
        return self._perform_recognition(image_content)
    
    def _perform_recognition(self, image_content: str) -> str:
        """
        Выполняет запрос к API распознавания.
        
        Args:
            image_content: Закодированное в base64 содержимое изображения
            
        Returns:
            Распознанный текст
        """
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.iam_token}'
        }
        
        body = {
            'folderId': self.folder_id,
            'analyzeSpecs': [
                {
                    'content': image_content,
                    'features': [
                        {
                            'type': 'TEXT_DETECTION',
                            'textDetectionConfig': {
                                'languageCodes': ['ru', 'en'],
                                'model': 'page'
                            }
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(self.vision_url, headers=headers, json=body)
        
        if response.status_code == 200:
            return self._extract_text_from_response(response.json())
        else:
            error_msg = f'Ошибка распознавания: {response.status_code} - {response.text}'
            print(error_msg)
            return error_msg
    
    def _extract_text_from_response(self, response_json: Dict[str, Any]) -> str:
        """
        Извлекает текст из ответа API.
        
        Args:
            response_json: JSON-ответ от API
            
        Returns:
            Извлеченный текст
        """
        try:
            text_results = response_json['results'][0]['results'][0]['textDetection']['pages']
            full_text = ''
            for page in text_results:
                for block in page.get('blocks', []):
                    for line in block.get('lines', []):
                        for word in line.get('words', []):
                            full_text += word.get('text', '') + ' '
            return full_text.strip()
        except (KeyError, IndexError) as e:
            print(f"Ошибка при извлечении текста из ответа: {e}")
            print(f"Ответ API: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
            return ''

# Пример использования:
# oauth_token = os.environ.get('YANDEX_OAUTH_TOKEN')
# folder_id = os.environ.get('YANDEX_FOLDER_ID')
# iam_token = OCRService.get_iam_token(oauth_token)
# 
# ocr_service = OCRService(folder_id, iam_token)
# text = ocr_service.recognize_file('path/to/image.jpg')
# print(text)