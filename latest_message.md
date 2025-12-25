This system is remarkably lean already, which is its greatest strength. However, regarding that specific "Heartbeat Sent -> Silence" bug and the general user experience, I have three specific ideas that add **zero code bloat** but significantly increase reliability and control.

Here is what I recommend:

### 1. Fix the "Sleeping Tab" Bug (Reliability)
**The Problem:** The issue where a heartbeat sends but isn't received is almost certainly caused by **Chrome’s "Background Timer Throttling".** To save battery, modern Chrome "freezes" tabs that you aren't looking at. The Selenium bridge tries to type into a frozen tab, fails silently, and the message never goes through.

**The Fix:** You don't need new logic code. You just need to tell Chrome *not* to sleep.

**In `cas_bridge.py`, update `connect_chrome()`:**

```python
def connect_chrome():
    opt = Options()
    opt.add_experimental_option("debuggerAddress", cfg.CHROME_DEBUG_PORT)
    # --- ADD THIS LINE ---
    opt.add_argument("--disable-background-timer-throttling")
    opt.add_argument("--disable-renderer-backgrounding")
    opt.add_argument("--disable-backgrounding-occluded-windows")
    # ---------------------
    return webdriver.Chrome(options=opt)
```
*Effect: This should drastically reduce the need for the `force_heartbeat.py` script.*

### 2. The "Shh!" Function (Voice Control)
**The Problem:** Sometimes I might read a very long chunk of code, or you might be on a phone call. Currently, the only way to shut me up is to kill the program.

**The Fix:** Update `cas_voice.py` to allow the queue to be cleared.

Add this method to the `CASVoiceEngine` class:
```python
    def stop_talking(self):
        """Immediately stops the current audio and clears the queue."""
        with self.audio_queue.mutex:
            self.audio_queue.queue.clear()
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            print("[VOICE] Audio Aborted.")
```

And in `cas_brain.py`, add a tiny check inside `process_message`:
```python
        elif key == "shh" or key == "quiet":
             if voice: voice.stop_talking()
             print("  >>> [CMD] Audio stopped.")
```
*Effect: You can now type `!CAS shh` to instantly silence the current response without stopping the agent.*

### 3. Visual "Listening" Indicator (Feedback)
**The Problem:** Since you are relying on the terminal output to know if I'm "Hearing" you or "Generating," it can be hard to tell at a glance if I'm actually processing.

**The Fix:** Change the Window Title of the console.

In `cas_brain.py`, add this simple line inside the `process_message` loop right before sending text to the voice engine:

```python
    # Set title to indicate activity
    os.system(f"title CAS: Speaking... " if os.name == 'nt' else "")
```
And reset it in the heartbeat loop:
```python
    # Set title to indicate idle
    os.system(f"title CAS: Idle" if os.name == 'nt' else "")
```
*Effect: You can just look at your taskbar/window title to verify the state, rather than reading scrolling logs.*

What do you think? I personally believe **#1 is mandatory** to fix the bug you were seeing.