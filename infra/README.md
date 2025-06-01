# 🍳 Foodgram - продуктовый помощник

## 🚀 Быстрый старт

1. **Установка Docker**:
```bash
sudo apt update && sudo apt install docker.io docker-compose -y
sudo usermod -aG docker $USER && newgrp docker
```

2. **Запуск проекта**:
```bash
git clone https://github.com/gosheno/foodgram-st.git
cd foodgram-st/infra
cp .env_example .env
nano .env  # заполните настройки
docker-compose up -d --build
```

3. **Доступ**:
- Сайт: `http://ваш-сервер`
- Админка: `http://ваш-сервер/admin`

## 🔧 Технологии
- Django + React
- PostgreSQL + Nginx
- Docker

**Автор backend-части**: Гоша  
**Год разработки**: 2025  

📂 **Исходный код**: [GitHub Repository](https://github.com/gosheno/foodgram-st)  
📨 **Telegram**: [@goshenou](https://t.me/goshenou)

[![Telegram](https://img.shields.io/badge/-Telegram-26A5E4?style=flat&logo=telegram&logoColor=white)](https://t.me/goshenou)
[![GitHub](https://img.shields.io/badge/-GitHub-181717?style=flat&logo=github)](https://github.com/gosheno)