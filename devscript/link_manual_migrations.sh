#! /bin/bash

if [ ! -f "manage.py" ]; then
  echo "Exit. this script should be run in project home."
  exit 99
fi


ln -vsfr person/manual_migrations/0*.py person/migrations/
ln -vsfr uploader/manual_migrations/0*.py uploader/migrations/
ln -vsfr work/manual_migrations/0*.py work/migrations/
ln -vsfr manifestation/manual_migrations/0*.py manifestation/migrations/
