# In cas_logic/what_john_sees_snapshot.py

import requests
from PIL import Image
import io
import win32clipboard

PHONE_URL = "http://192.168.0.235:8080/snap"


def fetch_and_clipboard_eye():
    try:
        # 1. Fetch from Phone
        print(f"[VISION] Connecting to Eye at {PHONE_URL}...")
        response = requests.get(PHONE_URL, timeout=3)

        if response.status_code == 200:
            # 2. Convert to Image Object
            image_bytes = io.BytesIO(response.content)
            img = Image.open(image_bytes)

            # 3. Convert to BMP buffer for Clipboard
            output = io.BytesIO()
            img.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]
            output.close()

            # 4. Push to Clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
            return True
        else:
            print(f"[VISION ERROR] Status Code: {response.status_code}")
            return False

    except Exception as e:
        print(f"[VISION ERROR] Eye Fetch Failed: {e}")
        return False


fetch_and_clipboard_eye()