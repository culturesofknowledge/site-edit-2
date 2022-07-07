#!/bin/bash

# Order of apps matters, uploader first as table there is referenced by other apps
apps=('uploader' 'institution' 'location' 'login' 'manifestation' 'person' 'work')

for app in "${apps[@]}"
do
  echo "Making migrations for $app"
  python manage.py makemigrations $app --settings siteedit2.settings
done

# Make migrations
echo "Migrating"
python manage.py migrate --settings siteedit2.settings

# Make migrations
echo "Load upload status"
python manage.py create_upload_status --settings siteedit2.settings

# Make migrations
echo "Load ISO639"
python manage.py create_iso639 --settings siteedit2.settings

# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000 --settings siteedit2.settings