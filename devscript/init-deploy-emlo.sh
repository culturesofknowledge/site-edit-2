#! /bin/bash

#########
# auto init and deploy emlo-edit for first time
# script also for testing deployment procedure
# 
# assume following command is already installed in system:
# * git
# * docker-compose
#######

set -x
set -e 

branch="${1:-main}"

git clone https://github.com/culturesofknowledge/site-edit-2
cd site-edit-2
git checkout "$branch"
git submodule update --init --recursive

cd siteedit2/settings
cp gunweb.py.example gunweb.py

orgline1a="ALLOWED_HOSTS\s*=\s*\[\s*'192.168.56.10'\s*\]"
orgline1b="ALLOWED_HOSTS = ['192.168.56.10', 'localhost', '127.0.0.1']"
sed -i "s/$orgline1a/$orgline1b/g" gunweb.py
orgline1a="CSRF_TRUSTED_ORIGINS\s*=\s*\[\s*'http://192.168.56.10',\s*\]"
orgline1b="CSRF_TRUSTED_ORIGINS = ['http://192.168.56.10', 'http://localhost', 'http://127.0.0.1']"
sed -i "s|$orgline1a|$orgline1b|g" gunweb.py

cd ../../docker/site-edit-2/
cp gunweb.env.example .gunweb.env

ln -sf .gunweb.env .env    # .env for `db` service
# edit variable in .gunweb.env if needed
# vi .gunweb.env


# run testing
docker-compose -f docker-compose.yml -f docker-compose-dev.yml up --build pycharm-py
docker-compose -f docker-compose.yml -f docker-compose-dev.yml down


# run docker 
docker-compose -f docker-compose.yml -f docker-compose-gunweb.yml up -d --build db gunicorn_web nginx
# -d for run in background 
# --build to build docker every time 

# create account for testing
echo "Define password to create account admina:"
docker exec -it site-edit-2_gunicorn_web_1 python3 manage.py createsuperuser --username admina

# wait few second, use curl or browser to test server is up
curl -L 'http://localhost:8010/'








