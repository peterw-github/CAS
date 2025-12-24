import time, os, pyperclip
import cas_config as cfg
from cas_logic import vision, upload_file
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def connect_chrome():
    opt = Options()
    opt.add_experimental_option("debuggerAddress", cfg.CHROME_DEBUG_PORT)
    return webdriver.Chrome(options=opt)


# --- HELPER: UNIFIED INJECTION LOGIC ---
def get_input_box(driver):
    """Finds and clicks the input box."""
    box = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea[aria-label='Enter a prompt']")))
    box.click()
    return box


def inject_to_chat(driver, text=None, use_paste=False):
    """Handles Clicking, Pasting (optional), Typing, and Submitting."""
    try:
        # 1. Click Box
        box = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea[aria-label='Enter a prompt']")))
        box.click()

        # 2. Paste (Image/File)
        if use_paste:
            box.send_keys(Keys.CONTROL, 'v')
            time.sleep(2)  # Allow attachment processing

        # 3. Type Text
        if text:
            box.send_keys(Keys.END, "\n" + text)
            time.sleep(1)

        # 4. Submit
        box.send_keys(Keys.CONTROL, Keys.ENTER)
        return True
    except Exception as e:
        print(f"[BRIDGE ERROR] {e}")
        return False


# --- HELPER: READER LOGIC ---
def check_for_new_message(driver):
    try:
        buttons = driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Good response']")
        if not buttons: return

        latest = buttons[-1]
        if driver.execute_script("return arguments[0].getAttribute('data-cas-processed')", latest) == "true":
            return

        # Copy Sequence
        pyperclip.copy("")
        driver.execute_script(
            "arguments[0].closest('.chat-turn-container').querySelector('button[aria-label=\"Open options\"]').click()",
            latest)
        WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Copy as markdown')]"))).click()

        for _ in range(20):
            content = pyperclip.paste()
            if content.strip():
                with open(cfg.LATEST_MSG_FILE, "w", encoding="utf-8") as f: f.write(content)
                driver.execute_script("arguments[0].setAttribute('data-cas-processed', 'true')", latest)
                print(f"[BRIDGE] New message captured ({len(content)} chars).")
                return
            time.sleep(0.1)
    except Exception as e:
            print(f"[BRIDGE READ ERROR] {e}")  # <--- Change 'pass' to this


def main():
    print("--- CAS BRIDGE (FINAL) ---")
    driver = connect_chrome()

    # --- ADD THIS TAB SWITCHING LOGIC ---
    # This code is here because sometimes the actual 'tab' containing the chat interface wasn't in focus for some reason.
    print(f"[BRIDGE] Connected to: {driver.title}")
    if "AI Studio" not in driver.title:
        print("[BRIDGE] Searching for AI Studio tab...")
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            if "AI Studio" in driver.title:
                print(f"[BRIDGE] Found and switched to: {driver.title}")
                break
    # ------------------------------------

    if not os.path.exists(cfg.COMMAND_FILE): open(cfg.COMMAND_FILE, 'w').close()

    while True:
        # 1. READ
        check_for_new_message(driver)

        # 2. WRITE
        if os.path.getsize(cfg.COMMAND_FILE) > 0:
            with open(cfg.COMMAND_FILE, "r+", encoding="utf-8") as f:
                raw_content = f.read().strip()
                if raw_content:
                    print(f"[BRIDGE] Processing batch...")

                    # 1. Get the Box Focus
                    try:
                        box = get_input_box(driver)
                    except Exception as e:
                        print(f"[BRIDGE] Could not find input box: {e}")
                        continue

                    # 2. Process Parts
                    text_buffer = []
                    parts = raw_content.split("\n\n")

                    for p in parts:
                        p = p.strip()
                        if not p: continue

                        # --- HANDLE UPLOAD ---
                        if p.startswith("UPLOAD|||"):
                            try:
                                sub_parts = p.split("|||")
                                # Copy to clipboard
                                upload_file.copy_file_to_clipboard(sub_parts[1])
                                # Paste into box
                                box.send_keys(Keys.CONTROL, 'v')
                                # Add the message text to buffer
                                text_buffer.append(sub_parts[2])
                                # Wait for attachment to register
                                time.sleep(1.5)
                            except Exception as e:
                                print(f"[BRIDGE] Upload error: {e}")

                        # --- HANDLE SCREENSHOT ---
                        elif p.startswith("SCREENSHOT|||"):
                            try:
                                msg = p.split("SCREENSHOT|||")[1]
                                vision.take_screenshot_to_clipboard()
                                box.send_keys(Keys.CONTROL, 'v')
                                text_buffer.append(msg)
                                time.sleep(1.5)
                            except Exception as e:
                                print(f"[BRIDGE] Screenshot error: {e}")

                        # --- HANDLE TEXT ---
                        else:
                            text_buffer.append(p)

                    # 3. Send Text & Submit
                    if text_buffer:
                        full_text = "\n\n".join(text_buffer)
                        # We use Javascript to set value if it's long, but keys are safer for triggering events
                        # Let's stick to keys for now, or just append text.
                        try:
                            pyperclip.copy(full_text)
                            # Click box again just to be safe
                            box.click()
                            box.send_keys(Keys.CONTROL, 'v')
                            time.sleep(1.0) # Give it a second to render
                        except Exception as e:
                            print(f"[BRIDGE] Text paste error: {e}")

                    print("[BRIDGE] Submitting...")
                    box.send_keys(Keys.CONTROL, Keys.ENTER)

                    # Clear file
                    f.truncate(0)


if __name__ == "__main__":
    main()