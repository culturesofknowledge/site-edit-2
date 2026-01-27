#!/bin/bash
echo "Making migrations"
python manage.py makemigrations
# Make migrations
echo "Migrating"
python manage.py migrate
# Create cache table
echo "Creating cache table"
python manage.py createcachetable
echo "add/update permissions"
python manage.py add_groups_and_permissions
echo "Starting server ..."
python -u manage.py runserver 0.0.0.0:8000
