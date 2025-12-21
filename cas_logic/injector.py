import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def send_prompt(message_text):
    print(f"[CAS INJECTOR] Target: AI Studio. Payload: '{message_text}'")

    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 5)  # Smart wait up to 5 seconds

        # 1. Find Text Area (ROBUST selector)
        textarea = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "textarea[aria-label='Enter a prompt']")
        ))

        # 2. Focus and Type
        textarea.click()
        textarea.send_keys(Keys.END)
        textarea.send_keys("\n" + message_text)

        # 3. Wait for Button to Enable
        run_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Run']")

        # Explicitly wait until the button is clickable (meaning the text was registered)
        wait.until(EC.element_to_be_clickable(run_button))

        run_button.click()

        print("[CAS INJECTOR] Payload Delivered.")
        return True

    except Exception as e:
        print(f"[CAS INJECTOR] Error: {e}")
        return False


if __name__ == "__main__":
    send_prompt("[CAS TEST]: Connection Established. I am listening.")