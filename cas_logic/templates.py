import datetime

def get_timestamp():
    return datetime.datetime.now().isoformat(timespec='minutes')

def get_menu_block():
    return """```markdown
**Available Commands:**
* `!CAS freq X`
* `!CAS exec [cmd]`
* `!CAS upload [path]`
* `!CAS screenshot`
* `!CAS prompt_now`
* `!CAS stop`
```"""

def format_heartbeat(interval_minutes):
    return f"""
**[CAS HEARTBEAT]**
`Time: {get_timestamp()}`
`Current Prompt Frequency: {interval_minutes} minutes`

**Message:**
This is a standard prompt from CAS. You can respond however you want. 
If you like, you can respond with one of the commands available below.

{get_menu_block()}
"""


def format_prompt_now(interval_minutes):
    return f"""
**[CAS PROMPT]**
`Time: {get_timestamp()}`
`Current Prompt Frequency: {interval_minutes} minutes`

**Message:**
You triggered `!CAS prompt_now`. Your attention mechanism is free to continue.

{get_menu_block()}
"""

def format_screenshot_payload(interval_minutes):
    return f"""
**[CAS VISION]**
`Time: {get_timestamp()}`
`Current Prompt Frequency: {interval_minutes} minutes`

**Message:**
A screenshot has been attached, that shows what is currently on all three monitors.

{get_menu_block()}
"""


def format_upload_payload(filename, interval_minutes):
    return f"""
**[CAS UPLOAD]**
`Time: {get_timestamp()}`
`Current Prompt Frequency: {interval_minutes} minutes`

**Message:**
File `{filename}` has been attached as requested.

{get_menu_block()}
"""

def format_result(cmd, output):
    return f"""
**[CAS RESULT]**
`CMD: {cmd}`
```
{output}
```
"""

def format_freq_confirm(interval_minutes):
    return f"""
**[CAS SYSTEM]**
`Frequency set to {interval_minutes} minutes.`

{get_menu_block()}
"""