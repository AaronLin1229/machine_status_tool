import requests
import json
import warnings

def crawl_api(url):
    try:
        warnings.filterwarnings('ignore', message='Unverified HTTPS request')
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        if isinstance(e, requests.Timeout):
            raise TimeoutError(f"Request timed out: {e}")
        elif isinstance(e, requests.HTTPError):
            raise ValueError(f"HTTP error occurred: {e}")
        elif isinstance(e, requests.ConnectionError):
            raise ConnectionError(f"Connection error occurred: {e}")
        else:
            raise RuntimeError(f"An unexpected error occurred: {e}")
