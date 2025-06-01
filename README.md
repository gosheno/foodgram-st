# Проект Foodgram
![example workflow](https://github.com/NIK-TIGER-BILL/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)  
  
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)


Foodgram - продуктовый помощник с базой кулинарных рецептов. Позволяет публиковать рецепты, сохранять избранные, а также формировать список покупок для выбранных рецептов. Можно подписываться на любимых авторов.


### Запуск проекта:

- Клонировать репозиторий:
```link
https://github.com/gosheno/foodgram-st.git
```

- В директории infra создать файл .env и заполнить своими данными по аналогии с .env_example:
```
# Файл .env
POSTGRES_USER=django_user
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432

DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=secretpassword
DJANGO_SUPERUSER_EMAIL=admin@example.com
SECRET_KEY='секретный ключ Django'
```
Запустить проект
```
docker-compose up --build
```
При первом запуске стоит проинициализировать базу данных
в отдельной консоли:

```
docker-compose exec backend ch ./init.sh
```
при этом выполнится скрипт внутри бэкенд контейнера 
```
#!/bin/bash
set -e

python manage.py migrate
python manage.py load_ingredients
python manage.py loaddata db
python manage.py createsuperuser --noinput

```
*данные супер пользователя берутся из соответсвующих полей .env файла*


- После запуска проект будут доступен по адресу: [http://localhost/](http://localhost/)


- Документация будет доступна по адресу: [http://localhost/api/docs/](http://localhost/api/docs/)


### Автор backend'а:

гоша (c) 2025

p.s у меня так и не получилось подключить страницы о проекте и технологии во фронте они просто не открываются 404
я буду очень рад если скажете как это сделать ибо просто раскомментировать не получилось
