import uuid
from datetime import datetime

class Document:
    """Модель документа для хранения информации об учебном материале"""
    
    def __init__(self, filename, content, file_path=None):
        """
        Инициализация документа
        
        Args:
            filename (str): Имя файла
            content (str): Распознанный текст документа
            file_path (str, optional): Путь к файлу на диске
        """
        self.id = str(uuid.uuid4())
        self.filename = filename
        self.content = content
        self.file_path = file_path
        self.created_at = datetime.now()
        self.analysis_history = []
    
    def add_analysis(self, question=None, answer=None, explanation=None):
        """
        Добавление результата анализа
        
        Args:
            question (str, optional): Заданный вопрос
            answer (str, optional): Полученный ответ
            explanation (str, optional): Объяснение материала
        """
        analysis = {
            "timestamp": datetime.now(),
            "type": "question" if question else "explanation",
            "question": question,
            "answer": answer,
            "explanation": explanation
        }
        
        self.analysis_history.append(analysis)
        return analysis
    
    def to_dict(self):
        """
        Преобразование документа в словарь
        
        Returns:
            dict: Словарь с данными документа
        """
        return {
            "id": self.id,
            "filename": self.filename,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "analysis_history": self.analysis_history
        }