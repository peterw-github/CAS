import time, re, os
import cas_config as cfg
from cas_logic import actions, templates
from cas_logic.cas_voice import CASVoiceEngine

# --- GLOBAL VOICE INSTANCE ---
voice = None


def get_mtime():
    return os.path.getmtime(cfg.LATEST_MSG_FILE) if os.path.exists(cfg.LATEST_MSG_FILE) else 0


def send(text):
    with open(cfg.COMMAND_FILE, "w", encoding="utf-8") as f: f.write(text)
    time.sleep(0.2)


def smart_wait(seconds, last_mtime):
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

    # --- INJECTION POINT: VOICE ---
    if voice:
        # We pass the raw text. The voice engine handles cleaning it.
        voice.speak(text)
    # ------------------------------

    new_int = curr_int
    stop = False
    found_cmd = False
    response_buffer = []

    matches = re.finditer(r'(?m)^`?!CAS\s+(\w+)\s+(.*)$', text)

    for m in matches:
        found_cmd = True
        key = m.group(1).lower()
        raw_args = m.group(2).strip()
        args = raw_args.strip('`').strip()

        if key in ["freq", "frequency", "timer", "prompt_frequency"]:
            try:
                clean_args = args.replace("`", "").replace("[", "").replace("]", "").strip()
                mins = int(clean_args)
                new_int = mins * 60
                print(f"  >>> [CMD] Frequency: {mins}m")
                response_buffer.append(templates.format_freq_confirm(mins))
            except ValueError:
                print(f"  >>> [ERROR] Invalid Freq: {args}")

        elif key == "exec":
            out = actions.run_system_command(args)
            response_buffer.append(templates.format_result(args, out))
            print("  >>> [CMD] Exec Ran")

        elif key == "cd":
            full_cmd = f"cd {args}"
            out = actions.run_system_command(full_cmd)
            response_buffer.append(templates.format_result(full_cmd, out))
            print(f"  >>> [CMD] CD Alias Ran: {args}")

        elif key == "prompt_now":
            print("  >>> [CMD] Prompt Now")
            response_buffer.append(templates.format_prompt_now(int(curr_int / 60)))

        elif key == "screenshot":
            print("  >>> [CMD] Screenshot")
            payload = templates.format_screenshot_payload(int(curr_int / 60))
            response_buffer.append(f"SCREENSHOT|||{payload}")

        elif key == "upload":
            target_path = args
            if not os.path.isabs(target_path):
                simulated_cwd = actions.get_cwd()
                target_path = os.path.join(simulated_cwd, target_path)

            if os.path.exists(target_path):
                print(f"  >>> [CMD] Upload: {target_path}")
                fname = os.path.basename(target_path)
                payload = templates.format_upload_payload(fname, int(curr_int / 60))
                response_buffer.append(f"UPLOAD|||{target_path}|||{payload}")
            else:
                print(f"  >>> [ERROR] File not found: {target_path}")

        elif key == "stop":
            stop = True

    if not found_cmd:
        print("  >>> [INFO] Silence (User/AI interaction detected).")

    if response_buffer:
        full_response = "\n\n".join(response_buffer)
        full_response += "\n" + templates.get_status_footer(int(curr_int / 60))
        send(full_response)
        print("  >>> [RES SENT BATCH]")

    return new_int, stop


def main():
    global voice
    print("[CAS BRAIN] Online. Initializing Voice...")

    # --- START VOICE ---
    voice = CASVoiceEngine()
    # -------------------

    curr_int = cfg.DEFAULT_INTERVAL
    last_mtime = get_mtime()

    # --- STARTUP CHECK ---
    start_executed = False
    try:
        with open(cfg.LATEST_MSG_FILE, "r", encoding="utf-8") as f:
            startup_text = f.read()

        if re.search(r'(?m)^`?!CAS\s+(\w+)', startup_text):
            print("[CAS BRAIN] Pending command detected at startup.")
            new_int, stop = process_message(curr_int)
            if stop: return
            if new_int != curr_int: curr_int = new_int
            last_mtime = get_mtime()
            next_hb = time.time() + curr_int
            start_executed = True

    except Exception as e:
        print(f"[CAS BRAIN] Startup check error: {e}")

    if not start_executed:
        time_since_last_msg = time.time() - last_mtime
        if time_since_last_msg < curr_int:
            print(f"[CAS BRAIN] Recent conversation detected ({int(time_since_last_msg)}s ago).")
            next_hb = time.time() + (curr_int - time_since_last_msg)
        else:
            next_hb = time.time()

    while True:
        now = time.time()
        if now >= next_hb:
            send(templates.format_heartbeat(int(curr_int / 60)))
            print("[CAS BRAIN] Heartbeat Sent.")
            next_hb = now + curr_int

        rem = next_hb - time.time()
        if smart_wait(rem, last_mtime):
            new_int, stop = process_message(curr_int)
            last_mtime = get_mtime()
            if stop: break
            if new_int != curr_int: curr_int = new_int
            next_hb = time.time() + curr_int

    # Cleanup on exit
    if voice:
        voice.shutdown()


if __name__ == "__main__":
    main()