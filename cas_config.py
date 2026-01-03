# --- START OF FILE cas_config.py ---

# --- PORTS & FILES ---
CHROME_DEBUG_PORT = "127.0.0.1:9222"
LATEST_MSG_FILE = "latest_message.md"
COMMAND_FILE = "command_queue.txt"
CWD_FILE = "cwd_state.txt"

# --- TIMING ---
DEFAULT_INTERVAL = 10 * 60
BRIDGE_LOOP_DELAY = 1
CLIPBOARD_TIMEOUT = 5

# --- VOICE SETTINGS ---
VIBEVOICE_URL = "https://e7f79aa8f4c2a79121.gradio.live/" # Update if expired
VOICE_SPEAKER = "Just Keep Your Head Down, - Halo 3"
VOICE_CFG_SCALE = 1.1
DISABLE_CLONE = False

# --- OUTPUT DIRS ---
OUTPUT_AUDIO_DIR = "AudioFiles"
OUTPUT_TEXT_DIR = "TextFiles"  # <--- NEW

# --- VISION ---
MONITORS = 0 # 0 for all monitors. 1, 2, and 3, respectively represent the monitors 'identified' by Windows, in display settings.

# --- NAVIGATION ---
# NEW: The "Home Base" for the AI. Use raw string r"" for Windows paths.
AI_START_DIR = r"D:\GoogleDrive\Core"