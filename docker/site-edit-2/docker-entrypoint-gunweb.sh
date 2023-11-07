#!/bin/bash


test -d $EMLO_APP_HOME || mkdir -p $EMLO_APP_HOME


# Name of the application
NAME="siteedit2"

# Django project directory
DJANGODIR=/code

# we will communicte using this unix socket
#SOCKFILE=$EMLO_APP_HOME/gunicorn.sock
GUN_BIND=0.0.0.0:8000

# the user to run as
USER=root

# the group to run as
GROUP=root


# WSGI module name
DJANGO_WSGI_MODULE=siteedit2.wsgi

echo "Starting $NAME as `whoami`"
# Activate the virtual environment

# should be export by .gunweb.env
# export DJANGO_SETTINGS_MODULE=siteedit2.settings.gunweb

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR


cd $DJANGODIR

python3 manage.py compilescss
python3 manage.py collectstatic -c --no-input


echo "Making migrations"
python manage.py makemigrations

# Make migrations
echo "Migrating"
python manage.py migrate

# Start server
echo "Starting server"

# ~/venv/emlo/bin/gunicorn siteedit2.wsgi:application --bind 0.0.0.0:8000

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)

        # --bind=unix:$SOCKFILE \
gunicorn ${DJANGO_WSGI_MODULE}:application \
        --name $NAME \
        --workers ${GUN_NUM_WORKERS:-4} \
        --user=$USER --group=$GROUP \
        --bind=$GUN_BIND \
        --log-level=debug \
        --log-file=-


