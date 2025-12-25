import cas_config as cfg
from cas_logic import templates


def force_pulse():
    print("[MANUAL TRIGGER] Forcing a Heartbeat...")

    # Generate the standard heartbeat text
    # We assume standard 10 min interval for the manual trigger
    text = templates.format_heartbeat(10)

    # Write it directly to the command queue
    # This bypasses the Brain, but the Bridge will see it instantly.
    try:
        with open(cfg.COMMAND_FILE, "w", encoding="utf-8") as f:
            f.write(text)
        print("[MANUAL TRIGGER] Signal written to queue.")
        print("Check the Bridge terminal to see if it picks it up.")
    except Exception as e:
        print(f"[ERROR] Could not write trigger: {e}")


if __name__ == "__main__":
    force_pulse()