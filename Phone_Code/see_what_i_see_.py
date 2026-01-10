import subprocess
import time
import os

# --- CONFIGURATION ---
PHONE_IP = "192.168.0.235"  # REPLACE THIS with the Static IP you just set
ADB_PORT = "5555"  # This is the standard port we opened
ADB_PATH = r"D:\CAS\Phone_Code\android_sdk_platform_tools\adb.exe"
PC_DESTINATION_FOLDER = r"D:\CAS\Phone_Code\Recordings"

# COORDINATES
COORD_WIDE_LENS = "1550 630"
COORD_SAVE_TICK = "1850 553"

def connect_wireless():
    print(f"--- 📡 CONNECTING TO PIXEL 9 ({PHONE_IP}) ---")

    # 1. Disconnect any stale connections to avoid confusion
    run_adb_cmd("disconnect")

    # 2. Attempt to connect
    output = run_adb_cmd(f"connect {PHONE_IP}:{ADB_PORT}", return_output=True)

    # 3. Verify success
    if output and f"connected to {PHONE_IP}" in output:
        print("✅ Wireless connection established!")
        return True
    else:
        print(f"❌ Failed to connect. Output: {output}")
        print("⚠️  TROUBLESHOOTING: Did the phone reboot? You may need to plug in USB once to run 'adb tcpip 5555'.")
        return False




def run_adb_cmd(command_string, return_output=False):
    full_cmd = f'"{ADB_PATH}" {command_string}'
    try:
        result = subprocess.run(full_cmd, shell=True, check=True, capture_output=True, text=True)
        if return_output:
            return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        return None


def get_camera_files():
    """Returns a Python SET of all filenames in the camera folder."""
    cmd = "shell ls /sdcard/DCIM/Camera/"
    output = run_adb_cmd(cmd, return_output=True)

    if not output:
        return set()

    # Split into lines and keep only mp4s
    files = {f for f in output.splitlines() if f.endswith(".mp4")}
    return files


def record_and_pull(duration_seconds=5):
    # 1. SNAPSHOT: See what files exist BEFORE we start
    print("👀 Taking inventory of existing videos...")
    files_before = get_camera_files()

    print("--- 🎬 STARTING RECORDING ---")

    # Wake & Unlock
    run_adb_cmd("shell input keyevent 224")
    run_adb_cmd("shell input swipe 500 1500 500 500")
    time.sleep(1)

    # Launch & Config
    run_adb_cmd("shell am start -a android.media.action.VIDEO_CAPTURE")
    time.sleep(0.5)
    run_adb_cmd(f"shell input tap {COORD_WIDE_LENS}")
    time.sleep(0.5)

    # Record
    run_adb_cmd("shell input keyevent 24")  # Start
    print(f"⏳ Recording for {duration_seconds}s...")
    time.sleep(duration_seconds)
    run_adb_cmd("shell input keyevent 24")  # Stop

    # Save
    print("✅ Saving video...")
    time.sleep(0.5)
    run_adb_cmd(f"shell input tap {COORD_SAVE_TICK}")

    # CRITICAL WAIT: Give Android time to write the file info
    print("💾 Waiting for file to finalize...")
    time.sleep(3)

    # 2. SNAPSHOT: See what files exist AFTER
    files_after = get_camera_files()

    # 3. COMPARE: The new file is the one in 'After' that wasn't in 'Before'
    new_files = files_after - files_before

    if not new_files:
        print("❌ Error: No new file detected! (Did the recording save?)")
        return

    # In case multiple files were created (unlikely), grab the first one
    new_video_name = list(new_files)[0]
    print(f"🎉 Identified new video: {new_video_name}")

    # 4. PULL
    phone_path = f"/sdcard/DCIM/Camera/{new_video_name}"
    dest_path = os.path.join(PC_DESTINATION_FOLDER, new_video_name)

    if not os.path.exists(PC_DESTINATION_FOLDER):
        os.makedirs(PC_DESTINATION_FOLDER)

    print(f"🚀 Transferring to: {dest_path}")
    run_adb_cmd(f'pull "{phone_path}" "{dest_path}"')
    print("✅ Done!")


if __name__ == "__main__":
    if os.path.exists(ADB_PATH):
        # TRY CONNECTING FIRST
        if connect_wireless():
            record_and_pull()
        else:
            print("🛑 Aborting: Could not connect to phone.")
    else:
        print(f"❌ Error: Could not find ADB at {ADB_PATH}")