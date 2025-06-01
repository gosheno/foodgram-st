# 🍳 Foodgram - Ваш кулинарный цифровой помощник  
![example workflow](https://github.com/NIK-TIGER-BILL/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)  

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django 4.2](https://img.shields.io/badge/Django-4.2-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.14-9F1D20?logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7.0-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-24.0-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![CI/CD](https://img.shields.io/badge/GitHub_Actions-✔-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)

## 🌟 О проекте

**Foodgram** — это интуитивно понятный сервис для всех любителей кулинарии, который позволяет:

- 📖 Создавать и публиковать рецепты с пошаговыми инструкциями  
- ❤️ Сохранять любимые рецепты в избранное  
- 🛒 Формировать умный список покупок для выбранных блюд  
- 👨‍🍳 Подписываться на любимых авторов  
- 🏷️ Искать рецепты по тегам и ингредиентам  

## 🚀 Технологический стек

| Компонент       | Технологии                          |
|-----------------|-------------------------------------|
| **Backend**     | Django + Django REST Framework      |
| **Frontend**    | React                               |
| **База данных** | PostgreSQL                          |
| **Кэширование** | Redis                               |
| **Сервер**      | Nginx + Gunicorn                    |
| **Инфраструктура** | Docker + Docker Compose         |
| **CI/CD**       | GitHub Actions                      |

## 🛠️ Быстрый старт

### 1. Клонирование репозитория
```bash
git clone https://github.com/gosheno/foodgram-st.git
cd foodgram-st/infra
```

### 2. Настройка окружения
Создайте `.env` файл на основе примера:
```bash
cp .env_example .env
nano .env  # Редактируем параметры
```

### 3. Запуск проекта
```bash
docker-compose up -d --build
```

### 4. Инициализация БД
```bash
docker-compose exec backend ./init.sh
```
*Скрипт автоматически:*
- Применяет миграции
- Загружает ингредиенты
- Создает суперпользователя (данные берутся из `.env`)

### 5. Доступ к сервису
- Основное приложение: [http://localhost](http://localhost)  
- API документация: [http://localhost/api/docs/](http://localhost/api/docs/)  
- Админ-панель: [http://localhost/admin/](http://localhost/admin/)  

## 🚀 Процесс деплоя

Проект использует автоматизированный пайплайн деплоя через GitHub Actions:

1. **При пуше в ветку `main`**:
   - Собираются Docker-образы для backend и frontend
   - Образы загружаются в Docker Hub
   - Происходит автоматический деплой на production-сервер

2. **На сервере**:
   - Обновляются образы из Docker Hub
   - Перезапускаются контейнеры без downtime
   - Применяются миграции (если есть)
   - Собирается статика

3. **Требования к серверу**:
   - Установленные Docker и Docker Compose
   - Настроенные переменные окружения
   - Доступ по SSH с GitHub Actions

## 🎯 Особенности реализации

### Backend
- Кастомная djoser-аутентификация  
- Оптимизированные запросы к БД (prefetch_related, select_related)  
- Кэширование с Redis  
- Документация API (Redoc)  

### Infrastructure
- Полностью контейнеризированное решение  
- Автоматическое развертывание через CI/CD  
- Готовые скрипты инициализации  
- Раздельные volumes для данных:
  - PostgreSQL
  - Redis
  - Статические файлы
  - Медиа-файлы


**Автор backend-части**: Гоша  
**Год разработки**: 2025  

📂 **Исходный код**: [GitHub Repository](https://github.com/gosheno/foodgram-st)  
📨 **Telegram**: [@goshenou](https://t.me/goshenou)

[![Telegram](https://img.shields.io/badge/-Telegram-26A5E4?style=flat&logo=telegram&logoColor=white)](https://t.me/goshenou)
[![GitHub](https://img.shields.io/badge/-GitHub-181717?style=flat&logo=github)](https://github.com/gosheno)
