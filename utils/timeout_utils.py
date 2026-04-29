import requests

def safe_request(url, data):
    try:
        return requests.post(url, json=data, timeout=3)
    except requests.Timeout:
        print("Timeout occurred")
        return None