#!/bin/bash

DJANGO_SETTINGS_MODULE=siteedit2.settings.tests

# Start server
echo "Starting server"
python manage.py test --noinput --keepdb