# EMLO Site Edit-2
This repository is a re-boot of the software behind the 
[Early Modern Letters Online (EMLO)](http://emlo.bodleian.ox.ac.uk/home) project for the 
[Bodleian Libraries](https://www.bodleian.ox.ac.uk/home) of the University of Oxford. 

More precisely this repository holds a new front-end design of the old one that can be found 
[here](https://github.com/culturesofknowledge/site-edit).

Project resides [here](https://github.com/culturesofknowledge/emlo-project/projects) and a list of relevant documents
can be found [here](https://github.com/culturesofknowledge/emlo-project/wiki/List-of-Documents).

The previous development approach was based on a modular
decoupled (almost) services like approach we are now going for a more 
monolithic style approach.

Dependencies:
* Postgres
* Django 4.0.4

## Uploader
Redesigned in isolation, as a modular piece that would integrate with the "old" code and accessible
[here](https://github.com/J4bbi/emlo_uploader), the code for this is now integrated into the repository as an
[app](https://docs.djangoproject.com/en/4.0/intro/tutorial01/#creating-the-polls-app).



How to run all unitest with docker 
------------------------------------
```
docker-compose -f $EMLO_CODE_HOME/docker-compose.yml -f $EMLO_CODE_HOME/docker-compose-pycharm.yml -f $EMLO_CODE_HOME/docker-compose-unittest.yml up pycharm-py
```



Reference
----------------------
* django-sass-processor -- https://github.com/jrief/django-sass-processor



How to use data migration tool
--------------------------------------

```shell
python3 manage.py data_migration -d ouls -p password -u postgres -o 172.17.0.1 -t 15432
```
* all input parameter is for connecting to old database (old db name, old password, old db host....  )

### if you need to use your own *settings* you can use --settings
```shell
python3 manage.py data_migration --settings=siteedit2.settings.local_dev -d ouls -p password -u postgres -o 172.17.0.1 -t 15432
```

How to create superuser 
----------------------------------
```shell
python3 manage.py createsuperuser
```
