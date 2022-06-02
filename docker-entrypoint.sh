#!/bin/bash

# Make migrations
echo "Make migrations for data"
python manage.py makemigrations uploader --settings siteedit2.settings

# Make migrations
echo "Make migrations for data"
python manage.py makemigrations --settings siteedit2.settings

# Apply database migrations
echo "Apply migrations"
python manage.py migrate --settings siteedit2.settings

# Load test data
# echo "Load test data"
# python manage.py load_test_data --settings pstf.settings.base

# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000 --settings siteedit2.settings