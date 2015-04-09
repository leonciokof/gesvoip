import json

from getenv import env
import requests


def send_message(message):
    payload = {'text': message}
    r = requests.post(env('SLACK_WEBHOOK_URL'), data=json.dumps(payload))
