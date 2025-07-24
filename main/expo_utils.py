import requests
from django.conf import settings

EXPO_PUSH_URL = 'https://exp.host/--/api/v2/push/send'

def send_expo_push(to_token, title, body, data=None):
    """
    Sends a single push via Expo.
    """
    msg = {
        'to': to_token,
        'sound': 'default',
        'title': title,
        'body': body,
        'data': data or {}
    }
    resp = requests.post(EXPO_PUSH_URL, json=msg, headers={
        'Accept': 'application/json',
        'Accept-encoding': 'gzip, deflate',
        'Content-Type': 'application/json',
    })
    resp.raise_for_status()
    return resp.json()
