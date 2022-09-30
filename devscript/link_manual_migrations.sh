#! /bin/bash

if [ ! -f "manage.py" ]; then
  echo "Exit. this script should be run in project home."
  exit 99
fi

cd person/migrations
ln -sf ../manual_migrations/0*

cd ../../

cd uploader/migrations
ln -sf ../manual_migrations/0*
