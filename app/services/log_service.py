import logging
import os
import time
from datetime import datetime
from threading import Lock
from flask import session
from collections import deque

class LogService:
    """
    Сервис логирования процесса выполнения приложения
    """
    
    # Максимальное количество сообщений для хранения в памяти
    MAX_LOG_MESSAGES = 100
    
    # Singleton инстанс
    _instance = None
    _lock = Lock()
    
    # Буфер для хранения последних сообщений логов
    _log_buffer = deque(maxlen=MAX_LOG_MESSAGES)
    
    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(LogService, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance
    
    def _initialize(self):
        """Инициализация логгера"""
        self.logger = logging.getLogger('textbook_analyzer')
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        
        # Очистка существующих обработчиков, чтобы избежать дублирования
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Обработчик для консоли
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # Обработчик для файла
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(os.path.join(log_dir, 'app.log'), encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
        
        # Специальный обработчик для веб-интерфейса
        self.logger.addHandler(self._WebLogHandler())
    
    def info(self, message, session_id=None):
        """Логирование информационного сообщения"""
        self._log_message(message, 'INFO', session_id)
    
    def warning(self, message, session_id=None):
        """Логирование предупреждения"""
        self._log_message(message, 'WARNING', session_id)
    
    def error(self, message, session_id=None):
        """Логирование ошибки"""
        self._log_message(message, 'ERROR', session_id)
    
    def success(self, message, session_id=None):
        """Логирование успешного выполнения операции"""
        self._log_message(message, 'SUCCESS', session_id)
    
    def _log_message(self, message, level, session_id=None):
        """
        Обрабатывает сообщение и отправляет его во все обработчики логгера
        """
        # Определяем текущее время
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Стандартное логирование в консоль и файл
        if level == 'INFO':
            self.logger.info(message)
        elif level == 'WARNING':
            self.logger.warning(message)
        elif level == 'ERROR':
            self.logger.error(message)
        else:  # SUCCESS и другие нестандартные уровни
            self.logger.info(f"[{level}] {message}")
        
        # Добавляем сообщение в буфер для веб-интерфейса
        log_entry = {
            'timestamp': timestamp,
            'message': message,
            'level': level,
            'session_id': session_id
        }
        self._log_buffer.append(log_entry)
    
    def get_logs(self, session_id=None, limit=None):
        """
        Получить логи для отображения в веб-интерфейсе
        """
        if session_id:
            filtered_logs = [log for log in self._log_buffer if log.get('session_id') == session_id]
        else:
            filtered_logs = list(self._log_buffer)
        
        if limit and limit > 0:
            return filtered_logs[-limit:]
        return filtered_logs
    
    def clear_logs(self, session_id=None):
        """
        Очистка логов для указанной сессии или всех логов
        """
        if not session_id:
            self._log_buffer.clear()
        else:
            # Сохраняем только логи других сессий
            self._log_buffer = deque(
                [log for log in self._log_buffer if log.get('session_id') != session_id],
                maxlen=self.MAX_LOG_MESSAGES
            )
    
    class _WebLogHandler(logging.Handler):
        """
        Специальный обработчик для передачи логов в веб-интерфейс
        """
        def emit(self, record):
            # Нет необходимости что-либо делать здесь, так как буфер обновляется
            # непосредственно в методе _log_message класса LogService
            pass
