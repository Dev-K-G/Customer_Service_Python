import time
import requests

def retry_request(url, data, retries=3):
    delay = 1

    for _ in range(retries):
        try:
            return requests.post(url, json=data, timeout=3)
        except Exception:
            time.sleep(delay)
            delay *= 2

    return None