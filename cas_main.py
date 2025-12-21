import time
import datetime
import re
import os
import sys

# Import our Hand (Injector)
# Ensure this path matches your project structure
from cas_logic.injector import send_prompt

# --- CONFIG ---
DEFAULT_INTERVAL = 10 * 60  # 10 Minutes
LATEST_MSG_FILE = "latest_message.md"


def get_file_mtime():
    """Returns the last modification time of the file."""
    if not os.path.exists(LATEST_MSG_FILE):
        return 0
    return os.path.getmtime(LATEST_MSG_FILE)


def get_latest_text():
    """Reads the file content safely."""
    if not os.path.exists(LATEST_MSG_FILE):
        return ""
    try:
        with open(LATEST_MSG_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"[CAS BRAIN] Error reading file: {e}")
        return ""


def parse_commands(text, current_interval):
    """
    Scans text for CAS commands.
    Returns: (new_interval, stop_signal)
    """
    next_interval = current_interval  # Persist existing interval by default
    should_stop = False

    # --- COMMAND 1: TIMER ---
    # Regex Explanation:
    # 1. We ignore the opening '<' to bypass Markdown escaping issues.
    # 2. We look for 'CAS_Timer'.
    # 3. We ignore junk until 'freq'.
    # 4. We accept straight (") or smart (”’) quotes.
    timer_match = re.search(r'CAS_Timer.*?freq\s*=\s*["”’\'](\d+)["”’\']', text)

    if timer_match:
        try:
            minutes = int(timer_match.group(1))
            next_interval = minutes * 60
            print(f"  >>> [COMMAND ACCEPTED] Timer set to {minutes} minutes.")
        except ValueError:
            print("  >>> [COMMAND ERROR] Could not parse minutes.")

    # --- COMMAND 2: STOP ---
    if "CAS_Stop" in text:
        print("  >>> [COMMAND ACCEPTED] Kill Switch engaged.")
        should_stop = True

    return next_interval, should_stop


def main_loop():
    print("---------------------------------------")
    print(f"[CAS BRAIN] Online. Monitoring: {LATEST_MSG_FILE}")
    print("---------------------------------------")

    current_interval = DEFAULT_INTERVAL

    while True:
        # 1. SNAPSHOT: When was the file last written to?
        last_mtime = get_file_mtime()

        # 2. EXECUTE: Send the Prompt
        timestamp_str = datetime.datetime.now().isoformat(timespec='minutes')
        payload = f""" 
`>>>[{timestamp_str}]`
[CAS HEARTBEAT]: System Active. 
Current Interval: {int(current_interval / 60)}m.
"""
        print(f"\n[CAS BRAIN] Sending Heartbeat (Interval: {int(current_interval / 60)}m)...")
        if not send_prompt(payload):
            print("[!] Failed to send prompt. Retrying loop in 60s...")
            time.sleep(60)
            continue

        # 3. LISTEN: Wait for file update (Max 60 seconds)
        print("[CAS BRAIN] Waiting for response...", end="", flush=True)

        new_content_detected = False

        # We check every 2 seconds, for up to 30 times (60 seconds total)
        for _ in range(30):
            time.sleep(2)
            current_mtime = get_file_mtime()

            # If the file's modified time is NEWER than our snapshot -> We have a reply
            if current_mtime > last_mtime:
                print(" RESPONSE RECEIVED.")
                new_content_detected = True
                break
            print(".", end="", flush=True)

        if not new_content_detected:
            print("\n[CAS BRAIN] No response detected (Timeout). Keeping old settings.")
            # If we timed out, we just go to sleep.
        else:
            # 4. PARSE: Read the new content
            # Give a tiny buffer for the file write to finish completely
            time.sleep(4)
            latest_text = get_latest_text()
            current_interval, stop_signal = parse_commands(latest_text, current_interval)

            if stop_signal:
                print("[CAS BRAIN] Exiting per user command.")
                sys.exit(0)

        # 5. SLEEP
        print(f"[CAS BRAIN] Sleeping for {int(current_interval / 60)} minutes...")
        time.sleep(current_interval)


if __name__ == "__main__":
    main_loop()