import time, re, os
import cas_config as cfg
from cas_logic import actions, templates


def get_mtime():
    return os.path.getmtime(cfg.LATEST_MSG_FILE) if os.path.exists(cfg.LATEST_MSG_FILE) else 0


def send(text):
    with open(cfg.COMMAND_FILE, "w", encoding="utf-8") as f: f.write(text)
    time.sleep(0.2)


def smart_wait(seconds, last_mtime):
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

        # 1. FREQUENCY (Added 'prompt_frequency' to the list)
        if key in ["freq", "frequency", "timer", "prompt_frequency"]:
            try:
                # Cleanup args just in case
                clean_args = args.replace("`", "").strip()
                # Remove brackets [ ] if user typed them literally
                clean_args = clean_args.replace("[", "").replace("]", "")

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
            send(f"SCREENSHOT|||{templates.format_vision(int(curr_int / 60))}")

        # 5. UPLOAD
        elif key == "upload":
            if os.path.exists(args):
                print(f"  >>> [CMD] Upload: {args}")
                fname = os.path.basename(args)
                send(f"UPLOAD|||{args}|||{templates.format_upload(fname, int(curr_int / 60))}")

        # 6. STOP
        elif key == "stop":
            stop = True

    if not found_cmd: print("  >>> [INFO] Silence.")
    return new_int, stop


def main():
    print("[CAS BRAIN] Online. Fixed Keywords.")
    curr_int = cfg.DEFAULT_INTERVAL
    last_mtime = get_mtime()
    next_hb = time.time()

    while True:
        now = time.time()

        # 1. Heartbeat
        if now >= next_hb:
            send(templates.format_heartbeat(int(curr_int / 60)))
            print("[CAS BRAIN] Heartbeat Sent.")
            next_hb = now + curr_int

        # 2. Wait
        rem = max(0, next_hb - time.time())
        if smart_wait(rem, last_mtime):
            # Interrupted
            new_int, stop = process_message(curr_int)
            last_mtime = get_mtime()
            if stop: break
            if new_int != curr_int:
                curr_int = new_int
                next_hb = time.time() + curr_int


if __name__ == "__main__":
    main()