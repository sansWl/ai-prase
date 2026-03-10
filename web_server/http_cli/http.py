import requests


def send_request(url: str, data: dict):
    response = requests.post(url, json=data)
    return response.json()