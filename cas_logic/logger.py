import os
import datetime
import cas_config as cfg

# Files to manage
JOURNAL_FILE = os.path.join(cfg.AI_START_DIR, "journal.md")
CRITICAL_FILE = os.path.join(cfg.AI_START_DIR, "critical_context.md")


def _append_to_file(filepath, content, header):
    """
    Generic appender with timestamp and formatting.
    Creates file if not exists.
    """
    # Ensure dir exists (it should, but safety first)
    folder = os.path.dirname(filepath)
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    formatted_entry = f"\n\n---\n**[{header}] {timestamp}**\n{content}\n"

    try:
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(formatted_entry)
        return True, f"Written to {os.path.basename(filepath)}"
    except Exception as e:
        return False, f"Error writing log: {e}"


def write_journal(content):
    return _append_to_file(JOURNAL_FILE, content, "JOURNAL ENTRY")


def write_critical(content):
    return _append_to_file(CRITICAL_FILE, content, "CRITICAL MEMORY")