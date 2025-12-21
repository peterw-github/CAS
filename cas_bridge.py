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
    except:
        pass


def main():
    print("--- CAS BRIDGE (FINAL) ---")
    driver = connect_chrome()
    if not os.path.exists(cfg.COMMAND_FILE): open(cfg.COMMAND_FILE, 'w').close()

    while True:
        # 1. READ
        check_for_new_message(driver)

        # 2. WRITE
        if os.path.getsize(cfg.COMMAND_FILE) > 0:
            with open(cfg.COMMAND_FILE, "r+", encoding="utf-8") as f:
                raw_cmd = f.read().strip()
                if raw_cmd:
                    print(f"[BRIDGE] CMD: {raw_cmd[:30]}...")

                    # Route Command
                    if raw_cmd.startswith("SCREENSHOT|||"):
                        text = raw_cmd.split("SCREENSHOT|||")[1]
                        if vision.take_screenshot_to_clipboard():
                            inject_to_chat(driver, text, use_paste=True)

                    elif raw_cmd.startswith("UPLOAD|||"):
                        parts = raw_cmd.split("|||")
                        if upload_file.copy_file_to_clipboard(parts[1]):
                            inject_to_chat(driver, parts[2], use_paste=True)

                    else:
                        # Standard Text
                        inject_to_chat(driver, raw_cmd, use_paste=False)

                f.truncate(0)

        time.sleep(cfg.BRIDGE_LOOP_DELAY)


if __name__ == "__main__":
    main()