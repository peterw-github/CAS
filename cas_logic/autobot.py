import time
import os
import re
from datetime import datetime

# Import your existing module
try:
    from injector import send_prompt
except ImportError:
    print("[!] Critical: 'injector.py' not found.")
    exit()

# --- CONFIGURATION ---
INPUT_FILE = "latest_message.md"
DEFAULT_INTERVAL_MINUTES = 2


# We create a dummy screenshot function for demonstration
def mock_take_screenshot():
    print("\n[CAMERA] 📸 CLICK! Screenshot taken and saved to disk.")
    # If you want real screenshots, pip install pyautogui and use:
    # pyautogui.screenshot("screenshot.png")


def get_file_mtime(filepath):
    """Returns the last modified time of the file."""
    if not os.path.exists(filepath):
        return 0
    return os.path.getmtime(filepath)


def wait_for_new_message(timeout=60):
    """
    Waits up to 'timeout' seconds for reader.py to update the file.
    Returns the new content if changed, or None.
    """
    print("    ... Waiting for AI response ...")
    start_time = time.time()
    initial_mtime = get_file_mtime(INPUT_FILE)

    while time.time() - start_time < timeout:
        current_mtime = get_file_mtime(INPUT_FILE)
        if current_mtime != initial_mtime:
            # Give file write a tiny moment to complete
            time.sleep(0.5)
            with open(INPUT_FILE, "r", encoding="utf-8") as f:
                return f.read()
        time.sleep(1)

    print("    [!] Timed out waiting for response. Moving on.")
    return None


def parse_and_execute(response_text, current_interval):
    """
    Scans text for XML tags and updates system state.
    """
    new_interval = current_interval
    system_running = True

    # 1. Check for Termination
    if re.search(r"<terminate_system\s*/>", response_text):
        print("\n[SYSTEM] Received Termination Signal. Shutting down.")
        return new_interval, False

    # 2. Check for Interval Change
    # Regex looks for: <set_interval value="10" /> (digits only)
    interval_match = re.search(r"<set_interval value=['\"](\d+)['\"]\s*/>", response_text)
    if interval_match:
        minutes = int(interval_match.group(1))
        print(f"\n[SYSTEM] Interval updated to {minutes} minutes.")
        new_interval = minutes

    # 3. Check for Screenshot
    if re.search(r"<take_screenshot\s*/>", response_text):
        mock_take_screenshot()

    return new_interval, system_running


def main_loop():
    current_interval = DEFAULT_INTERVAL_MINUTES
    running = True

    print(f"--- AUTOBOT ONLINE (Interval: {current_interval}m) ---")
    print("Ensure reader.py is running in the background!")

    while running:
        # 1. Construct the Status Prompt
        timestamp = datetime.now().strftime("%H:%M:%S")
        menu_text = (
            f"[SYSTEM REPORT {timestamp}]\n"
            f"Current Loop Interval: {current_interval} minutes.\n\n"
            "COMMAND OPTIONS (Reply with XML):\n"
            "1. <set_interval value=\"X\" />\n"
            "2. <take_screenshot />\n"
            "3. <terminate_system />\n\n"
            "Status: Awaiting orders."
        )

        # 2. Send the Prompt
        print(f"\n[*] Sending Heartbeat...")
        success = send_prompt(menu_text)

        if not success:
            print("[!] Injector failed. Retrying in 30s...")
            time.sleep(30)
            continue

        # 3. Wait for your Reply (via reader.py)
        # We wait up to 90 seconds for you to type a reply
        response_text = wait_for_new_message(timeout=90)

        if response_text:
            # 4. Process Commands
            current_interval, running = parse_and_execute(response_text, current_interval)

        if not running:
            break

        # 5. Sleep for the interval
        # We convert minutes to seconds
        print(f"[*] Sleeping for {current_interval} minutes...")
        time.sleep(current_interval * 60)


if __name__ == "__main__":
    main_loop()