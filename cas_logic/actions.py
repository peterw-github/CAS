import subprocess


def run_system_command(cmd):
    """Executes a shell command and returns output."""
    print(f"[ACTION] Executing: {cmd}")
    try:
        # Basic HTML unescape for safety
        cmd = cmd.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        output = (result.stdout + result.stderr).strip()
        return output if output else "[Done]"
    except Exception as e:
        return f"Error executing command: {e}"