import time
import os
from obswebsocket import obsws, requests
from cas_logic import upload_file
import cas_config as cfg  # Importing config to grab the folder path if needed

# --- CONFIGURATION ---
OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = "abeUarkO5QZDkcJw"  # <--- MAKE SURE THIS IS CORRECT


def wait_for_file_ready(filepath, timeout=20):
    """
    Watches a file and waits until it is > 0 bytes AND stops growing.
    """
    print(f"[OBS BRIDGE] Waiting for file to finalize (Muxing)...")
    start_time = time.time()
    last_size = -1
    stable_checks = 0

    while time.time() - start_time < timeout:
        try:
            if not os.path.exists(filepath):
                time.sleep(0.5)
                continue

            current_size = os.path.getsize(filepath)

            # 1. If it's 0 bytes, it's definitely not ready.
            if current_size == 0:
                time.sleep(1.0)
                continue

            # 2. Check if size is stable (hasn't changed since last loop)
            if current_size == last_size:
                stable_checks += 1
                # We want 2 consecutive checks where size matches to be sure
                if stable_checks >= 2:
                    print(f"[OBS BRIDGE] File ready: {current_size / 1024:.2f} KB")
                    return True
            else:
                # Size changed! It's still writing. Reset counter.
                stable_checks = 0
                last_size = current_size

            time.sleep(1.0)

        except Exception as e:
            print(f"[OBS BRIDGE] Wait error: {e}")
            time.sleep(1.0)

    print(f"[OBS BRIDGE] Timeout waiting for file: {filepath}")
    return False


def record_screen(duration=10):
    print(f"[OBS BRIDGE] Connecting to OBS...")

    try:
        ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
        ws.connect()

        # 1. Start Recording
        print(f"[OBS BRIDGE] Starting {duration}s recording...")
        ws.call(requests.StartRecord())

        # 2. Wait
        time.sleep(duration)

        # 3. Stop Recording
        print("[OBS BRIDGE] Stopping...")
        response = ws.call(requests.StopRecord())

        # 4. Extract path (This is usually instant, even if file is 0KB)
        saved_path = response.datain.get('outputPath')
        ws.disconnect()

        if saved_path:
            # --- THE FIX: WAIT FOR MUXING TO FINISH ---
            if wait_for_file_ready(saved_path, timeout=30):

                # 5. Copy to Clipboard
                success = upload_file.copy_file_to_clipboard(saved_path)
                if success:
                    print("[OBS BRIDGE] Success! Video is in your clipboard.")
                    return True
                else:
                    print("[ERROR] Failed to copy to clipboard.")
                    return False
            else:
                print("[ERROR] File never finished writing (Timeout).")
                return False
        else:
            print("[ERROR] OBS stopped, but returned no file path.")
            return False

    except Exception as e:
        print(f"[ERROR] OBS Connection Failed: {e}")
        return False


if __name__ == "__main__":
    print("--- TESTING OBS RECORDING ---")
    record_screen(5)