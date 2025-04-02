import requests

class GPTService:
    """Сервис для работы с YandexGPT"""
    
    def __init__(self, gpt_url, folder_id, iam_token, model_uri):
        """
        Инициализация сервиса GPT
        
        Args:
            gpt_url (str): URL API YandexGPT
            folder_id (str): Идентификатор каталога в Yandex Cloud
            iam_token (str): IAM-токен для авторизации
            model_uri (str): URI модели YandexGPT
        """
        self.gpt_url = gpt_url
        self.folder_id = folder_id
        self.model_uri = model_uri
        self.headers = {
            "Authorization": f"Bearer {iam_token}",
            "Content-Type": "application/json",
            "x-folder-id": folder_id
        }
    
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
        """Отправка запроса к API YandexGPT"""
        response = requests.post(self.gpt_url, headers=self.headers, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"Ошибка при обращении к YandexGPT: {response.text}")
        
        result = response.json()
        return result["result"]["alternatives"][0]["message"]["text"]