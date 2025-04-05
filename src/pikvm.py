import requests
import urllib3
from requests.auth import HTTPBasicAuth
from io import BytesIO
import cv2
import numpy as np

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_screenshot(api_url, username, password):
    """Get screenshot from PiKVM"""
    params = {
        "save": "false",
        "load": "false",
        "allow_offline": "false",
        "ocr": "false",
        "preview": "false",
    }
    response = requests.get(api_url, params=params, verify=False, auth=HTTPBasicAuth(username, password))
    if response.status_code == 200:
        image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        return cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    else:
        print(f"Failed to get image. Status code: {response.status_code}")
        return None