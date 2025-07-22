import urllib.request
from base64 import b64encode
import importlib
import os

import Secret

importlib.reload(Secret)

from Secret import Secret


class Notification:
    def __init__(self):
        Secret().loadEnv()
        
    def sendNotification(self, message):
        url = os.environ.get("NTFY_URL")
        username = os.environ.get("NTFY_USER")
        password = os.environ.get("NTFY_PASS")
        data = message.encode("utf-8")
        credentials = f"{username}:{password}"
        b64_credentials = b64encode(credentials.encode("utf-8")).decode("utf-8")

        req = urllib.request.Request(url, data=data)
        req.add_header("Authorization", f"Basic {b64_credentials}")
        req.add_header("Content-Type", "text/plain")

        try:
            with urllib.request.urlopen(req) as response:
                print(f"Notification sent. Status: {response.status}")
        except Exception as e:
            print(f"Failed to send notification: {e}")
