import time
import pyperclip
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def trigger_google_copy(driver, thumbs_up_button):
    """Helper: Clicks menus to copy text."""
    try:
        old_clipboard = pyperclip.paste()

        # Find container bubble
        chat_bubble = thumbs_up_button.find_element(By.XPATH,
                                                    "./ancestor::div[contains(@class, 'chat-turn-container')]")

        # Click Options (Three dots)
        options_btn = chat_bubble.find_element(By.CSS_SELECTOR, "button[aria-label='Open options']")
        driver.execute_script("arguments[0].click();", options_btn)

        # Wait for 'Copy as markdown'
        wait = WebDriverWait(driver, 3)
        copy_menu_item = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(text(), 'Copy as markdown')]/ancestor::button")
        ))
        copy_menu_item.click()

        # Wait for Clipboard update
        start_time = time.time()
        while time.time() - start_time < 5:
            current_content = pyperclip.paste()
            if current_content != old_clipboard and current_content.strip():
                return current_content
            time.sleep(0.1)
        return None
    except Exception:
        return None


def wait_for_next_message(driver):
    """
    BLOCKS execution until a NEW message appears in the chat.
    """
    print("[CAS READER] Watching for new response...", end="", flush=True)

    while True:
        try:
            # 1. Get all thumbs up buttons
            thumbs_buttons = driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Good response']")

            if not thumbs_buttons:
                time.sleep(1)
                continue

            latest_button = thumbs_buttons[-1]

            # 2. Check if we already processed this specific button
            is_processed = driver.execute_script("return arguments[0].getAttribute('data-cas-processed')",
                                                 latest_button)

            if is_processed == "true":
                time.sleep(1)
                continue

            # 3. It's new! Extract it.
            print("\n[CAS READER] New message detected. Extracting...")
            text = trigger_google_copy(driver, latest_button)

            if text:
                # Mark as processed
                driver.execute_script("arguments[0].setAttribute('data-cas-processed', 'true')", latest_button)
                return text
            else:
                print("[!] Copy failed. Retrying...")
                time.sleep(1)

        except Exception:
            time.sleep(1)