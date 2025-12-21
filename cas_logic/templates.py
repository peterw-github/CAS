import datetime

def ts(): return datetime.datetime.now().isoformat(timespec='minutes')

def menu():
    return """```markdown
**Available Commands:**
* `!CAS freq X`
* `!CAS exec [cmd]`
* `!CAS upload [path]`
* `!CAS screenshot`
* `!CAS prompt_now`
* `!CAS stop`
```"""

def format_heartbeat(mins):
    return f"**[CAS HEARTBEAT]**\n`Time: {ts()}`\n`Freq: {mins}m`\n\n**Message:**\nStandard prompt.\n\n{menu()}"

def format_prompt_now(mins):
    return f"**[CAS PROMPT]**\n`Time: {ts()}`\n`Freq: {mins}m`\n\n**Message:**\nImmediate prompt triggered.\n\n{menu()}"

def format_vision(mins):
    return f"**[CAS VISION]**\n`Time: {ts()}`\n`Freq: {mins}m`\n\n**Message:**\nScreenshot attached.\n\n{menu()}"

def format_upload(fname, mins):
    return f"**[CAS UPLOAD]**\n`Time: {ts()}`\n`Freq: {mins}m`\n\n**Message:**\nFile `{fname}` attached.\n\n{menu()}"

def format_result(cmd, out):
    return f"**[CAS RESULT]**\n`CMD: {cmd}`\n```\n{out}\n```"

def format_freq(mins):
    return f"**[CAS SYSTEM]**\n`Frequency set to {mins}m.`\n\n{menu()}"