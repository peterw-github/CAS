import time, os, pyperclip, datetime
import cas_config as cfg
from cas_logic import vision, upload_file, eyes
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException


def connect_chrome():
    opt = Options()
    opt.add_experimental_option("debuggerAddress", cfg.CHROME_DEBUG_PORT)
    # --- ADD THIS LINE ---
    opt.add_argument("--disable-background-timer-throttling")
    opt.add_argument("--disable-renderer-backgrounding")
    opt.add_argument("--disable-backgrounding-occluded-windows")
    # ---------------------
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
                # 1. Standard Write (For the Brain)
                with open(cfg.LATEST_MSG_FILE, "w", encoding="utf-8") as f:
                    f.write(content)

                # --- NEW: RAW LOGGING (MARKDOWN) ---
                try:
                    os.makedirs("RawTextFiles", exist_ok=True)
                    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    # Change extension to .md
                    raw_filename = os.path.join("RawTextFiles", f"msg_{ts}.md")

                    with open(raw_filename, "w", encoding="utf-8") as log_f:
                        # 1. Write the actual message (Markdown viewers will render this normally)
                        log_f.write(content)

                        # 2. Add a footer with the "Python Representation"
                        #    We wrap it in a code block so it's easy to read in PyCharm's preview.
                        log_f.write("\n\n---\n\n### DEBUG: RAW REPR\n```python\n")
                        log_f.write(repr(content))
                        log_f.write("\n```")

                    print(f"[BRIDGE] Logged raw message to {raw_filename}")
                except Exception as e:
                    print(f"[BRIDGE LOG ERROR] {e}")
                # -----------------------------------

                driver.execute_script("arguments[0].setAttribute('data-cas-processed', 'true')", latest)
                print(f"[BRIDGE] New message captured ({len(content)} chars).")
                return
            time.sleep(0.1)

    except StaleElementReferenceException:
        # The DOM updated while we were looking at it.
        # Ignore this and try again in the next loop.
        return
    except Exception as e:
        print(f"[BRIDGE READ ERROR] {e}")


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
                                file_identifier = sub_parts[1]
                                msg_payload = sub_parts[2]

                                # 1. Copy to Clipboard
                                # If it's a SCREEN_RECORD, the file is ALREADY in the clipboard (from the recording script).
                                # If it's a normal file path, we need to put it there now.
                                if file_identifier == "SCREEN_RECORD":
                                    pass  # Already in clipboard
                                else:
                                    upload_file.copy_file_to_clipboard(file_identifier)

                                # 2. Paste into Input Box
                                box.send_keys(Keys.CONTROL, 'v')

                                # 3. Add Message Text
                                text_buffer.append(msg_payload)

                                # 4. Processing Wait
                                # Videos need time for AI Studio to "watch" them before the send button unlocks.
                                if file_identifier == "SCREEN_RECORD":
                                    print("[BRIDGE] Video pasted. Waiting 12s for processing...")
                                    time.sleep(12.0)
                                else:
                                    time.sleep(2.0)  # Normal files are faster

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

                        # --- HANDLE IMAGE FROM PHONE ---
                        elif p.startswith("EYES|||"):
                            try:
                                msg = p.split("EYES|||")[1]
                                # Call the new logic
                                success = eyes.fetch_and_clipboard_eye()
                                if success:
                                    box.send_keys(Keys.CONTROL, 'v')
                                    text_buffer.append(msg)
                                    time.sleep(1.5)
                                else:
                                    text_buffer.append("[BRIDGE] Error fetching Eyes view.")
                            except Exception as e:
                                print(f"[BRIDGE] Eyes error: {e}")

                        # --- HANDLE TEXT ---
                        else:
                            text_buffer.append(p)

                    # 3. Send Text & Submit
                    if text_buffer:
                        full_text = "\n\n".join(text_buffer)

                        # --- STRATEGY 1: TRY CLIPBOARD (FAST) ---
                        copied_successfully = False
                        # Only try this if we think the screen might be unlocked
                        try:
                            for attempt in range(5):
                                try:
                                    pyperclip.copy(full_text)
                                    copied_successfully = True
                                    break
                                except:
                                    time.sleep(0.2)
                        except:
                            pass

                        if copied_successfully:
                            try:
                                box.click()
                                box.send_keys(Keys.CONTROL, 'v')
                                time.sleep(1.0)
                            except Exception as e:
                                print(f"[BRIDGE] Paste failed, retrying with typing... ({e})")
                                copied_successfully = False  # Trigger fallback

                        # --- STRATEGY 2: FALLBACK TO TYPING (SLOW BUT RELIABLE) ---
                        # The reason why we bother with this, is because if the Windows PC is locked, the clipboard won't work.
                        if not copied_successfully:
                            print(
                                "[BRIDGE] Clipboard unavailable (Screen Locked?). Switching to DIRECT TYPING.")
                            try:
                                # This sends the text directly to Chrome via code, bypassing the OS clipboard
                                box.send_keys(full_text)
                                time.sleep(1.0)
                            except Exception as e:
                                print(f"[BRIDGE ERROR] Direct typing failed: {e}")

                    print("[BRIDGE] Submitting...")
                    box.send_keys(Keys.CONTROL, Keys.ENTER)

                    # Clear file
                    f.truncate(0)


if __name__ == "__main__":
    main()