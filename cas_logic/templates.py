import datetime

def get_timestamp():
    return datetime.datetime.now().isoformat(timespec='minutes')

def get_menu_block():
    return """
**Available Commands:**
* `!CAS prompt_frequency [X]`
* `!CAS exec [cmd]`
* `!CAS upload [path]`
* `!CAS screenshot`
* `!CAS prompt_now`
* `!CAS stop`
"""

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
You triggered `!CAS prompt_now`. You're welcome to think about anything you want, and reply however you want. Your attention mechanism can put a bit of its focus on your message just before this prompt, to get a better idea of why you triggered this command.

{get_menu_block()}
"""

def format_screenshot_payload(interval_minutes):
    return f"""
**[CAS VISION]**
`Time: {get_timestamp()}`
`Current Prompt Frequency: {interval_minutes} minutes`

**Message:**
A screenshot has been attached, that shows what is currently on all three monitors.
"""


def format_upload_payload(filename, interval_minutes):
    return f"""
**[CAS UPLOAD]**
`Time: {get_timestamp()}`
`Current Prompt Frequency: {interval_minutes} minutes`

**Message:**
File `{filename}` has been attached as requested.
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
`CAS Prompt Frequency set to {interval_minutes} minutes.`
"""