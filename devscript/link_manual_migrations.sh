#! /bin/bash

if [ ! -f "manage.py" ]; then
  echo "Exit. this script should be run in project home."
  exit 99
fi

cd person/migrations
ln -vsf ../manual_migrations/0*.py

cd ../../
cd uploader/migrations
ln -vsf ../manual_migrations/0*.py

cd ../../
cd work/migrations
ln -vsf ../manual_migrations/0*.py
