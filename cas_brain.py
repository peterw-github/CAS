import time, datetime, re, os

DEFAULT_INTERVAL = 10 * 60


def wait_for_reply(timeout=60):
    """Waits for latest_message.md to be modified."""
    start_mtime = os.path.getmtime("latest_message.md") if os.path.exists("latest_message.md") else 0
    print("[CAS BRAIN] Waiting...", end="", flush=True)

    for _ in range(timeout // 2):
        time.sleep(2)
        if (os.path.getmtime("latest_message.md") if os.path.exists("latest_message.md") else 0) > start_mtime:
            print(" RECEIVED.")
            time.sleep(0.5)  # Let write finish
            with open("latest_message.md", "r", encoding="utf-8") as f: return f.read()
        print(".", end="", flush=True)
    print(" TIMEOUT.")
    return None


def main_loop():
    print("[CAS BRAIN] Online.")
    interval = DEFAULT_INTERVAL

    while True:
        # 1. Speak
        timestamp = datetime.datetime.now().isoformat(timespec='minutes')
        payload = f"`>>>[{timestamp}]`\n[CAS HEARTBEAT] Active. Interval: {int(interval / 60)}m."
        with open("command_queue.txt", "w", encoding="utf-8") as f:
            f.write(payload)

        # 2. Listen
        response = wait_for_reply()

        # 3. Think
        if response:
            match = re.search(r'CAS_Timer.*?freq\s*=\s*["”’\'](\d+)["”’\']', response)
            if match:
                interval = int(match.group(1)) * 60
                print(f"  >>> Interval set to {interval // 60}m.")
            if "CAS_Stop" in response: break

        # 4. Sleep
        print(f"[CAS BRAIN] Sleeping {int(interval / 60)}m...")
        time.sleep(interval)


if __name__ == "__main__":
    main_loop()