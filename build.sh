#!/usr/bin/env bash
# exit on error
set -o errexit

python -m pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

if [[ $DJANGO_SUPERUSER_PASSWORD ]]; then
  python manage.py createsuperuser --no-input || true
fi