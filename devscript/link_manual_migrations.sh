#! /bin/bash

if [ ! -f "manage.py" ]; then
  echo "Exit. this script should be run in project home."
  exit 99
fi


ln -vsfr person/manual_migrations/0*.py person/migrations/
ln -vsfr uploader/manual_migrations/0*.py uploader/migrations/
ln -vsfr work/manual_migrations/0*.py work/migrations/
ln -vsfr manifestation/manual_migrations/0*.py manifestation/migrations/
ln -vsfr audit/manual_migrations/0*.py audit/migrations/
ln -vsfr location/manual_migrations/0*.py location/migrations/
ln -vsfr core/manual_migrations/0*.py core/migrations/
