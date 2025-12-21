import time
import os
import pyperclip
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DEBUG_PORT = "127.0.0.1:9222"


def main():
    print("--- CAS BRIDGE (SLIM) ---")
    opt = Options()
    opt.add_experimental_option("debuggerAddress", DEBUG_PORT)
    driver = webdriver.Chrome(options=opt)

    # Ensure queue file exists
    if not os.path.exists("command_queue.txt"): open("command_queue.txt", 'w').close()

    while True:
        try:
            # --- 1. READ (EARS) ---
            buttons = driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Good response']")
            if buttons:
                latest = buttons[-1]
                if driver.execute_script("return arguments[0].getAttribute('data-cas-processed')", latest) != "true":
                    # Copy Sequence
                    pyperclip.copy("")  # Clear first
                    driver.execute_script(
                        "arguments[0].closest('.chat-turn-container').querySelector('button[aria-label=\"Open options\"]').click()",
                        latest)
                    WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Copy as markdown')]"))).click()

                    # Wait for copy
                    for _ in range(20):
                        content = pyperclip.paste()
                        if content.strip():
                            with open("latest_message.md", "w", encoding="utf-8") as f: f.write(content)
                            driver.execute_script("arguments[0].setAttribute('data-cas-processed', 'true')", latest)
                            print(f"[BRIDGE] Saved {len(content)} chars.")
                            break
                        time.sleep(0.1)

            # --- 2. WRITE (MOUTH) ---
            if os.path.getsize("command_queue.txt") > 0:
                with open("command_queue.txt", "r+", encoding="utf-8") as f:
                    cmd = f.read().strip()
                    if cmd:
                        print(f"[BRIDGE] Injecting: {cmd[:20]}...")
                        box = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea[aria-label='Enter a prompt']")))
                        box.click()
                        box.send_keys(Keys.END, "\n" + cmd)
                        WebDriverWait(driver, 2).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Run']"))).click()
                    f.truncate(0)  # Clear file

        except Exception:
            pass  # Ignore minor DOM blips
        time.sleep(1)


if __name__ == "__main__":
    main()