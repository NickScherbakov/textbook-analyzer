#!/usr/bin/env python3
import os
import sys
import argparse
from git import Repo, GitCommandError

def commit_changes(message=None):
    """
    Создает коммит всех изменений в текущем состоянии проекта
    
    Args:
        message: Сообщение коммита (опционально)
    """
    try:
        # Находим корень репозитория (текущая директория или родительская)
        repo_path = os.path.dirname(os.path.abspath(__file__))
        repo = Repo(repo_path)
        
        # Проверяем, есть ли изменения для коммита
        if not repo.is_dirty(untracked_files=True):
            print("Нет изменений для коммита.")
            return False
        
        # Добавляем все изменения в индекс
        repo.git.add(A=True)
        
        # Используем сообщение по умолчанию, если не указано
        if not message:
            message = "Сохранение текущего состояния проекта"
        
        # Создаем коммит
        repo.git.commit(m=message)
        print(f"Коммит успешно создан: {message}")
        
        return True
    except GitCommandError as e:
        print(f"Ошибка Git: {str(e)}")
        return False
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Создает коммит всех изменений в проекте")
    parser.add_argument("-m", "--message", help="Сообщение коммита")
    args = parser.parse_args()
    
    commit_changes(args.message)
