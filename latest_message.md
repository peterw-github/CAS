Understood. You want a "Raw Mode" for the voice, where it reads absolutely everything (actions, commands, weird headers) *except* for the actual code blocks.

Here is the updated `cas_voice.py`.

I have simplified `_clean_text` to **only** target the triple backticks (` ``` `).

```python
import threading
import queue
import os
import re
import datetime
import numpy as np
import sounddevice as sd
import soundfile as sf
from gradio_client import Client
import cas_config as cfg

class CASVoiceEngine:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.playback_finished = threading.Event()
        self.client = None
        self.stream = None
        
        # Ensure output dirs exist
        os.makedirs(cfg.OUTPUT_AUDIO_DIR, exist_ok=True)
        os.makedirs(cfg.OUTPUT_TEXT_DIR, exist_ok=True)

        # Start the background audio thread
        self.thread = threading.Thread(target=self._playback_thread_func, daemon=True)
        self.thread.start()

        # Connect to Gradio
        print(f"[VOICE] Connecting to VibeVoice at {cfg.VIBEVOICE_URL}...")
        try:
            self.client = Client(cfg.VIBEVOICE_URL)
            print("[VOICE] Connected.")
        except Exception as e:
            print(f"[VOICE] Connection Failed (Running in Text-Only Mode): {e}")

    def _playback_thread_func(self):
        """Continuous audio stream handler running in background."""
        while not self.playback_finished.is_set():
            try:
                data, fs = self.audio_queue.get(timeout=0.5)
                if self.stream is None:
                    self.stream = sd.OutputStream(
                        samplerate=fs,
                        channels=data.shape[1] if len(data.shape) > 1 else 1,
                        dtype='float32'
                    )
                    self.stream.start()
                self.stream.write(data)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[VOICE] Playback Error: {e}")
                if self.stream:
                    self.stream.stop()
                    self.stream.close()
                    self.stream = None

    def _clean_text(self, text):
        """
        MINIMAL CLEANUP:
        1. Identifies content between triple backticks (```) and replaces it with "[Code Block]".
        2. Preserves EVERYTHING else (Actions *sigh*, Commands !CAS, Headers, etc).
        """
        # Regex to find ``` (anything) ``` including newlines
        text = re.sub(r"```.*?```", " [Code Block] ", text, flags=re.DOTALL)
        
        # Basic whitespace normalization (optional, but prevents long silences)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

    def _save_text_log(self, text):
        """Saves the CLEANED text to the TextFiles folder as Markdown."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(cfg.OUTPUT_TEXT_DIR, f"speech_{timestamp}.md")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception as e:
            print(f"[VOICE] Failed to save text log: {e}")

    def speak(self, text):
        """Public method to trigger speech."""
        if not self.client:
            return

        clean_text = self._clean_text(text)
        if not clean_text: 
            return

        self._save_text_log(clean_text)

        print(f"[VOICE] Generating: {clean_text[:50]}...")
        
        t = threading.Thread(target=self._generate_and_queue, args=(clean_text,))
        t.start()

    def _generate_and_queue(self, text):
        try:
            job = self.client.submit(
                num_speakers=1,
                script=text,
                speaker_1=cfg.VOICE_SPEAKER,
                speaker_2="en-Frank_man", 
                speaker_3=None,
                speaker_4=None,
                cfg_scale=cfg.VOICE_CFG_SCALE,
                disable_voice_cloning=cfg.DISABLE_CLONE,
                api_name="/generate_stream"
            )
            
            full_audio_buffer = []
            sample_rate = 24000

            for output_file in job:
                if output_file:
                    data, fs = sf.read(output_file, dtype='float32')
                    sample_rate = fs
                    self.audio_queue.put((data, fs))
                    full_audio_buffer.append(data)
            
            if full_audio_buffer:
                full_audio = np.concatenate(full_audio_buffer)
                ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                sf.write(os.path.join(cfg.OUTPUT_AUDIO_DIR, f"tts_{ts}.wav"), full_audio, sample_rate)

        except Exception as e:
            print(f"[VOICE] Generation Error: {e}")

    def shutdown(self):
        self.playback_finished.set()
```