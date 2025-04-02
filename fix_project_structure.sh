#!/bin/bash

# Скрипт для исправления структуры проекта textbook-analyzer

echo "Начинаю исправление структуры проекта..."

# 1. Исправление имени файла _init_.py на __init__.py
if [ -f "app/_init_.py" ]; then
    echo "Исправляю имя файла _init_.py на __init__.py"
    mv "app/_init_.py" "app/__init__.py"
    echo "✅ Файл переименован"
else
    echo "⚠️ Файл app/_init_.py не найден"
fi

# 2. Исправление опечатки в имени файла ducument.py на document.py
if [ -f "app/models/ducument.py" ]; then
    echo "Исправляю опечатку в имени файла ducument.py на document.py"
    mv "app/models/ducument.py" "app/models/document.py"
    echo "✅ Файл переименован"
else
    echo "⚠️ Файл app/models/ducument.py не найден"
fi

# 3. Создание отсутствующих директорий
echo "Создаю отсутствующие директории..."

# Директория для тестов
if [ ! -d "tests" ]; then
    mkdir -p tests
    echo "✅ Создана директория tests/"
else
    echo "⚠️ Директория tests/ уже существует"
fi

# Директория для документации
if [ ! -d "docs" ]; then
    mkdir -p docs
    echo "✅ Создана директория docs/"
else
    echo "⚠️ Директория docs/ уже существует"
fi

# Поддиректории для статических файлов
if [ ! -d "app/static/css" ]; then
    mkdir -p app/static/css
    echo "✅ Создана директория app/static/css/"
else
    echo "⚠️ Директория app/static/css/ уже существует"
fi

if [ ! -d "app/static/js" ]; then
    mkdir -p app/static/js
    echo "✅ Создана директория app/static/js/"
else
    echo "⚠️ Директория app/static/js/ уже существует"
fi

if [ ! -d "app/static/img" ]; then
    mkdir -p app/static/img
    echo "✅ Создана директория app/static/img/"
else
    echo "⚠️ Директория app/static/img/ уже существует"
fi

# 4. Создание пустых файлов для инициализации модулей Python
touch tests/__init__.py
touch app/models/__init__.py
touch app/services/__init__.py

echo "Исправление структуры проекта завершено!"
echo "Пожалуйста, проверьте изменения и сделайте коммит."