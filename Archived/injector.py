from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def send_prompt(driver, message_text):
    """
    Uses the EXISTING driver connection to send a prompt.
    """
    print(f"[CAS INJECTOR] Target: AI Studio. Payload: '{message_text}'")

    try:
        wait = WebDriverWait(driver, 5)  # Smart wait up to 5 seconds

        # 1. Find Text Area
        textarea = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "textarea[aria-label='Enter a prompt']")
        ))

        # 2. Focus and Type
        textarea.click()
        textarea.send_keys(Keys.END)
        # We add a newline to ensure it doesn't merge with previous text
        textarea.send_keys("\n" + message_text)

        # 3. Wait for Button to Enable
        run_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Run']")
        wait.until(EC.element_to_be_clickable(run_button))

        run_button.click()

        print("[CAS INJECTOR] Payload Delivered.")
        return True

    except Exception as e:
        print(f"[CAS INJECTOR] Error: {e}")
        return False