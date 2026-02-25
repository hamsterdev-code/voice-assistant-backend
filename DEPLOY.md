# Деплой Voice Assistant Backend

## Dockerfile

Проект содержит `Dockerfile` для сборки. Платформа (Coolify и др.) должна использовать его.

## Порт

Приложение слушает порт **8000** (или `PORT` из env). В настройках деплоя укажи:
- **Port:** 8000

## ERR_TIMED_OUT — что проверить

Если сайт не открывается (таймаут):

1. **Порт в настройках домена** — в Coolify: Destination → Domain → Port = 8000
2. **Firewall** — порты 80/443 и проброс до контейнера
3. **Пересборка** — после изменений в Dockerfile сделай полный rebuild

## CORS

Production-домен уже добавлен в `config/settings.py`. Для нового домена добавь его в `allowed_origins`.
