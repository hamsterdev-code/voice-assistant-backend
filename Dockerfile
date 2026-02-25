FROM python:3.12-slim

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Порт (платформы вроде Coolify/Railway передают PORT через env)
ENV PORT=8000
EXPOSE 8000

# Запуск (без --reload в продакшене)
CMD sh -c 'uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}'
