You are absolutely right. The "two scripts watching a file" approach is causing a **Race Condition**. `cas_main.py` gives up waiting before `reader.py` has finished writing, or they just get out of sync.

The smartest way to fix this is to **merge the logic**.

Instead of `reader.py` running in a separate infinite loop, we will turn `reader.py` into a **library** that `cas_main.py` imports.

**The New Logic Flow (Single Loop):**
1. `cas_main` sends the prompt.
2. `cas_main` calls `reader.wait_for_response()`. **(The script pauses here)**.
3. `reader` watches the browser. As soon as the response generates, it grabs it and returns it to `cas_main`.
4. `cas_main` processes the command and sleeps.

This guarantees you never miss a message.

Here are the two updated files.

### 1. `reader.py` (The Library)
*I have removed the `main()` loop. It now just provides a function that waits for the next message.*

```python
import time
import pyperclip
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def trigger_google_copy(driver, thumbs_up_button):
    """Interacts with UI to copy text to clipboard."""
    try:
        old_clipboard = pyperclip.paste()
        
        # Find container
        chat_bubble = thumbs_up_button.find_element(By.XPATH, "./ancestor::div[contains(@class, 'chat-turn-container')]")
        
        # Click Options
        options_btn = chat_bubble.find_element(By.CSS_SELECTOR, "button[aria-label='Open options']")
        driver.execute_script("arguments[0].click();", options_btn)
        
        # Wait for and Click 'Copy as markdown'
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
    BLOCKS and waits until a new, unprocessed 'Good response' button appears.
    Returns the text of the response.
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
            is_processed = driver.execute_script("return arguments[0].getAttribute('data-cas-processed')", latest_button)
            
            if is_processed == "true":
                # We have seen this one. Wait for a NEW one.
                time.sleep(1)
                continue
            
            # 3. It's new! Extract it.
            print("\n[CAS READER] New message detected. Extracting...")
            text = trigger_google_copy(driver, latest_button)
            
            if text:
                # Mark as processed so we don't read it again next loop
                driver.execute_script("arguments[0].setAttribute('data-cas-processed', 'true')", latest_button)
                return text
            else:
                print("[!] Copy failed. Retrying...")
                time.sleep(1)
                
        except Exception:
            time.sleep(1)
```

### 2. `cas_main.py` (The Controller)
*This script now owns the connection. It sends, waits (using the reader), parses, and sleeps.*

```python
import time
import datetime
import re
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Import our new Reader Library
import reader 

# --- CONFIG ---
DEBUG_PORT = "127.0.0.1:9222"
DEFAULT_INTERVAL = 10 * 60 

def connect_chrome():
    options = Options()
    options.add_experimental_option("debuggerAddress", DEBUG_PORT)
    return webdriver.Chrome(options=options)

def send_prompt(driver, message_text):
    """Injects prompt using the shared driver instance."""
    try:
        wait = WebDriverWait(driver, 5)
        textarea = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea[aria-label='Enter a prompt']")))
        textarea.click()
        textarea.send_keys(Keys.END)
        textarea.send_keys("\n" + message_text)
        
        run_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Run']")
        wait.until(EC.element_to_be_clickable(run_button))
        run_button.click()
        print("[CAS INJECTOR] Payload Sent.")
        return True
    except Exception as e:
        print(f"[CAS INJECTOR] Error: {e}")
        return False

def parse_commands(text, current_interval):
    next_interval = current_interval
    should_stop = False

    # Regex that ignores escape chars and handles smart quotes
    timer_match = re.search(r'CAS_Timer.*?freq\s*=\s*["”’\'](\d+)["”’\']', text)
    if timer_match:
        minutes = int(timer_match.group(1))
        next_interval = minutes * 60
        print(f"  >>> [COMMAND ACCEPTED] Timer set to {minutes} minutes.")

    if "CAS_Stop" in text:
        print("  >>> [COMMAND ACCEPTED] Kill Switch engaged.")
        should_stop = True

    return next_interval, should_stop

def main_loop():
    driver = connect_chrome()
    if not driver: return
    
    print("[CAS BRAIN] Online. Control Loop Started.")
    current_interval = DEFAULT_INTERVAL

    while True:
        # 1. SEND
        timestamp_str = datetime.datetime.now().isoformat(timespec='minutes')
        payload = f""" 
`>>>[{timestamp_str}]`
[CAS HEARTBEAT]: System Active. 
Current Interval: {int(current_interval / 60)}m.
"""
        send_prompt(driver, payload)

        # 2. WAIT & READ (This blocks until I reply)
        # We pass the driver to the reader so it watches the SAME window
        response_text = reader.wait_for_next_message(driver)
        
        # Save to file just for logging/history (optional)
        with open("latest_message.md", "w", encoding="utf-8") as f:
            f.write(response_text)

        # 3. PARSE
        current_interval, stop_signal = parse_commands(response_text, current_interval)

        if stop_signal:
            break

        # 4. SLEEP
        print(f"[CAS BRAIN] Sleeping for {int(current_interval / 60)} minutes...")
        time.sleep(current_interval)

if __name__ == "__main__":
    main_loop()
```

### How to run this:
1.  Save the code above into `reader.py` and `cas_main.py`.
2.  **Stop running reader.py separately.** You don't need it anymore.
3.  Just run `python cas_main.py`.

This effectively "merges" the two minds. `cas_main` now has eyes. It will send a message, stare at the screen until I reply, process the command, and then sleep. No timeouts, no race conditions.