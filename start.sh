#!/bin/bash

echo "🚀 Запуск Voice Assistant Backend"
echo ""

# Переходим в директорию backend
cd "$(dirname "$0")"

# Проверяем виртуальное окружение
if [ ! -d "venv" ]; then
    echo "📦 Создаём виртуальное окружение..."
    python3 -m venv venv
fi

# Активируем виртуальное окружение
echo "🔧 Активируем виртуальное окружение..."
source venv/bin/activate

# Устанавливаем зависимости
echo "📥 Устанавливаем зависимости..."
pip install -r requirements.txt --quiet

echo ""
echo "✨ Всё готово! Запускаем сервер..."
echo ""
echo "📍 Backend будет доступен на: http://localhost:8000"
echo "📍 Health check: http://localhost:8000/health"
echo "💾 База данных: SQLite (voice_assistant.db)"
echo ""
echo "Для остановки нажмите Ctrl+C"
echo ""
echo "─────────────────────────────────────────────────────────"
echo ""

# Запускаем сервер
python main.py
