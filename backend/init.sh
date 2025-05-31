#!/bin/bash
set -e

python manage.py migrate
python manage.py load_ingredients
python manage.py loaddata db
python manage.py createsuperuser --noinput
