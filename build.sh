#!/usr/bin/env bash

echo ">>> Очистка старых пакетов..."
pip uninstall -y openai

echo ">>> Установка зависимостей..."
pip install --no-cache-dir -r requirements.txt
