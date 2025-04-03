import os
import requests
import json
from datetime import datetime, timedelta
import logging

class TokenManager:
    """Менеджер токенов для Yandex Cloud API"""
    
    def __init__(self):
        self.iam_token = None
        self.token_expires_at = None
        self.oauth_token = os.environ.get('YANDEX_OAUTH_TOKEN')
        self.logger = logging.getLogger(__name__)
    
    def get_iam_token(self, force_refresh=False):
        """
        Получение или обновление IAM-токена
        
        Args:
            force_refresh: Принудительное обновление токена
            
        Returns:
            str: Действующий IAM-токен
        """
        # Проверяем, нужно ли обновить токен
        if force_refresh or self.token_needs_refresh():
            self.refresh_iam_token()
        
        return self.iam_token
    
    def token_needs_refresh(self):
        """
        Проверяет, нужно ли обновить токен
        
        Returns:
            bool: True, если токен отсутствует или истекает в ближайшие 5 минут
        """
        if not self.iam_token or not self.token_expires_at:
            return True
        
        # Обновляем токен за 5 минут до истечения срока его действия
        return datetime.now() + timedelta(minutes=5) >= self.token_expires_at
    
    def refresh_iam_token(self):
        """
        Обновляет IAM-токен, используя OAuth-токен
        
        Raises:
            Exception: Если не удалось получить новый IAM-токен
        """
        if not self.oauth_token:
            self.logger.error("OAuth-токен не установлен. Необходимо установить YANDEX_OAUTH_TOKEN в переменных окружения.")
            raise ValueError("OAuth-токен не установлен. Установите YANDEX_OAUTH_TOKEN в переменных окружения.")
        
        url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
        
        try:
            response = requests.post(
                url,
                json={'yandexPassportOauthToken': self.oauth_token}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.iam_token = data.get('iamToken')
                
                # Устанавливаем время истечения срока действия токена
                # Обычно IAM токены действуют 12 часов
                expires_at = data.get('expiresAt')
                if expires_at:
                    # Конвертируем строку в datetime
                    self.token_expires_at = datetime.strptime(
                        expires_at.replace('Z', '+0000'),
                        '%Y-%m-%dT%H:%M:%S%z'
                    ).replace(tzinfo=None)
                else:
                    # Если срок действия не указан, устанавливаем 11 часов
                    self.token_expires_at = datetime.now() + timedelta(hours=11)
                
                self.logger.info(f"IAM токен успешно обновлен. Действителен до: {self.token_expires_at}")
            else:
                self.logger.error(f"Ошибка получения IAM-токена: {response.status_code} - {response.text}")
                raise Exception(f"Ошибка получения IAM-токена: {response.status_code} - {response.text}")
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении IAM токена: {str(e)}")
            raise

# Создаем singleton-экземпляр менеджера токенов
token_manager = TokenManager()

def get_token(force_refresh=False):
    """
    Получение IAM-токена
    
    Args:
        force_refresh: Принудительное обновление токена
        
    Returns:
        str: Действующий IAM-токен
    """
    return token_manager.get_iam_token(force_refresh)