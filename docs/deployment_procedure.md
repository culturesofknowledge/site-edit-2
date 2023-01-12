last update date: 2023-01-12


Pre-condition
----------------------
* [Docker installed](https://docs.docker.com/engine/install/ubuntu/)


Procedure for first time deploy
--------------------------

```shell
# copy or clone project to server 
git clone https://github.com/culturesofknowledge/site-edit-2

cd site-edit-2/siteedit2/settings
cp gunweb.py.example gunweb.py
# change hostname / ip in  ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS
vi gunweb.py


cd ../../docker/site-edit-2/
cp gunweb.env.example .gunweb.env
# edit variable in .gunweb.env if needed
vi .gunweb.env


# run docker 
docker-compose -f docker-compose.yml -f docker-compose-gunweb.yml up -d --build db gunicorn_web nginx
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

### How to change nginx port

* edit file `docker-compose-gunweb.yml`

### Is it running on https?

* for now (2023-01-12), it has no settings for https yet, I believe we can add https settings by
  editing `nginx-gun.conf` file

### What is relation of each component ?
```
---------     --------------------------     ------------
| nginx | --> | site-edit-2 (gunicorn) | --> | postgres |
---------     --------------------------     ------------
```


### improve throughput of web server
* add number of working `GUN_NUM_WORKERS` in `.gunweb.env`



Procedure for data migration
---------------------------------
* KTODO