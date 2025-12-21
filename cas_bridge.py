import time
import os
import pyperclip
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Import logic modules
from cas_logic import vision
from cas_logic import upload_file  # <--- You renamed this, which is good.

DEBUG_PORT = "127.0.0.1:9222"


def main():
    print("--- CAS BRIDGE (VISION + UPLOAD + TEXT) ---")
    opt = Options()
    opt.add_experimental_option("debuggerAddress", DEBUG_PORT)
    driver = webdriver.Chrome(options=opt)

    if not os.path.exists("command_queue.txt"): open("command_queue.txt", 'w').close()

    while True:
        try:
            # --- 1. READ (EARS) ---
            # (Standard Reader Logic)
            buttons = driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Good response']")
            if buttons:
                latest = buttons[-1]
                if driver.execute_script("return arguments[0].getAttribute('data-cas-processed')", latest) != "true":
                    pyperclip.copy("")
                    driver.execute_script(
                        "arguments[0].closest('.chat-turn-container').querySelector('button[aria-label=\"Open options\"]').click()",
                        latest)
                    WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Copy as markdown')]"))).click()
                    for _ in range(20):
                        content = pyperclip.paste()
                        if content.strip():
                            with open("latest_message.md", "w", encoding="utf-8") as f: f.write(content)
                            driver.execute_script("arguments[0].setAttribute('data-cas-processed', 'true')", latest)
                            print(f"[BRIDGE] Saved {len(content)} chars.")
                            break
                        time.sleep(0.1)

            # --- 2. WRITE ---
            if os.path.getsize("command_queue.txt") > 0:
                with open("command_queue.txt", "r+", encoding="utf-8") as f:
                    cmd = f.read().strip()
                    if cmd:
                        print(f"[BRIDGE] Processing command...")

                        box = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea[aria-label='Enter a prompt']")))
                        box.click()

                        # A. SCREENSHOT
                        if cmd.startswith("SCREENSHOT|||"):
                            text_part = cmd.split("SCREENSHOT|||")[1]
                            print("[BRIDGE] Taking Screenshot...")
                            if vision.take_screenshot_to_clipboard():
                                box.send_keys(Keys.CONTROL, 'v')
                                time.sleep(2)
                                box.send_keys(Keys.END, "\n" + text_part)
                                time.sleep(1)
                                box.send_keys(Keys.CONTROL, Keys.ENTER)

                        # B. UPLOAD (NEW PROTOCOL)
                        elif cmd.startswith("UPLOAD|||"):
                            # Split into: [UPLOAD, path, text]
                            parts = cmd.split("|||")
                            if len(parts) >= 3:
                                path = parts[1]
                                text_part = parts[2]

                                print(f"[BRIDGE] Uploading file: {path}")
                                if upload_file.copy_file_to_clipboard(path):
                                    # 1. Paste File
                                    box.send_keys(Keys.CONTROL, 'v')
                                    time.sleep(2)

                                    # 2. Type Text
                                    box.send_keys(Keys.END, "\n" + text_part)
                                    time.sleep(1)

                                    # 3. Submit
                                    box.send_keys(Keys.CONTROL, Keys.ENTER)
                                else:
                                    box.send_keys(Keys.END, f"\n[SYSTEM ERROR] Could not upload file: {path}")
                                    box.send_keys(Keys.CONTROL, Keys.ENTER)

                        # C. STANDARD TEXT
                        else:
                            box.send_keys(Keys.END, "\n" + cmd)
                            time.sleep(1)
                            box.send_keys(Keys.CONTROL, Keys.ENTER)

                    f.truncate(0)

        except Exception:
            pass
        time.sleep(1)


if __name__ == "__main__":
    main()