import mss, io, win32clipboard
from PIL import Image

def take_screenshot_to_clipboard():
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[0] # 0 = All Monitors
            print(f"[VISION] Capturing: {monitor}")
            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

            output = io.BytesIO()
            img.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]
            output.close()

            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
            return True
    except Exception as e:
        print(f"[VISION ERROR] {e}")
        return False