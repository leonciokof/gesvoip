web: gunicorn --pythonpath="$PWD/gesvoip_project" gesvoip_project.wsgi -b "0.0.0.0:$PORT"
worker: gesvoip_project/manage.py celery worker -B -l info
