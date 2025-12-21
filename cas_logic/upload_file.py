import win32clipboard, os, struct

def copy_file_to_clipboard(file_path):
    try:
        file_path = os.path.abspath(file_path)
        if not os.path.exists(file_path): return False

        # Build Windows CF_HDROP structure
        files = (file_path + "\0\0").encode('utf-16-le')
        header = struct.pack("IIIII", 20, 0, 0, 0, 1)
        data = header + files

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(15, data) # 15 = CF_HDROP
        win32clipboard.CloseClipboard()
        return True
    except Exception as e:
        print(f"[FILE ERROR] {e}")
        return False