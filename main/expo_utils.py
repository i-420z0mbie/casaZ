import requests

def send_expo_push(token, title, body, data=None):
    response = requests.post(
        "https://exp.host/--/api/v2/push/send",
        json={
            "to": token,
            "title": title,
            "body": body,
            "data": data or {},
        },
        headers={
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/json",
        }
    )
    response.raise_for_status()
    return response.json()
