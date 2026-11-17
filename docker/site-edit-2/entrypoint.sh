#!/bin/bash
# Stop if any step fails, so the server never starts on a database that failed to migrate
set -e
# Create migrations yourself with `python manage.py makemigrations` and commit them
echo "Migrating"
python manage.py migrate
# Create cache table
echo "Creating cache table"
python manage.py createcachetable
echo "add/update permissions"
python manage.py add_groups_and_permissions
echo "Starting server ..."
python -u manage.py runserver 0.0.0.0:8000
