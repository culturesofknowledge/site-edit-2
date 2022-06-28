#!/bin/bash

# Make migrations
echo "Load upload status"
python manage.py create_upload_status --settings siteedit2.settings

# Make migrations
echo "Load ISO639"
python manage.py create_iso639 --settings siteedit2.settings

# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000 --settings siteedit2.settings