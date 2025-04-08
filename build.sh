#!/usr/bin/env bash

echo ">>> Удаляем старую версию openai (вручную)..."
rm -rf ~/.cache/pip
pip uninstall -y openai

echo ">>> Устанавливаем openai 1.25.0 без кэша..."
pip install --no-cache-dir openai==1.25.0

echo ">>> Установка остальных зависимостей..."
pip install --no-cache-dir -r requirements.txt
