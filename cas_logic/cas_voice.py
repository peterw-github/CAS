import threading
import queue
import os
import re
import datetime
import time
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
        """
        Robust playback loop.
        It waits for a few chunks to buffer before starting to ensure smooth playback.
        """
        buffer = []
        BUFFER_SIZE = 2  # Wait for 2 chunks before playing (reduces "cutting out")

        while not self.playback_finished.is_set():
            try:
                # 1. Get Data
                data, fs = self.audio_queue.get(timeout=0.5)

                # 2. Add to local small buffer
                buffer.append(data)

                # 3. If we haven't started streaming yet, wait for buffer to fill
                #    (Unless the queue is empty, meaning that's all the audio there is)
                if self.stream is None and len(buffer) < BUFFER_SIZE and not self.audio_queue.empty():
                    continue

                # 4. Play what we have
                while buffer:
                    chunk = buffer.pop(0)

                    # Initialize Stream if needed
                    if self.stream is None:
                        try:
                            self.stream = sd.OutputStream(
                                samplerate=fs,
                                channels=chunk.shape[1] if len(chunk.shape) > 1 else 1,
                                dtype='float32'
                            )
                            self.stream.start()
                            print("[VOICE] Audio Stream Started.")
                        except Exception as e:
                            print(f"[VOICE] Stream Init Error: {e}")
                            continue

                    # Write to hardware
                    try:
                        self.stream.write(chunk)
                    except Exception as e:
                        print(f"[VOICE] Write Error (Recovering): {e}")
                        # Try to reset stream
                        if self.stream:
                            self.stream.close()
                            self.stream = None

            except queue.Empty:
                # If queue is empty, just loop.
                # The stream stays open to avoid popping, unless we want to close it.
                continue
            except Exception as e:
                print(f"[VOICE] Critical Playback Error: {e}")

    def _clean_text(self, text):
        # 1. Remove Code Blocks (replace with space)
        text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)

        # 2. Collapse all horizontal whitespace (tabs/spaces) to single space
        text = re.sub(r'[^\S\r\n]+', ' ', text)

        # 3. Check for the Toggle
        use_smart_merge = getattr(cfg, 'VOICE_SMART_MERGE', False)

        if use_smart_merge:
            # --- MODE A: SMART MERGE (The new behavior) ---
            # 1. Normalize line endings
            text = text.replace('\r\n', '\n')

            # 2. Handle MAJOR breaks (3 empty lines = 4 newlines)
            #    Protect them by turning them into a placeholder
            text = re.sub(r'\n{4,}', '<<MAJOR_BREAK>>', text)

            # 3. Merge everything else (standard paragraphs) into a single line
            text = re.sub(r'\n+', ' ', text)

            # 4. Restore the MAJOR breaks as a single empty line (\n\n)
            text = text.replace('<<MAJOR_BREAK>>', '\n\n')

        else:
            # --- MODE B: LEGACY BEHAVIOR (Your original logic) ---
            spacing = getattr(cfg, 'VOICE_PARAGRAPH_SPACING', 1)

            if spacing == 0:
                # Merge all paragraphs
                text = re.sub(r'\n+', ' ', text)
            else:
                # Replace any chunk of newlines with exactly X newlines
                replacement = "\n" * spacing
                text = re.sub(r'\n+', replacement, text)

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

        print(f"[VOICE] Generating ({len(clean_text)} chars)...")

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
            chunk_count = 0

            for output_file in job:
                if output_file:
                    chunk_count += 1
                    data, fs = sf.read(output_file, dtype='float32')
                    sample_rate = fs

                    # Send to player
                    self.audio_queue.put((data, fs))

                    # Store for saving
                    full_audio_buffer.append(data)
                    print(f"[VOICE DEBUG] Chunk {chunk_count} received ({len(data)} samples)")

            print(f"[VOICE] Generation Complete. Total Chunks: {chunk_count}")

            # Save full file
            if full_audio_buffer:
                full_audio = np.concatenate(full_audio_buffer)
                ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                sf.write(os.path.join(cfg.OUTPUT_AUDIO_DIR, f"tts_{ts}.wav"), full_audio, sample_rate)

        except Exception as e:
            print(f"[VOICE] Generation Error: {e}")

    def shutdown(self):
        self.playback_finished.set()