"""
Django settings for gesvoip_project project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

import logging
import os
import sys

from getenv import env
from logentries import LogentriesHandler
from mongoengine import connect
import djcelery

djcelery.setup_loader()

MONGODB_URI = env('MONGODB_URI', 'mongodb://127.0.0.1/gesvoip')
connect('gesvoip', host=MONGODB_URI)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = env(
    'SECRET_KEY', 'lf&u5w0$1zicy4kxsl@2=%+orky(off#(ivx95^u4zjk@@0(!j')

DEBUG = env('DEBUG', True)

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = env('ALLOWED_HOSTS', ['*'])

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'mongoengine.django.mongo_auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'crispy_forms',
    'pagination_bootstrap',
    'django_extensions',
    'djrill',
    'activelink',
    'raven.contrib.django.raven_compat',
    'gesvoip',
    'djcelery',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pagination_bootstrap.middleware.PaginationMiddleware',
)

ROOT_URLCONF = 'gesvoip_project.urls'

WSGI_APPLICATION = 'gesvoip_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.dummy'
    }
}

LANGUAGE_CODE = 'es-cl'

TIME_ZONE = 'America/Santiago'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

ADMINS = (
    ('Leonardo Gatica', 'lgaticastyle@gmail.com'),
)

MANAGERS = ADMINS

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_URL = '/media/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

CRISPY_TEMPLATE_PACK = 'bootstrap3'

SERVER_EMAIL = 'contacto@convergia.cl'

DEFAULT_FROM_EMAIL = SERVER_EMAIL

INTERNAL_IPS = ('127.0.0.1',)

AUTHENTICATION_BACKENDS = (
    'mongoengine.django.auth.MongoEngineBackend',
)
SESSION_ENGINE = 'mongoengine.django.sessions'
AUTH_USER_MODEL = 'mongo_auth.MongoUser'
MONGOENGINE_USER_DOCUMENT = 'mongoengine.django.auth.User'

# Credenciales de conexion sftp para obtener portados
TEP_HOST = env('TEP_HOST')
TEP_USERNAME = env('TEP_USERNAME')
TEP_PASSWORD = env('TEP_PASSWORD')

GESVOIP_URL = env('GESVOIP_URL')
STI_URL = env('STI_URL')

BROKER_URL = env('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = BROKER_URL
BROKER_TRANSPORT = 'redis'
CELERYBEAT_SCHEDULER = 'celerybeatredis.schedulers.RedisScheduler'
CELERY_REDIS_SCHEDULER_URL = BROKER_URL
CELERY_REDIS_SCHEDULER_KEY_PREFIX = 'tasks:meta:'

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

else:
    EMAIL_BACKEND = 'djrill.mail.backends.djrill.DjrillBackend'
    MANDRILL_API_KEY = env('MANDRILL_APIKEY')
    RAVEN_CONFIG = {
        'dsn': env('RAVEN_DSN'),
    }
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'root': {
            'level': 'WARNING',
            'handlers': ['sentry'],
        },
        'formatters': {
            'verbose': {
                'format': (
                    '%(levelname)s %(asctime)s %(module)s %(process)d '
                    '%(thread)d %(message)s')
            },
        },
        'handlers': {
            'logentries_handler': {
                'token': env('LOGENTRIES_TOKEN'),
                'class': 'logentries.LogentriesHandler'
            },
            'sentry': {
                'level': 'ERROR',
                'class': (
                    'raven.contrib.django.raven_compat.handlers.SentryHandler')
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            },
        },
        'loggers': {
            'django.db.backends': {
                'level': 'ERROR',
                'handlers': ['console'],
                'propagate': False,
            },
            'raven': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
            'sentry.errors': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
            'logentries': {
                'handlers': ['logentries_handler'],
                'level': 'INFO',
            },
        },
    }
    MIDDLEWARE_CLASSES += ((
        'raven.contrib.django.raven_compat.middleware.'
        'SentryResponseErrorIdMiddleware'),
    )

if 'test' in sys.argv:
    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
    )
    DEBUG = False
    TEMPLATE_DEBUG = False
    EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
