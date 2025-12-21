import time
import pyperclip
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIG ---
DEBUG_PORT = "127.0.0.1:9222"
OUTPUT_FILE = "latest_message.md"


def connect_chrome():
    options = Options()
    options.add_experimental_option("debuggerAddress", DEBUG_PORT)
    try:
        return webdriver.Chrome(options=options)
    except Exception as e:
        print(f"[!] Critical: Could not connect to Chrome ({DEBUG_PORT}).\nError: {e}")
        return None


def wait_for_clipboard_update(previous_content, timeout=5):
    """Waits for clipboard to change."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        current_content = pyperclip.paste()
        if current_content != previous_content and current_content.strip():
            return current_content
        time.sleep(0.1)
    return None


def trigger_google_copy(driver, thumbs_up_button):
    """Navigates from Thumbs Up -> Parent Bubble -> Three Dots -> Copy."""
    try:
        old_clipboard = pyperclip.paste()

        # 1. Find the container bubble
        chat_bubble = thumbs_up_button.find_element(By.XPATH,
                                                    "./ancestor::div[contains(@class, 'chat-turn-container')]")

        # 2. Find and Click 'Three Dots'
        options_btn = chat_bubble.find_element(By.CSS_SELECTOR, "button[aria-label='Open options']")
        driver.execute_script("arguments[0].click();", options_btn)

        # 3. Wait for Menu and Click 'Copy as markdown'
        wait = WebDriverWait(driver, 3)
        copy_menu_item = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(text(), 'Copy as markdown')]/ancestor::button")
        ))
        copy_menu_item.click()

        # 4. Wait for Clipboard
        new_text = wait_for_clipboard_update(old_clipboard)
        return new_text

    except Exception as e:
        # If interaction fails (e.g. menu didn't open), return None
        return None


def main():
    driver = connect_chrome()
    if not driver: return

    print("--- READER V9: VERIFIED TRIGGER ACTIVE ---")

    # We store the ACTUAL CONTENT of the last saved file.
    # This is the ultimate source of truth.
    last_saved_content = ""

    while True:
        try:
            # 1. Find all 'Good response' buttons
            thumbs_buttons = driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Good response']")

            if not thumbs_buttons:
                time.sleep(1)
                continue

            # 2. Target the latest one
            latest_button = thumbs_buttons[-1]

            # 3. Optimization: Check for a JS flag
            # We tag the button in the browser so we don't check it 100 times a second
            is_processed = driver.execute_script("return arguments[0].getAttribute('data-cas-processed')",
                                                 latest_button)

            if is_processed == "true":
                time.sleep(1)
                continue

            # 4. If not marked as processed, we suspect it might be new.
            print("\n[?] Unprocessed message detected. Verifying...")

            # Perform the copy
            captured_text = trigger_google_copy(driver, latest_button)

            if captured_text:
                # --- THE DOUBLE CHECK ---
                # Compare what we just copied to what we last saved.
                # We strip whitespace to avoid issues with newlines/spaces.
                if captured_text.strip() == last_saved_content.strip():
                    print("  [i] False alarm. Content matches last save. Marking as done.")
                else:
                    # It IS new!
                    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                        f.write(captured_text)
                    print(f"  [System] SAVED NEW MESSAGE ({len(captured_text)} chars).")
                    last_saved_content = captured_text

                # 5. Mark this button as processed in the DOM
                # This prevents the loop from trying again until the button is replaced (new message)
                driver.execute_script("arguments[0].setAttribute('data-cas-processed', 'true')", latest_button)
                print("Waiting for next prompt...")

            else:
                print("  [!] Failed to copy. Will retry...")
                time.sleep(1)

        except Exception:
            # Swallow minor DOM errors during page refreshes
            time.sleep(1)


if __name__ == "__main__":
    main()