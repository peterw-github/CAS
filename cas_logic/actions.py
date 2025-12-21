import subprocess

def run_system_command(cmd):
    print(f"[ACTION] Executing: {cmd}")
    try:
        # Sanitize HTML entities
        cmd = cmd.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return (result.stdout + result.stderr).strip() or "[Done]"
    except Exception as e:
        return f"Error: {e}"