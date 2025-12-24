import subprocess
import os
import time
import cas_config as cfg

# --- CONFIGURATION ---
MAX_OUTPUT_CHARS = 2000  # Safety limit



def set_cwd(path):
    """Writes the new CWD to file."""
    with open(cfg.CWD_FILE, "w", encoding="utf-8") as f:
        f.write(path)



def get_cwd():
    """Reads the persistent CWD from file, or defaults to current execution dir."""
    if os.path.exists(cfg.CWD_FILE):
        try:
            with open(cfg.CWD_FILE, "r", encoding="utf-8") as f:
                path = f.read().strip()
                if os.path.isdir(path):
                    return path
        except:
            pass
    return os.getcwd()



def run_system_command(cmd):
    print(f"[ACTION] Executing: {cmd}")
    current_wd = get_cwd()

    # Use a safe marker with no special shell characters
    marker = "CAS_FOLDER_SYNC"
    wrapped_cmd = f'{cmd} && echo {marker} && cd'

    try:
        # Sanitize
        cmd = cmd.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")

        result = subprocess.run(
            wrapped_cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=current_wd,
            encoding='utf-8',
            errors='replace'
        )

        full_output = (result.stdout + result.stderr).strip()

        # 1. Parse the new CWD from the output
        if marker in full_output:
            parts = full_output.split(marker)
            clean_output = parts[0].strip()
            new_path = parts[1].strip()

            # 2. Update the state file safely from Python
            if os.path.isdir(new_path):
                set_cwd(new_path)
                status_tag = f"[cwd: {new_path}]"
            else:
                status_tag = f"[cwd: {current_wd}] (Path update failed)"
        else:
            # If the command failed, the marker might not be reached
            clean_output = full_output
            status_tag = f"[cwd: {current_wd}]"

        # 3. SAFETY VALVE: Output length
        if len(clean_output) > MAX_OUTPUT_CHARS:
            filename = f"output_dump_{int(time.time())}.txt"
            with open(os.path.abspath(filename), "w", encoding="utf-8") as f:
                f.write(clean_output)
            return f"[WARNING] Output too long. Saved to {filename}\n\n{status_tag}"

        return f"{clean_output}\n\n{status_tag}" if clean_output else status_tag

    except Exception as e:
        return f"Error: {e}"