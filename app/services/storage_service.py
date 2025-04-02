import os
import json
from datetime import datetime

class StorageService:
    """Сервис для хранения и управления данными документов"""
    
    def __init__(self, storage_dir):
        """
        Инициализация сервиса хранения
        
        Args:
            storage_dir (str): Директория для хранения данных
        """
        self.storage_dir = storage_dir
        self.documents_dir = os.path.join(storage_dir, "documents")
        self.metadata_file = os.path.join(storage_dir, "metadata.json")
        
        # Создание директорий, если не существуют
        os.makedirs(self.documents_dir, exist_ok=True)
        
        # Инициализация метаданных
        if not os.path.exists(self.metadata_file):
            self._save_metadata({
                "documents": [],
                "last_updated": datetime.now().isoformat()
            })
    
    def save_document(self, document):
        """
        Сохранение документа
        
        Args:
            document: Документ для сохранения
            
        Returns:
            str: ID документа
        """
        # Сохранение содержимого документа в отдельный файл
        document_path = os.path.join(self.documents_dir, f"{document.id}.json")
        with open(document_path, 'w', encoding='utf-8') as f:
            json.dump(document.to_dict(), f, ensure_ascii=False, indent=2)
        
        # Обновление метаданных
        metadata = self._get_metadata()
        metadata["documents"].append({
            "id": document.id,
            "filename": document.filename,
            "created_at": document.created_at.isoformat()
        })
        metadata["last_updated"] = datetime.now().isoformat()
        self._save_metadata(metadata)
        
        return document.id
    
    def get_document(self, document_id):
        """
        Получение документа по ID
        
        Args:
            document_id (str): ID документа
            
        Returns:
            dict: Данные документа или None, если документ не найден
        """
        document_path = os.path.join(self.documents_dir, f"{document_id}.json")
        if not os.path.exists(document_path):
            return None
        
        with open(document_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def update_document(self, document_id, update_data):
        """
        Обновление данных документа
        
        Args:
            document_id (str): ID документа
            update_data (dict): Данные для обновления
            
        Returns:
            bool: True в случае успеха, False если документ не найден
        """
        document = self.get_document(document_id)
        if not document:
            return False
        
        # Обновление данных
        document.update(update_data)
        
        # Сохранение обновленных данных
        document_path = os.path.join(self.documents_dir, f"{document_id}.json")
        with open(document_path, 'w', encoding='utf-8') as f:
            json.dump(document, f, ensure_ascii=False, indent=2)
        
        return True
    
    def delete_document(self, document_id):
        """
        Удаление документа
        
        Args:
            document_id (str): ID документа
            
        Returns:
            bool: True в случае успеха, False если документ не найден
        """
        document_path = os.path.join(self.documents_dir, f"{document_id}.json")
        if not os.path.exists(document_path):
            return False
        
        # Удаление файла документа
        os.remove(document_path)
        
        # Обновление метаданных
        metadata = self._get_metadata()
        metadata["documents"] = [doc for doc in metadata["documents"] if doc["id"] != document_id]
        metadata["last_updated"] = datetime.now().isoformat()
        self._save_metadata(metadata)
        
        return True
    
    def get_all_documents(self):
        """
        Получение списка всех документов
        
        Returns:
            list: Список метаданных документов
        """
        metadata = self._get_metadata()
        return metadata["documents"]
    
    def _get_metadata(self):
        """
        Получение метаданных
        
        Returns:
            dict: Метаданные
        """
        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_metadata(self, metadata):
        """
        Сохранение метаданных
        
        Args:
            metadata (dict): Метаданные для сохранения
        """
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)