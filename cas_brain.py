import time, re, os
from cas_logic import actions, templates

# --- CONFIG ---
DEFAULT_INTERVAL = 10 * 60
LATEST_MSG_FILE = "latest_message.md"
COMMAND_FILE = "command_queue.txt"


# --- IO UTILS ---
def get_file_mtime():
    return os.path.getmtime(LATEST_MSG_FILE) if os.path.exists(LATEST_MSG_FILE) else 0


def send_to_bridge(text):
    with open(COMMAND_FILE, "w", encoding="utf-8") as f: f.write(text)


def smart_wait(seconds, last_mtime):
    print(f"[CAS BRAIN] Sleeping {int(seconds)}s...", end="", flush=True)
    start = time.time()
    while time.time() - start < seconds:
        if get_file_mtime() > last_mtime:
            print("\n[CAS BRAIN] ! INTERRUPT DETECTED !")
            return True
        time.sleep(1)
    print(" Done.")
    return False


# --- LOGIC ---
def process_latest_message(current_interval):
    time.sleep(0.5)
    with open(LATEST_MSG_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    new_interval = current_interval
    should_stop = False

    # Regex to find commands
    matches = re.finditer(r'(?m)^!CAS\s+(\w+)\s*(.*)', text)
    command_found = False

    for match in matches:
        command_found = True
        keyword = match.group(1).lower()
        args = match.group(2).strip()

        # 1. FREQ
        if keyword in ["freq", "frequency", "timer"]:
            try:
                minutes = int(args)
                new_interval = minutes * 60
                print(f"  >>> [COMMAND] Frequency: {minutes}m.")
                send_to_bridge(templates.format_freq_confirm(minutes))
            except:
                pass

        # 2. EXEC
        elif keyword == "exec":
            output = actions.run_system_command(args)
            send_to_bridge(templates.format_result(args, output))
            print("  >>> [RESULT SENT]")

        # 3. PROMPT NOW
        elif keyword == "prompt_now":
            print("  >>> [COMMAND] Immediate Prompt.")
            send_to_bridge(templates.format_prompt_now(int(current_interval / 60)))

        # 4. STOP
        elif keyword == "stop":
            should_stop = True

        # 5. SCREENSHOT
        elif keyword == "screenshot":
            print("  >>> [COMMAND] Requesting Screenshot.")

            # Generate the text payload
            text_payload = templates.format_screenshot_payload(int(current_interval / 60))

            # Combine Tag + Text
            composite_command = f"SCREENSHOT|||{text_payload}"

            send_to_bridge(composite_command)


        # 6. UPLOAD (File Attachment)
        elif keyword == "upload":
            path = args.strip()
            if os.path.exists(path):
                print(f"  >>> [COMMAND] Uploading File: {path}")

                # 1. Get Filename for the message
                filename = os.path.basename(path)

                # 2. Generate Message
                text_payload = templates.format_upload_payload(filename, int(current_interval / 60))

                # 3. Create Composite Command: UPLOAD|||path|||text
                cmd = f"UPLOAD|||{path}|||{text_payload}"

                send_to_bridge(cmd)
            else:
                print(f"  >>> [ERROR] File not found: {path}")

    if not command_found:
        print("  >>> [INFO] No commands found. Silence.")

    return new_interval, should_stop


def main_loop():
    print("[CAS BRAIN] Online. Modular Version.")
    current_interval = DEFAULT_INTERVAL
    last_read_mtime = get_file_mtime()
    next_heartbeat_time = time.time()

    while True:
        now = time.time()

        # 1. HEARTBEAT
        if now >= next_heartbeat_time:
            payload = templates.format_heartbeat(int(current_interval / 60))
            send_to_bridge(payload)
            print("[CAS BRAIN] Heartbeat Sent.")
            next_heartbeat_time = now + current_interval

        # 2. WAIT & SLEEP
        seconds_remaining = max(0, next_heartbeat_time - time.time())

        if smart_wait(seconds_remaining, last_read_mtime):
            # Interrupted
            new_int, stop = process_latest_message(current_interval)
            last_read_mtime = get_file_mtime()

            if stop: break

            if new_int != current_interval:
                current_interval = new_int
                next_heartbeat_time = time.time() + current_interval


if __name__ == "__main__":
    main_loop()