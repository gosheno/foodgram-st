# 🍳 Foodgram - продуктовый помощник

[![CI/CD](https://github.com/yourusername/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)](https://github.com/yourusername/foodgram-project-react/actions)
[![Docker](https://img.shields.io/badge/Docker-✔-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)

## 🚀 Развертывание на сервере

### 1. Подготовка сервера


**Установка необходимых компонентов:**

```bash
# Обновление пакетов
sudo apt update && sudo apt upgrade -y

# Установка Docker
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Настройка проекта

**Клонирование репозитория:**
```bash
git clone https://github.com/gosheno/foodgram-st.git
cd foodgram-st/infra
```

**Настройка окружения:**
```bash
cp .env_example .env
nano .env  # Редактируем параметры
```

Пример содержимого `.env`:
```ini
# PostgreSQL
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=your_strong_password

# Django
SECRET_KEY='your-secret-key-here'
DEBUG=False
ALLOWED_HOSTS=your-server-ip,localhost,127.0.0.1

# Superuser
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=admin_password
DJANGO_SUPERUSER_EMAIL=admin@example.com
```

### 3. Запуск проекта

**Сборка и запуск контейнеров:**
```bash
docker-compose up -d --build
```

**Инициализация базы данных:**
```bash
# Даем время контейнерам запуститься
sleep 10

# Применяем миграции, создаем суперпользователя
docker-compose exec backend python manage.py init.sh
```

### 4. Доступ к проекту

После успешного развертывания:
- Основное приложение: `http://ваш-сервер`
- API документация: `http://ваш-сервер/api/docs/`
- Админ-панель: `http://ваш-сервер/admin/`

### 5. Полезные команды

**Обновление проекта:**
```bash
docker-compose down
git pull origin main
docker-compose up -d --build
```

**Просмотр логов:**
```bash
docker-compose logs -f  # все логи
docker-compose logs -f backend  # логи бэкенда
```


## 🛠 Технологический стек

- **Backend**: Django + DRF
- **Frontend**: React
- **База данных**: PostgreSQL
- **Кэширование**: Redis
- **Веб-сервер**: Nginx
- **Контейнеризация**: Docker + Docker Compose

## 📄 Лицензия

MIT License. Подробнее см. в файле LICENSE.