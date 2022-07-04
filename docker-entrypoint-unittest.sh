#!/bin/bash

# Apply database migrations
echo "Apply migrations"
python manage.py migrate --settings siteedit2.settings

# Start server
echo "Starting server"
python manage.py test --settings siteedit2.settings.tests