import win32clipboard
import os
import struct


def copy_file_to_clipboard(file_path):
    """
    Copies a FILE object to the clipboard (simulating Ctrl+C on a file in Explorer).
    This allows 'pasting' the file as an attachment.
    """
    try:
        # Convert to absolute path to be safe
        file_path = os.path.abspath(file_path)

        if not os.path.exists(file_path):
            print(f"[FILE ERROR] Path not found: {file_path}")
            return False

        # Build the DROPFILES structure required by Windows (CF_HDROP)
        # 1. Prepare the file list (double null-terminated)
        files = (file_path + "\0\0").encode('utf-16-le')

        # 2. DROPFILES header
        # DWORD pFiles; (Offset = 20)
        # POINT pt; (x=0, y=0)
        # BOOL fNC; (0)
        # BOOL fWide; (1 for Unicode)
        header = struct.pack("IIIII", 20, 0, 0, 0, 1)

        data = header + files

        # 3. Open & Set
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(15, data)  # 15 = CF_HDROP
        win32clipboard.CloseClipboard()

        print(f"[FILE OPS] File loaded to clipboard: {file_path}")
        return True

    except Exception as e:
        print(f"[FILE OPS ERROR] {e}")
        return False