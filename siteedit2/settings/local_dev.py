# pylint: disable=unused-wildcard-import,wildcard-import
# pylint: disable=wrong-import-position,line-too-long
import os

os.environ['POSTGRES_NAME'] = 'postgres'
os.environ['POSTGRES_USER'] = 'postgres'
os.environ['POSTGRES_PASSWORD'] = 'postgres'
os.environ['POSTGRES_HOST'] = 'localhost'

from .base import *  # noqa

DEBUG = True

#ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.29.86']
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.29.86', '192.168.29.99']

CSRF_TRUSTED_ORIGINS = ['http://localhost', 'http://127.0.0.1', 'http://192.168.29.86', 'http://192.168.29.99']

DATABASES['default']['NAME'] = 'postgres'
DATABASES['default']['USER'] = 'postgres'
DATABASES['default']['PASSWORD'] = 'postgres'
DATABASES['default']['HOST'] = 'localhost'
DATABASES['default']['PORT'] = '25432'

STATIC_ROOT = '/home/rama/work/projects/EMLO/emlo/emlo-code/static'

# Email
EMAIL_FROM_EMAIL = ""

SECRET_KEY = 'aklasjdOI@J)(!J)(DJ!@()DJ)(JSIODJAOIF*)!N)@(!N)(EJ90sjd9a0sjd90asj9d0j09JDS90J)(Ad82)*@8dJ)*WDj)J@()JD(!J@)(DJ!)(@D*#*DJ@#)(DJ)(@!#DJ)(JS)IDJ()9jd09qajd90ajs9dq802j1'

MEDIA_ROOT = '/home/rama/work/projects/EMLO/emlo/emlo-code/media/files/'
MEDIA_URL =  '/home/rama/work/projects/EMLO/emlo/emlo-code/project-dirs/media/'

EMAIL_HOST="localhost"
#MAIL_USERNAME="faee44dae713db"
#MAIL_PASSWORD="7010ab07e00063"
EMAIL_PORT=1025

TEST_WEB_HOST = 'http://localhost:8000'
