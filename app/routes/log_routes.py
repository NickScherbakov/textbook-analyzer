from flask import Blueprint, request, jsonify, session
from app.services.log_service import LogService

# Создаем Blueprint для маршрутов логирования
log_bp = Blueprint('logs', __name__, url_prefix='/api/logs')

# Получаем экземпляр сервиса логирования
log_service = LogService()

@log_bp.route('', methods=['GET'])
def get_logs():
    """
    Получить логи для текущей сессии
    
    Query Parameters:
        limit (int): Максимальное количество логов для возврата
        level (str): Фильтровать логи по уровню
        
    Returns:
        JSON с массивом логов
    """
    session_id = session.get('session_id')
    limit = request.args.get('limit', 50, type=int)
    level = request.args.get('level')
    
    logs = log_service.get_logs(session_id=session_id, limit=limit)
    
    # Фильтрация по уровню, если указан
    if level:
        logs = [log for log in logs if log.get('level').lower() == level.lower()]
    
    log_service.info(f'Запрошены логи (limit={limit}, level={level})', session_id)
    return jsonify({'logs': logs, 'count': len(logs)})

@log_bp.route('/all', methods=['GET'])
def get_all_logs():
    """
    Получить все логи (требует административных прав)
    """
    # Здесь можно добавить проверку прав администратора
    session_id = session.get('session_id')
    limit = request.args.get('limit', 100, type=int)
    level = request.args.get('level')
    
    logs = log_service.get_logs(limit=limit)
    
    # Фильтрация по уровню
    if level:
        logs = [log for log in logs if log.get('level').lower() == level.lower()]
    
    log_service.info(f'Администратор запросил все логи (limit={limit}, level={level})', session_id)
    return jsonify({'logs': logs, 'count': len(logs)})

@log_bp.route('/clear', methods=['POST'])
def clear_logs():
    """
    Очистить логи для текущей сессии
    """
    session_id = session.get('session_id')
    log_service.info('Запрос на очистку логов', session_id)
    log_service.clear_logs(session_id=session_id)
    return jsonify({'status': 'success', 'message': 'Логи успешно очищены'})

# Только для административных целей
@log_bp.route('/clear/all', methods=['POST'])
def clear_all_logs():
    """
    Очистить все логи (требует административных прав)
    """
    session_id = session.get('session_id')
    log_service.info('Запрос на очистку всех логов от администратора', session_id)
    log_service.clear_logs()  # Очистить все логи
    return jsonify({'status': 'success', 'message': 'Все логи успешно очищены'})
