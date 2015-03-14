"""
WSGI config for gesvoip_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os

import dotenv

env_file = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(
    	os.path.abspath(__file__)))), '.env')

if os.path.isfile(env_file):
    dotenv.read_dotenv(env_file)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gesvoip_project.settings")

from django.core.wsgi import get_wsgi_application
from dj_static import Cling

application = Cling(get_wsgi_application())
