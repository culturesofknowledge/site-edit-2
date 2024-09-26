"""
Django settings for siteedit2 project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
# pylint: disable=unused-wildcard-import,wildcard-import

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
from cllib import log_utils

BASE_DIR = Path(__file__).resolve().parent.parent

EMLO_APP_HOME = os.environ.get('EMLO_APP_HOME', Path.home().joinpath('emlo_home').as_posix())
Path(EMLO_APP_HOME).mkdir(parents=True, exist_ok=True)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-0s-b#1j!$4!2e$u-ibm*5p$e_o1i%w-6%v$fu*5+bjkaj2j%tr')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

CSRF_TRUSTED_ORIGINS = ['http://localhost', 'http://127.0.0.1']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sass_processor',
    'django_q',
    'core',
    'login',
    'uploader',
    'location',
    'work',
    'institution',
    'manifestation',
    'person',
    'publication',
    'audit',
    'list',
    'tombstone',

    # Tailwind settings
    'tailwind',
    'emlotheme',
    'django_browser_reload',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'django_browser_reload.middleware.BrowserReloadMiddleware',
]

ROOT_URLCONF = 'siteedit2.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.emlo_global_contexts',
            ],
        },
    },
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'sass_processor.finders.CssFinder',
]

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "emlotheme/static_src"),
]

SASS_PROCESSOR_INCLUDE_DIRS = [
]

SASS_PROCESSOR_ROOT = 'static/'

WSGI_APPLICATION = 'siteedit2.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_NAME', '__unknown_env__'),
        'USER': os.environ.get('POSTGRES_USER', '__unknown_env__'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', '__unknown_env__'),
        'HOST': os.environ.get('POSTGRES_HOST', '__unknown_env__'),
        'PORT': '5432',
    }
}

# Django Q2 settings

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache',
    }
}

Q_CLUSTER = {
    'name': 'DjangORM',
    'workers': 4,
    'timeout': 90,
    'retry': 120,
    'queue_limit': 50,
    'bulk': 10,
    'orm': 'default'
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

debug_log_setting = {
    'level': 'DEBUG',
    'handlers': ['console'],
    'propagate': True,
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'detailed_web': {
            'format': log_utils.detailed_web_fmt,
            'datefmt': '%Y%m%d %H%M%S',
            'class': 'cllib.log_utils.ColorFormatter',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'detailed_web',
            'level': 'DEBUG',
        },

        'roll_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'detailed_web',
            'level': 'INFO',
            'filename': Path(EMLO_APP_HOME).joinpath('emlo.log').as_posix(),
            'backupCount': 10,
            'maxBytes': 10485760,
        },
        'roll_file_debug': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'detailed_web',
            'level': 'DEBUG',
            'filename': Path(EMLO_APP_HOME).joinpath('emlo.debug.log').as_posix(),
            'backupCount': 10,
            'maxBytes': 10485760,
        },

    },
    'loggers': {
        # # uncomment to log all sql
        # 'django.db.backends': {
        #     'level': 'DEBUG',
        #     'propagate': True,
        # },
        'urllib3.connectionpool': {
            'level': 'INFO',
            'propagate': True,
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'roll_file', 'roll_file_debug'],
        'propagate': True,
    },
}

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/London'

USE_I18N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'login.CofkUser'

# #### Login setting
LOGIN_URL = '/login/gate'
LOGIN_REDIRECT_URL = '/login/dashboard'

MEDIA_ROOT = '/code/files/'  # TODO this needs to be updated

MEDIA_URL = '/media/'

# ######### EMLO settings

DEFAULT_IMG_LICENCE_URL = 'http://cofk2.bodleian.ox.ac.uk/culturesofknowledge/licence/terms_of_use.html'

EMAIL_FROM_EMAIL = "Excited User <mailgun@<your mailgun messages url>>"

# Limit for file size, in kbs. Files larger than this will be queued.
UPLOAD_ASYNCHRONOUS_FILESIZE_LIMIT = 1000
UPLOAD_ROOT_URL = 'http://localhost:8000'

EMLO_SEQ_VAL_INIT = {
    'COFKUNIONPERSION__IPERSON_ID': 1000,
}

# SECURE
### change to True if you are using *https*
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# export
# root url for generate url in export
EXPORT_ROOT_URL = 'http://localhost:8020'

# Test
SELENIUM_CHROME_LOCAL_DRIVER = False
SELENIUM_CHROME_HEADLESS = False

# ------------------ Tailwind settings ------------------
TAILWIND_APP_NAME = 'emlotheme'

INTERNAL_IPS = [
    '127.0.0.1',
]
