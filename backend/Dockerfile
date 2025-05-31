FROM python:3.10
WORKDIR /app

RUN pip install gunicorn==20.1.0
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .

RUN chmod +x /app/init.sh
CMD ["/bin/sh", "-c", "python manage.py collectstatic --noinput \
    && exec gunicorn --bind 0.0.0.0:8000 --workers 3 foodgram_api.wsgi"]