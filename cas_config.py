# --- PORTS & FILES ---
CHROME_DEBUG_PORT = "127.0.0.1:9222"
LATEST_MSG_FILE = "latest_message.md"
COMMAND_FILE = "command_queue.txt"

# --- TIMING ---
DEFAULT_INTERVAL = 10 * 60  # 10 Minutes
BRIDGE_LOOP_DELAY = 1       # How fast the bridge checks for commands
CLIPBOARD_TIMEOUT = 5       # How long to wait for copy operations