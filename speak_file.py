import time
import os
from cas_logic.cas_voice import CASVoiceEngine

INPUT_FILE = "manual_input.md"


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] Could not find '{INPUT_FILE}'. Please create it first.")
        return

    # 1. Read the file
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        text = f.read().strip()

    if not text:
        print("[INFO] File is empty. Nothing to say.")
        return

    print(f"--- SPEAKING FROM: {INPUT_FILE} ---")
    print(f"Text: {text[:50]}..." if len(text) > 50 else f"Text: {text}")

    # 2. Start Engine
    voice = CASVoiceEngine()

    # 3. Speak
    voice.speak(text)

    # 4. Keep alive (Wait for user to close)
    # We need this because audio plays in a background thread.
    # If we exit main(), the audio cuts off instantly.
    print("\n--> Audio queued. Press ENTER to exit when finished.")
    input()

    # Cleanup
    voice.shutdown()


if __name__ == "__main__":
    main()