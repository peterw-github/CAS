import datetime
from textwrap import dedent

def get_timestamp():
    return datetime.datetime.now().isoformat(timespec='minutes')


# --- Regular Heartbeat ---
def format_heartbeat(interval_minutes):
    return dedent(f"""
            **[CAS HEARTBEAT]**
            `Time: {get_timestamp()}`
            `Current Prompt Frequency: {interval_minutes} minutes`
            `!CAS help` for available features.
            """).strip()


# --- Other Actions ---

def format_screenshot_payload(interval_minutes): # Arg kept for compatibility, but unused
    return dedent(f"""
            **[CAS VISION]**
            A screenshot has been attached, that shows what is currently on all three monitors.
            """).strip()

def format_upload_payload(filename, interval_minutes): # Arg kept for compatibility, but unused
    return dedent(f"""
            **[CAS UPLOAD]**
            File `{filename}` has been attached as requested.
            """).strip()

def format_result(cmd, output):
    return dedent(f"""
            **[CAS RESULT]**
            `CMD: {cmd}`
            ```
            {output}
            ```
            """).strip()

def format_freq_confirm(interval_minutes):
    return dedent(f"""
            **[CAS SYSTEM]**
            Frequency updated to {interval_minutes} minutes.
            """).strip()

def format_prompt_now(interval_minutes):
    return dedent(f"""
            **[CAS PROMPT]**
            `Time: {get_timestamp()}`
            `Current Prompt Frequency: {interval_minutes} minutes`
            
            **Message:**
            You triggered `!CAS prompt_now`. You're welcome to think about anything you want, and reply however you want. Your attention mechanism can put a bit of its focus on your message just before this prompt, to get a better idea of why you triggered this command.
            """).strip()


