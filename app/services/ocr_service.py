import base64
import requests
import json
import os
from pathlib import Path
from typing import List, Dict, Any
import logging
from app.utils.token_manager import get_token

class OCRService:
    def __init__(self, folder_id: str, iam_token: str = None):
        """
        Инициализация сервиса OCR.
        
        Args:
            folder_id: Идентификатор каталога в Яндекс.Облаке
            iam_token: IAM-токен для аутентификации (опционально, если не указан, токен будет получен из менеджера токенов)
        """
        self.folder_id = folder_id
        self.iam_token = iam_token or get_token()  # Получаем токен из менеджера, если не передан
        self.vision_url = 'https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze'
        self.logger = logging.getLogger(__name__)
        
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
            error_message = f'Ошибка получения IAM-токена: {response.status_code} - {response.text}'
            logging.error(error_message)
            raise Exception(error_message)
    
    def refresh_token(self):
        """
        Обновляет IAM-токен через менеджер токенов
        """
        self.iam_token = get_token(force_refresh=True)
        self.logger.info("IAM-токен для OCR обновлен")
    
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
    
    def process_image(self, image_bytes: bytes) -> str:
        """
        Обрабатывает изображение для распознавания текста.
        
        Args:
            image_bytes: Байты изображения
            
        Returns:
            Распознанный текст
        """
        return self.recognize_bytes(image_bytes)
    
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
        elif response.status_code == 401:
            # Если 401 (Unauthorized), пробуем обновить токен и повторить запрос
            self.logger.warning("Токен истек. Пробуем обновить и повторить запрос")
            self.refresh_token()
            
            # Обновляем заголовки с новым токеном
            headers['Authorization'] = f'Bearer {self.iam_token}'
            
            # Повторяем запрос
            retry_response = requests.post(self.vision_url, headers=headers, json=body)
            
            if retry_response.status_code == 200:
                return self._extract_text_from_response(retry_response.json())
            else:
                error_msg = f'Ошибка распознавания после обновления токена: {retry_response.status_code} - {retry_response.text}'
                self.logger.error(error_msg)
                return error_msg
        else:
            error_msg = f'Ошибка распознавания: {response.status_code} - {response.text}'
            self.logger.error(error_msg)
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
            error_msg = f"Ошибка при извлечении текста из ответа: {e}"
            self.logger.error(error_msg)
            self.logger.debug(f"Ответ API: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
            return ''