import time
import os
import pyperclip
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIG ---
DEBUG_PORT = "127.0.0.1:9222"
LATEST_MSG_FILE = "latest_message.md"
COMMAND_FILE = "command_queue.txt"


def connect_chrome():
    options = Options()
    options.add_experimental_option("debuggerAddress", DEBUG_PORT)
    return webdriver.Chrome(options=options)


def wait_for_clipboard_update(timeout=5):
    """Waits for clipboard to become non-empty."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        content = pyperclip.paste()
        if content and content.strip():  # If text exists
            return content
        time.sleep(0.1)
    return None


def read_browser(driver):
    """Checks for new message, copies it, checks duplicates, saves."""
    try:
        # 1. Find the latest button
        thumbs_buttons = driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Good response']")
        if not thumbs_buttons: return

        latest_button = thumbs_buttons[-1]

        # 2. Check if we already processed this specific button DOM element
        is_processed = driver.execute_script("return arguments[0].getAttribute('data-cas-processed')", latest_button)
        if is_processed == "true": return

        # 3. THE FIX: Clear clipboard first so we know when copy happens
        pyperclip.copy("")

        # 4. Perform the click sequence
        chat_bubble = latest_button.find_element(By.XPATH, "./ancestor::div[contains(@class, 'chat-turn-container')]")
        options_btn = chat_bubble.find_element(By.CSS_SELECTOR, "button[aria-label='Open options']")
        driver.execute_script("arguments[0].click();", options_btn)

        wait = WebDriverWait(driver, 2)
        copy_menu = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Copy as markdown')]/ancestor::button")))
        copy_menu.click()

        # 5. Wait for text to appear in clipboard
        new_text = wait_for_clipboard_update()

        if new_text:
            # Check against file to avoid writing duplicates
            current_file_content = ""
            if os.path.exists(LATEST_MSG_FILE):
                with open(LATEST_MSG_FILE, "r", encoding="utf-8") as f:
                    current_file_content = f.read()

            if new_text.strip() != current_file_content.strip():
                with open(LATEST_MSG_FILE, "w", encoding="utf-8") as f:
                    f.write(new_text)
                print(f"[BRIDGE] New message saved ({len(new_text)} chars).")
            else:
                print("[BRIDGE] Content identical to file. Marking as read.")

            # Mark as processed so we don't click it again
            driver.execute_script("arguments[0].setAttribute('data-cas-processed', 'true')", latest_button)

    except Exception as e:
        # Squelch minor DOM errors
        pass


def inject_prompt(driver):
    """Checks command_queue.txt. If content exists, injects it."""
    if not os.path.exists(COMMAND_FILE): return

    try:
        with open(COMMAND_FILE, "r", encoding="utf-8") as f:
            prompt_text = f.read().strip()

        if not prompt_text: return

        print(f"[BRIDGE] Injecting: {prompt_text[:30]}...")

        wait = WebDriverWait(driver, 5)
        textarea = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea[aria-label='Enter a prompt']")))
        textarea.click()
        textarea.send_keys(Keys.END)
        textarea.send_keys("\n" + prompt_text)

        run_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Run']")
        wait.until(EC.element_to_be_clickable(run_button))
        run_button.click()

        # Clear queue
        open(COMMAND_FILE, 'w').close()
        print("[BRIDGE] Injection Complete.")

    except Exception as e:
        print(f"[BRIDGE] Injection Error: {e}")


def main():
    print("--- CAS IO BRIDGE (FIXED) ---")
    driver = connect_chrome()

    if not os.path.exists(COMMAND_FILE):
        open(COMMAND_FILE, 'w').close()

    while True:
        read_browser(driver)
        inject_prompt(driver)
        time.sleep(1)


if __name__ == "__main__":
    main()