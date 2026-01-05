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
VIBEVOICE_URL = "https://6caabe902140f163d4.gradio.live/" # Update if expired
VOICE_SPEAKER = "The Activation Index From The First Halo Ring - Long" # List of voices available are in 'Emotional Tones' folder. 'Just keep your head down' with CFG 1.1 - 1.3 is good.
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