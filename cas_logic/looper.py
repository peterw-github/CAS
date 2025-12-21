import os
import time

# We import the function directly from your existing injector.py
# Make sure injector.py is in the same folder!
try:
    from injector import send_prompt
except ImportError:
    print("[!] Critical: Could not find 'injector.py'. Make sure it is in the same folder.")
    exit()

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

    # Optional: Add a meta-prompt so I know why you are sending this back
    # You can comment this out if you just want the raw text
    final_payload = f"Please review/summarize the following text:\n\n{message_content}"

    # OR, if you want just the raw text:
    # final_payload = message_content

    # 3. Trigger the Injector
    print("[*] Injecting payload into Chrome...")
    success = send_prompt(final_payload)

    if success:
        print("[+] Loop complete. Message sent back to AI.")
    else:
        print("[!] Injection failed.")


if __name__ == "__main__":
    relay_last_message()