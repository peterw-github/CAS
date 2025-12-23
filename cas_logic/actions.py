import subprocess
import os
import cas_config as cfg


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
        cmd = cmd.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")

        # --- QUOTE STRIPPING FOR CD ---
        if cmd.strip().lower().startswith("cd"):
            # Remove "cd"
            target_dir = cmd[2:].strip()
            # Remove quotes
            target_dir = target_dir.replace('"', '').replace("'", "")

            if not target_dir:
                return f"Current Directory: {current_wd}"

            # Now os.path.join handles it correctly even with spaces
            new_path = os.path.abspath(os.path.join(current_wd, target_dir))

            if os.path.isdir(new_path):
                set_cwd(new_path)
                return f"Directory changed to: {new_path}"
            else:
                return f"Error: Directory not found: {new_path}"

        # 3. Handle standard commands
        # We pass 'cwd=current_wd' so the command runs where we expect it to.
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=current_wd  # <--- The magic argument
        )

        output = (result.stdout + result.stderr).strip()

        # Add a helpful footer showing where we are
        return f"{output}\n\n[cwd: {current_wd}]" or f"[Done]\n\n[cwd: {current_wd}]"

    except Exception as e:
        return f"Error: {e}"