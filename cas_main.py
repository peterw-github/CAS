import time
import datetime
import re
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# --- MODULAR IMPORTS ---
# Ensure your folder is named 'cas_logic' and has an empty __init__.py file inside it (optional in newer Python but good practice)
from cas_logic import injector
from cas_logic import reader

# --- CONFIG ---
DEBUG_PORT = "127.0.0.1:9222"
DEFAULT_INTERVAL = 10 * 60


def connect_chrome():
    print("[CAS MAIN] Connecting to Chrome...")
    options = Options()
    options.add_experimental_option("debuggerAddress", DEBUG_PORT)
    return webdriver.Chrome(options=options)


def parse_commands(text, current_interval):
    next_interval = current_interval
    should_stop = False

    # Flexible Regex for commands
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
    # 1. ONE Connection to rule them all
    driver = connect_chrome()
    if not driver: return

    print("[CAS MAIN] System Online.")
    current_interval = DEFAULT_INTERVAL

    while True:
        # 2. INJECT
        timestamp_str = datetime.datetime.now().isoformat(timespec='minutes')
        payload = f""" 
`>>>[{timestamp_str}]`
[CAS HEARTBEAT]: System Active. 
Current Interval: {int(current_interval / 60)}m.
"""
        # Pass the driver to the injector
        injector.send_prompt(driver, payload)

        # 3. READ (Blocking)
        # Pass the driver to the reader
        response_text = reader.wait_for_next_message(driver)

        # Save log
        with open("latest_message.md", "w", encoding="utf-8") as f:
            f.write(response_text)

        # 4. THINK
        current_interval, stop_signal = parse_commands(response_text, current_interval)

        if stop_signal:
            break

        # 5. WAIT
        print(f"[CAS MAIN] Sleeping for {int(current_interval / 60)} minutes...")
        time.sleep(current_interval)


if __name__ == "__main__":
    main_loop()