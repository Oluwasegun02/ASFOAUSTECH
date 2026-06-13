#!/usr/bin/env bash
# exit on error
set -o errexit

python -m pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Create superuser only if environment variables are set and superuser doesn't exist
# This command will attempt to create a superuser and will fail if one already exists,
# but `|| true` will prevent the build from failing.
if [[ $DJANGO_SUPERUSER_PASSWORD ]]; then
  echo "Attempting to create superuser..."
  python manage.py createsuperuser --no-input || true
fi
