#!/bin/bash
echo "Making migrations"
python manage.py makemigrations
# Make migrations
echo "Migrating"
python manage.py migrate
# Create cache table
echo "Creating cache table"
python manage.py createcachetable
python -u manage.py runserver 0.0.0.0:8000
