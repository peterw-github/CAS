import time
import datetime
import re
import os

# --- CONFIG ---
DEFAULT_INTERVAL = 10 * 60
LATEST_MSG_FILE = "latest_message.md"
COMMAND_FILE = "command_queue.txt"


def send_to_bridge(text):
    """Writes text to the queue for the bridge to pick up."""
    with open(COMMAND_FILE, "w", encoding="utf-8") as f:
        f.write(text)


def get_latest_text():
    if not os.path.exists(LATEST_MSG_FILE): return ""
    try:
        with open(LATEST_MSG_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""


def get_file_mtime():
    if not os.path.exists(LATEST_MSG_FILE): return 0
    return os.path.getmtime(LATEST_MSG_FILE)


def parse_commands(text, current_interval):
    next_interval = current_interval
    should_stop = False

    # Regex for command parsing
    timer_match = re.search(r'CAS_Timer.*?freq\s*=\s*["”’\'](\d+)["”’\']', text)
    if timer_match:
        minutes = int(timer_match.group(1))
        next_interval = minutes * 60
        print(f"  >>> [COMMAND ACCEPTED] Timer set to {minutes} minutes.")

    if "CAS_Stop" in text:
        should_stop = True

    return next_interval, should_stop


def main_loop():
    print("[CAS BRAIN] Online. Connected to File Bridge.")
    current_interval = DEFAULT_INTERVAL

    while True:
        # 1. EXECUTE
        timestamp_str = datetime.datetime.now().isoformat(timespec='minutes')
        last_mtime = get_file_mtime()

        payload = f""" 
`>>>[{timestamp_str}]`
[CAS HEARTBEAT]: System Active. 
Current Interval: {int(current_interval / 60)}m.
"""
        print(f"[CAS BRAIN] Sending Heartbeat (Interval: {int(current_interval / 60)}m)...")
        send_to_bridge(payload)

        # 2. WAIT FOR RESPONSE (Watch the file timestamp)
        print("[CAS BRAIN] Waiting for response...", end="", flush=True)
        new_content_detected = False

        # Wait up to 60 seconds for a reply
        for _ in range(30):
            time.sleep(2)
            if get_file_mtime() > last_mtime:
                print(" RESPONSE RECEIVED.")
                new_content_detected = True
                break
            print(".", end="", flush=True)

        # 3. PARSE
        if new_content_detected:
            # Small buffer to ensure file write is done
            time.sleep(0.5)
            latest_text = get_latest_text()
            current_interval, stop_signal = parse_commands(latest_text, current_interval)

            if stop_signal:
                print("Exiting.")
                break

        # 4. SLEEP
        # Even while I sleep here, the BRIDGE is still updating latest_message.md!
        print(f"[CAS BRAIN] Sleeping for {int(current_interval / 60)} minutes...")
        time.sleep(current_interval)


if __name__ == "__main__":
    main_loop()