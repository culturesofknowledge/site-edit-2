#!/bin/bash

DJANGO_SETTINGS_MODULE=siteedit2.settings.test

# Apply database migrations
echo "Apply migrations"
python manage.py migrate

# Start server
echo "Starting server"
python manage.py test