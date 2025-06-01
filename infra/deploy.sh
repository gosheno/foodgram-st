#!/bin/bash

# 1. Получаем последние образы
docker-compose pull

# 2. Останавливаем текущие контейнеры
docker-compose down

# 3. Запускаем новые версии
docker-compose up -d

# 4. Очищаем старые образы
docker system prune -af

# 5. Применяем миграции (если нужно)
docker-compose exec backend python manage.py migrate

# 6. Собираем статику
docker-compose exec backend python manage.py collectstatic --noinput