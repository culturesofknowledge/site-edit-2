last update date: 2023-11-06


Pre-condition
----------------------

* [Docker installed](https://docs.docker.com/engine/install/ubuntu/)

Procedure for first time deploy
--------------------------

```shell
# copy or clone project to server 
git clone https://github.com/culturesofknowledge/site-edit-2
cd site-edit-2
git submodule update --init --recursive

cd siteedit2/settings
cp gunweb.py.example gunweb.py
# change hostname / ip in  ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS
# about email setting, see [How to set up email service ?]
# for export in search page, you need to update EXPORT_ROOT_URL
# e.g. EXPORT_ROOT_URL = 'http://your-emlo-edit-hostname'
# for more settings please see gunweb.py.example
vi gunweb.py


cd ../../docker/site-edit-2/
cp gunweb.env.example .gunweb.env
ln -sf .gunweb.env .env    # .env for `db` service
# edit variable in .gunweb.env if needed
# e.g. `DJANGO_SECRET_KEY`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, 
vi .gunweb.env


# run docker 
docker-compose -f docker-compose.yml -f docker-compose-gunweb.yml up -d --build db gunicorn_web nginx django-q
# -d for run in background 
# --build to build docker every time 

# wait few second, use curl or browser to test server is up
curl -L http://<ip>:8010/

# create account for testing
docker exec -it site-edit-2_gunicorn_web_1 python3 manage.py createsuperuser
```

Q & A
----------------------

### What will happen after run the "Procedure for first time deploy"?

* after docker startup, site-edit-2, postgres DB, and nginx will run in background
* nginx will be running in **8010** port

### How to change nginx port?

* edit file `docker-compose-gunweb.yml`

### Is it running on https?

* for now (2023-01-12), it has no settings for https yet, I believe we can add https settings by
  editing `nginx-gun.conf` file

### What is relation of each component ?

```
---------     ----------------     ------------
| nginx | --> | site-edit-2  | --> | postgres |
---------     |  (gunicorn)  |     ------------
              ----------------
```

### improve throughput of web server

* add number of working `GUN_NUM_WORKERS` in `.gunweb.env`

### How to set up email service ?

we used django buildin email module, following variable need to be set:
update `site-edit-2/siteedit2/settings/gunweb.py`
```python
# Host for sending email.
EMAIL_HOST = "smtp.mailgun.org"

# Port for sending email.
EMAIL_PORT = 587

# Whether to send SMTP 'Date' header in the local time zone or in UTC.
EMAIL_USE_LOCALTIME = False
EMAIL_HOST_USER = "postmaster@kasjldkajsdk.mailgun.org"
EMAIL_HOST_PASSWORD = "alksdjalskdjalskdjlaksdjlkas"
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
EMAIL_SSL_CERTFILE = None
EMAIL_SSL_KEYFILE = None
EMAIL_TIMEOUT = 60

EMAIL_FROM_EMAIL = f"Excited User <mailgun@kajsdlkasjdlkasjdl.mailgun.org>"

```


### How to read logs of web server

```
less -R /var/lib/docker/volumes/site-edit-2_emlo_home/_data/emlo.debug.log
```

Procedure for data migration
---------------------------------

* following command for copy data from old DB to new DB.
* it will process copy and convert to make old data compatible in new system
* pre condition
    * web server docker is running
    * old DB is running and can be connected to docker
    * at least 8GB RAM in server
    * command `psql` installed
* `-o` and `-t` should be ip and port of old DB, in my case it is 172.17.0.1
  * 172.17.0.1 is ip of docker host, docker host is the machine that run docker
* `old_audit_data.sql` is file that contain audit data

```shell

# after web server is up

docker exec -it site-edit-2_gunicorn_web_1 python3 manage.py data_migration -d ouls -p password -u postgres -o 172.17.0.1 -t 15432

# copy audit data to new db by sql
psql --host localhost --port 25432 -d postgres --password  --username postgres  < old_audit_data.sql
```


Config for `HTTPS` 
-------------------------------
* set `SESSION_COOKIE_SECURE` and `CSRF_COOKIE_SECURE` to `True` in django files


Offical Django Deployment checklist
--------------------------------------------
* https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/