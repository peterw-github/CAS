import os
import time
import injector


INPUT_FILE = "latest_message.md"


def relay_last_message():
    """
    Reads the content of latest_message.md and feeds it back into AI Studio.
    """

    # 1. Validation Checks
    if not os.path.exists(INPUT_FILE):
        print(f"[!] Error: '{INPUT_FILE}' does not exist yet. Run reader.py first!")
        return

    # 2. Read the file
    print(f"[*] Reading {INPUT_FILE}...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        message_content = f.read().strip()

    if not message_content:
        print("[!] The file is empty. Nothing to send.")
        return

    print(f"[*] Content loaded ({len(message_content)} chars).")

    final_payload = message_content

    # 3. Trigger the Injector
    print("[*] Injecting payload into Chrome...")
    success = send_prompt(final_payload)

    if success:
        print("[+] Loop complete. Message sent back to AI.")
    else:
        print("[!] Injection failed.")


if __name__ == "__main__":
    relay_last_message()