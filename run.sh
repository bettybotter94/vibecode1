#!/bin/bash

# Скрипт для запуска сервиса

echo "Установка зависимостей..."
pip install -r requirements.txt

echo "Запуск сервиса..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000

