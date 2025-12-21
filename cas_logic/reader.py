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
    """Connects to the running Chrome instance."""
    options = Options()
    options.add_experimental_option("debuggerAddress", DEBUG_PORT)
    try:
        return webdriver.Chrome(options=options)
    except Exception as e:
        print(f"[!] Critical: Could not connect to Chrome ({DEBUG_PORT}).\nError: {e}")
        return None


def wait_for_clipboard_update(previous_content, timeout=5):
    """
    Waits until the clipboard content changes from what it was before.
    Returns the new content, or None if it timed out.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        current_content = pyperclip.paste()
        if current_content != previous_content and current_content.strip():
            return current_content
        time.sleep(0.1)
    return None


def trigger_google_copy(driver, thumbs_up_button):
    """
    Navigates from Thumbs Up -> Parent Bubble -> Three Dots -> Copy.
    """
    try:
        # 1. Snapshot current clipboard (so we know when it changes)
        old_clipboard = pyperclip.paste()

        # 2. Find the container bubble (Go up from Thumbs Up)
        chat_bubble = thumbs_up_button.find_element(By.XPATH,
                                                    "./ancestor::div[contains(@class, 'chat-turn-container')]")

        # 3. Find and Click the 'Three Dots' (Force Click)
        options_btn = chat_bubble.find_element(By.CSS_SELECTOR, "button[aria-label='Open options']")
        driver.execute_script("arguments[0].click();", options_btn)

        # 4. Wait for Menu and Click 'Copy as markdown'
        wait = WebDriverWait(driver, 3)
        copy_menu_item = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(text(), 'Copy as markdown')]/ancestor::button")
        ))
        copy_menu_item.click()

        # 5. Wait for the OS Clipboard to actually receive the new text
        new_text = wait_for_clipboard_update(old_clipboard)

        return new_text

    except Exception as e:
        print(f"  [!] Interaction Error: {e}")
        return None


def main():
    driver = connect_chrome()
    if not driver: return

    print("--- READER V7: THUMBS-UP TRIGGER ACTIVE ---")

    # Track the specific ID of the Thumbs Up button to avoid duplicates
    last_processed_id = None

    while True:
        try:
            # 1. Find all 'Good response' buttons
            thumbs_buttons = driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Good response']")

            # If none exist, just wait
            if not thumbs_buttons:
                time.sleep(1)
                continue

            # 2. Target the latest one
            latest_button = thumbs_buttons[-1]

            # 3. Check if we have already handled this specific button
            if latest_button.id != last_processed_id:
                print("\n[!] New message detected via Thumbs Up.")

                # Execute the extraction
                captured_text = trigger_google_copy(driver, latest_button)

                if captured_text:
                    # Save to file
                    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                        f.write(captured_text)

                    print(f"  [System] Saved {len(captured_text)} chars to {OUTPUT_FILE}")

                    # Mark this button ID as processed
                    last_processed_id = latest_button.id
                    print("Waiting for next prompt...")

            else:
                # Idle wait
                time.sleep(1)

        except Exception:
            # Swallow minor DOM errors during page refreshes
            time.sleep(1)


if __name__ == "__main__":
    main()