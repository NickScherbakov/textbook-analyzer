/**
 * Основной JavaScript файл приложения
 */

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всплывающих подсказок (Bootstrap Tooltips)
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Drag and drop функциональность для загрузки файлов
    setupDragAndDrop();
});

/**
 * Настройка drag and drop функциональности для загрузки файлов
 */
function setupDragAndDrop() {
    const uploadArea = document.querySelector('.upload-area');
    const fileInput = document.getElementById('imageInput');
    
    if (!uploadArea || !fileInput) return;
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        uploadArea.classList.add('bg-light');
        uploadArea.style.borderColor = '#0d6efd';
    }
    
    function unhighlight() {
        uploadArea.classList.remove('bg-light');
        uploadArea.style.borderColor = '';
    }
    
    uploadArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            fileInput.files = files;
            // Опционально - автоматическая отправка формы после выбора файла
            // document.getElementById('uploadForm').dispatchEvent(new Event('submit'));
        }
    }
}

/**
 * Функция для обработки ошибок запросов
 * @param {Response} response - Ответ от сервера
 * @returns {Promise} - Промис с данными или ошибкой
 */
async function handleResponse(response) {
    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `HTTP error! status: ${response.status}`);
    }
    return response.json();
}

/**
 * Показать уведомление
 * @param {string} message - Текст сообщения
 * @param {string} type - Тип уведомления (success, danger, warning)
 */
function showNotification(message, type = 'success') {
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Автоматическое скрытие через 5 секунд
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    }, 5000);
}