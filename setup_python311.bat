echo Проверка наличия Python 3.11...
where python3.11 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python 3.11 не найден! Пожалуйста, установите его с сайта python.org
    exit /b 1
)

echo Создание нового виртуального окружения с Python 3.11...
python3.11 -m venv venv_py311

echo Активация нового окружения...
call venv_py311\Scripts\activate.bat

echo Установка зависимостей...
pip install -r requirements.txt

echo Запуск проекта...
python run.py