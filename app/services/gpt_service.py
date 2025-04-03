import requests
import logging
from app.utils.token_manager import get_token

class GPTService:
    """Сервис для работы с YandexGPT"""
    
    def __init__(self, gpt_url, folder_id, iam_token=None, model_uri=None):
        """
        Инициализация сервиса GPT
        
        Args:
            gpt_url (str): URL API YandexGPT
            folder_id (str): Идентификатор каталога в Yandex Cloud
            iam_token (str, optional): IAM-токен для авторизации. Если None, будет получен через token_manager
            model_uri (str, optional): URI модели YandexGPT. Если None, будет создан на основе folder_id
        """
        self.gpt_url = gpt_url
        self.folder_id = folder_id
        self.iam_token = iam_token or get_token()
        self.model_uri = model_uri or f"gpt://{folder_id}/yandexgpt-lite"
        self.headers = {
            "Authorization": f"Bearer {self.iam_token}",
            "Content-Type": "application/json",
            "x-folder-id": folder_id
        }
        self.logger = logging.getLogger(__name__)
    
    def refresh_token(self):
        """Обновляет IAM-токен через менеджер токенов"""
        self.iam_token = get_token(force_refresh=True)
        self.headers["Authorization"] = f"Bearer {self.iam_token}"
        self.logger.info("IAM-токен для GPT обновлен")
    
    def explain_content(self, content, instruction="Объясни этот учебный материал простыми словами"):
        """
        Генерация объяснения учебного материала
        
        Args:
            content (str): Текст учебного материала
            instruction (str): Инструкция для модели
            
        Returns:
            str: Объяснение материала
        """
        prompt = f"{instruction}:\n\n{content}"
        
        payload = {
            "modelUri": self.model_uri,
            "completionOptions": {
                "stream": False,
                "temperature": 0.6,
                "maxTokens": 2000
            },
            "messages": [
                {
                    "role": "system",
                    "text": "Ты - репетитор, который помогает студентам понять сложный учебный материал. " +
                            "Объясняй понятно, структурированно и с примерами."
                },
                {
                    "role": "user",
                    "text": prompt
                }
            ]
        }
        
        return self._send_request(payload)
    
    def answer_question(self, content, question):
        """
        Ответ на вопрос по учебному материалу
        
        Args:
            content (str): Текст учебного материала
            question (str): Вопрос
            
        Returns:
            str: Ответ на вопрос
        """
        prompt = f"Ответь на вопрос на основе этого учебного материала:\n\nМатериал: {content}\n\nВопрос: {question}"
        
        payload = {
            "modelUri": self.model_uri,
            "completionOptions": {
                "stream": False,
                "temperature": 0.3,
                "maxTokens": 1500
            },
            "messages": [
                {
                    "role": "system",
                    "text": "Ты - помощник по учебным материалам. Отвечай на вопросы точно, основываясь только на предоставленной информации."
                },
                {
                    "role": "user",
                    "text": prompt
                }
            ]
        }
        
        return self._send_request(payload)
    
    def generate_examples(self, content, topic):
        """
        Генерация дополнительных примеров по теме
        
        Args:
            content (str): Текст учебного материала
            topic (str): Тема для генерации примеров
            
        Returns:
            str: Дополнительные примеры
        """
        prompt = f"Сгенерируй практические примеры по теме на основе учебного материала:\n\nМатериал: {content}\n\nТема: {topic}"
        
        payload = {
            "modelUri": self.model_uri,
            "completionOptions": {
                "stream": False,
                "temperature": 0.7,
                "maxTokens": 1500
            },
            "messages": [
                {
                    "role": "system",
                    "text": "Ты - опытный преподаватель. Создавай практические примеры, которые помогут лучше понять и запомнить материал."
                },
                {
                    "role": "user",
                    "text": prompt
                }
            ]
        }
        
        return self._send_request(payload)
    
    def _send_request(self, payload):
        """Отправка запроса к API YandexGPT с автоматическим обновлением токена при необходимости"""
        try:
            response = requests.post(self.gpt_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                return result["result"]["alternatives"][0]["message"]["text"]
            elif response.status_code == 401:
                # Если 401 (неавторизован), обновляем токен и повторяем запрос
                self.logger.warning("Токен для GPT истек. Обновление...")
                self.refresh_token()
                
                # Повторяем запрос с новым токеном
                retry_response = requests.post(self.gpt_url, headers=self.headers, json=payload)
                
                if retry_response.status_code == 200:
                    result = retry_response.json()
                    return result["result"]["alternatives"][0]["message"]["text"]
                else:
                    error_msg = f"Ошибка при обращении к YandexGPT после обновления токена: {retry_response.status_code} - {retry_response.text}"
                    self.logger.error(error_msg)
                    raise Exception(error_msg)
            else:
                error_msg = f"Ошибка при обращении к YandexGPT: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
        except Exception as e:
            self.logger.error(f"Ошибка при отправке запроса к YandexGPT: {str(e)}")
            raise