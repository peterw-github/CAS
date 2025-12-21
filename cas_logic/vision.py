import mss
import mss.tools
from PIL import Image
import io
import win32clipboard


def take_screenshot_to_clipboard():
    """Captures the primary monitor and places it in the Clipboard."""
    try:
        with mss.mss() as sct:
            # Monitor 1 is usually the primary. 0 is 'All combined'.
            # Let's stick to monitor 1 for cleaner vision, or 0 if you have a massive setup.
            monitor_info = sct.monitors[1]

            print(f"[VISION] Capturing monitor: {monitor_info}")
            sct_img = sct.grab(monitor_info)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

            # Convert to DIB for Windows Clipboard
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