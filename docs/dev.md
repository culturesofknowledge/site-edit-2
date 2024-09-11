# How to run the project
* run background service (e.g. Databases)
```bash
docker-compose -f $EMLO_DOCKER_HOME/docker-compose.yml -f $EMLO_DOCKER_HOME/docker-compose-dev.yml up db chrome
```

* run tailwind 
```bash
export DJANGO_SETTINGS_MODULE='siteedit2.settings.local_dev'
$EMLO_VENV_PATH/bin/python3 $EMLO_CODE_HOME/manage.py tailwind start
```

* run web server
```bash
export DJANGO_SETTINGS_MODULE='siteedit2.settings.local_dev'
$EMLO_VENV_PATH/bin/python3 $EMLO_CODE_HOME/manage.py runserver 0.0.0.0:8020
```

