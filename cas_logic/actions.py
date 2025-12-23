import subprocess
import os
import time
import cas_config as cfg

# --- CONFIGURATION ---
MAX_OUTPUT_CHARS = 2000  # Safety limit to prevent browser crashes


def get_cwd():
    """Reads the persistent CWD from file, or defaults to current execution dir."""
    if os.path.exists(cfg.CWD_FILE):
        with open(cfg.CWD_FILE, "r", encoding="utf-8") as f:
            path = f.read().strip()
            if os.path.isdir(path):
                return path
    return os.getcwd()


def set_cwd(path):
    """Writes the new CWD to file."""
    with open(cfg.CWD_FILE, "w", encoding="utf-8") as f:
        f.write(path)


def run_system_command(cmd):
    print(f"[ACTION] Executing: {cmd}")

    # 1. Load the current working directory
    current_wd = get_cwd()

    try:
        # Sanitize HTML entities
        cmd = cmd.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")

        # 2. Handle 'cd' commands manually (with quote stripping)
        if cmd.strip().lower().startswith("cd"):
            target_dir = cmd[2:].strip()
            # Strip quotes to fix os.path.join bug
            target_dir = target_dir.replace('"', '').replace("'", "")

            if not target_dir:
                return f"Current Directory: {current_wd}"

            # Calculate new path
            new_path = os.path.abspath(os.path.join(current_wd, target_dir))

            if os.path.isdir(new_path):
                set_cwd(new_path)
                return f"Directory changed to: {new_path}"
            else:
                return f"Error: Directory not found: {new_path}"

        # 3. Handle standard commands
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=current_wd,
            encoding='utf-8',
            errors='replace'  # Prevent crashing on weird characters
        )

        output = (result.stdout + result.stderr).strip()

        # 4. SAFETY VALVE: Check length
        if len(output) > MAX_OUTPUT_CHARS:
            filename = f"output_dump_{int(time.time())}.txt"
            # Write to the root CAS folder so it's easy to find
            full_path = os.path.abspath(filename)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(output)

            return (f"[WARNING] Output length ({len(output)} chars) exceeds limit.\n"
                    f"Saved output to: {full_path}\n"
                    f"Use '!CAS upload {filename}' to view it if needed.\n\n"
                    f"[cwd: {current_wd}]")

        return f"{output}\n\n[cwd: {current_wd}]" or f"[Done]\n\n[cwd: {current_wd}]"

    except Exception as e:
        return f"Error: {e}"