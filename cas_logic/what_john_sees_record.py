import subprocess
import time
import os
from cas_logic import upload_file  # Import the tool to load clipboard

# --- CONFIGURATION ---
PHONE_IP = "192.168.0.235"
ADB_PORT = "5555"
# Adjusted path relative to CAS if needed, or absolute
ADB_PATH = r"D:\CAS\Phone_Code\android_sdk_platform_tools\adb.exe"  # <--- CHECK THIS PATH ON YOUR MACHINE
PC_DESTINATION_FOLDER = r"D:\CAS\Phone_Code\Recordings"

# COORDINATES (Keep your working coordinates)
COORD_WIDE_LENS = "1550 630"
COORD_SAVE_TICK = "1850 553"


def run_adb_cmd(command_string, return_output=False):
    # Verify ADB exists
    if not os.path.exists(ADB_PATH):
        print(f"[ADB] Error: ADB executable not found at {ADB_PATH}")
        return None

    full_cmd = f'"{ADB_PATH}" {command_string}'
    try:
        result = subprocess.run(full_cmd, shell=True, check=True, capture_output=True, text=True)
        if return_output:
            return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[ADB] Command failed: {e}")
        return None


def connect_wireless():
    print(f"[ADB] Connecting to Pixel 9 ({PHONE_IP})...")
    run_adb_cmd("disconnect")  # Clear stale
    output = run_adb_cmd(f"connect {PHONE_IP}:{ADB_PORT}", return_output=True)
    if output and f"connected to {PHONE_IP}" in output:
        return True
    return False


def get_camera_files():
    cmd = "shell ls /sdcard/DCIM/Camera/"
    output = run_adb_cmd(cmd, return_output=True)
    if not output: return set()
    return {f for f in output.splitlines() if f.endswith(".mp4")}


def record_phone_screen(duration_seconds=10):
    """
    Records video on Phone, Pulls to PC, Copies to Clipboard.
    Returns True if success.
    """

    # 1. Connectivity Check
    if not connect_wireless():
        print("[ADB] Could not connect to phone.")
        return False

    # 2. Inventory (Before)
    print("[ADB] Scanning files...")
    files_before = get_camera_files()

    print(f"[ADB] Recording {duration_seconds}s...")

    # 3. Execution Sequence
    run_adb_cmd("shell input keyevent 224")  # Wake
    run_adb_cmd("shell input swipe 500 1500 500 500")  # Unlock
    time.sleep(1)

    run_adb_cmd("shell am start -a android.media.action.VIDEO_CAPTURE")
    time.sleep(0.5)
    run_adb_cmd(f"shell input tap {COORD_WIDE_LENS}")  # Wide Angle
    time.sleep(0.5)

    run_adb_cmd("shell input keyevent 24")  # Start Record
    time.sleep(duration_seconds)
    run_adb_cmd("shell input keyevent 24")  # Stop Record

    time.sleep(0.5)
    run_adb_cmd(f"shell input tap {COORD_SAVE_TICK}")  # Confirm Save if needed

    print("[ADB] Finalizing file...")
    time.sleep(3)  # Critical wait for file write

    # 4. Inventory (After) & Compare
    files_after = get_camera_files()
    new_files = files_after - files_before

    if not new_files:
        print("[ADB ERROR] No new video file detected.")
        return False

    new_video_name = list(new_files)[0]
    phone_path = f"/sdcard/DCIM/Camera/{new_video_name}"
    local_path = os.path.join(PC_DESTINATION_FOLDER, new_video_name)

    if not os.path.exists(PC_DESTINATION_FOLDER):
        os.makedirs(PC_DESTINATION_FOLDER)

    # 5. Pull File
    print(f"[ADB] Pulling {new_video_name}...")
    run_adb_cmd(f'pull "{phone_path}" "{local_path}"')

    # 6. Verify and Clipboard
    if os.path.exists(local_path):
        # We reuse the logic from screen_record: Copy to Clipboard
        success = upload_file.copy_file_to_clipboard(local_path)
        if success:
            print("[ADB] Success! Video pushed to clipboard.")
            return True

    return False