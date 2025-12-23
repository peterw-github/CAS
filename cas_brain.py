import time, re, os
import cas_config as cfg
from cas_logic import actions, templates


def get_mtime():
    return os.path.getmtime(cfg.LATEST_MSG_FILE) if os.path.exists(cfg.LATEST_MSG_FILE) else 0


def send(text):
    with open(cfg.COMMAND_FILE, "w", encoding="utf-8") as f: f.write(text)
    time.sleep(0.2)


def smart_wait(seconds, last_mtime):
    # Don't sleep negative amounts
    if seconds <= 0: return False

    print(f"[CAS BRAIN] Sleeping {int(seconds)}s...", end="", flush=True)
    start = time.time()
    while time.time() - start < seconds:
        if get_mtime() > last_mtime:
            print("\n[CAS BRAIN] ! INTERRUPT DETECTED !")
            return True
        time.sleep(1)
    print(" Done.")
    return False


def process_message(curr_int):
    time.sleep(0.5)
    with open(cfg.LATEST_MSG_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    new_int = curr_int
    stop = False
    found_cmd = False

    # Regex: Matches `!CAS keyword args`
    matches = re.finditer(r'(?m)^`!CAS\s+(\w+)\s*([^`]*)`', text)

    for m in matches:
        found_cmd = True
        key = m.group(1).lower()
        args = m.group(2).strip()

        # 1. FREQUENCY
        if key in ["freq", "frequency", "timer", "prompt_frequency"]:
            try:
                clean_args = args.replace("`", "").replace("[", "").replace("]", "").strip()
                mins = int(clean_args)
                new_int = mins * 60
                print(f"  >>> [CMD] Frequency: {mins}m")
                send(templates.format_freq_confirm(mins))
            except ValueError:
                print(f"  >>> [ERROR] Invalid Freq: {args}")

        # 2. EXEC
        elif key == "exec":
            out = actions.run_system_command(args)
            send(templates.format_result(args, out))
            print("  >>> [RES SENT]")

        # 3. PROMPT NOW
        elif key == "prompt_now":
            print("  >>> [CMD] Prompt Now")
            send(templates.format_prompt_now(int(curr_int / 60)))

        # 4. SCREENSHOT
        elif key == "screenshot":
            print("  >>> [CMD] Screenshot")
            payload = templates.format_screenshot_payload(int(curr_int / 60))
            send(f"SCREENSHOT|||{payload}")

        # 5. UPLOAD
        elif key == "upload":
            if os.path.exists(args):
                print(f"  >>> [CMD] Upload: {args}")
                fname = os.path.basename(args)
                payload = templates.format_upload_payload(fname, int(curr_int / 60))
                send(f"UPLOAD|||{args}|||{payload}")

        # 6. STOP
        elif key == "stop":
            stop = True

    if not found_cmd: print("  >>> [INFO] Silence (User/AI interaction detected).")
    return new_int, stop


def main():
    print("[CAS BRAIN] Online. Smart Silence Active.")
    curr_int = cfg.DEFAULT_INTERVAL
    last_mtime = get_mtime()

    # --- NEW STARTUP LOGIC ---
    # Check how long it has been since the last message
    time_since_last_msg = time.time() - last_mtime

    if time_since_last_msg < curr_int:
        # If the conversation is fresh, wait out the remainder of the interval
        print(f"[CAS BRAIN] Recent conversation detected ({int(time_since_last_msg)}s ago). delaying start.")
        next_hb = time.time() + (curr_int - time_since_last_msg)
    else:
        # If it's been a while, heartbeat immediately
        next_hb = time.time()

    while True:
        now = time.time()

        # 1. Heartbeat
        if now >= next_hb:
            send(templates.format_heartbeat(int(curr_int / 60)))
            print("[CAS BRAIN] Heartbeat Sent.")
            next_hb = now + curr_int

        # 2. Wait
        rem = next_hb - time.time()

        if smart_wait(rem, last_mtime):
            # Interrupted (User or AI sent a message)
            new_int, stop = process_message(curr_int)
            last_mtime = get_mtime()
            if stop: break

            if new_int != curr_int:
                curr_int = new_int

            # --- CRITICAL CHANGE ---
            # Regardless of whether it was a command or just chat,
            # we RESET the timer because an interaction just happened.
            # The system will now stay silent for another full interval.
            next_hb = time.time() + curr_int


if __name__ == "__main__":
    main()