# YouTube Downloader & Audio Processor

This toolkit contains two Python scripts designed to streamline the creation of audio datasets.

1.  **`download_video.py`**: Downloads high-quality video/audio from YouTube.
    
2.  **`convert_to_wav.py`**: Batch converts local video files into `.wav` audio optimized for AI/TTS training (24kHz, 384kbps).
    

## Prerequisites

Before running the scripts, ensure you have the following installed:

1.  **Python 3.x**: [Download Python](https://www.python.org/downloads/ "null")
    
2.  **FFmpeg**: Required for audio processing.
    
    -   _Windows:_ [Download & Install Guide](https://ffmpeg.org/download.html "null") (Ensure it is added to your system PATH).
        
    -   _Mac:_ Install via Homebrew: `brew install ffmpeg`
        
    -   _Linux:_ Install via package manager: `sudo apt install ffmpeg`
        

## Installation

1.  Open your terminal or command prompt in the folder containing the scripts.
    
2.  Install the required Python library for the downloader:
    

    pip install yt-dlp
    

## Usage

### 1\. Download Videos (`download_video.py`)

This script downloads a video from a YouTube URL to the current folder.

**Run:**

    python download_video.py
    

-   You will be prompted to paste a YouTube URL.
    
-   The script attempts to download the best quality format available using `yt-dlp`.
    

### 2\. Convert to Audio (`convert_to_wav.py`)

This script scans the current folder for video files (e.g., `.mp4`, `.mkv`, `.mov`) and converts them to `.wav`.

**Run:**

    python convert_to_wav.py
    

**Technical Specifications:**

The converter is pre-configured with the following settings, which match common requirements for **TTS (Text-to-Speech) model training**:

-   **Format:** `.wav` (PCM 16-bit)
    
-   **Sample Rate:** 24,000 Hz
    
-   **Channels:** Mono (1)
    
-   **Bitrate:** 384 kbps
    
    -   _Calculation:_ `24000 Hz * 16-bit depth * 1 channel = 384,000 bps`
        

_Note: The script outputs Mono audio to strictly adhere to the 384kbps requirement at 24kHz. Stereo would result in 768kbps._

## Troubleshooting

-   **"FFmpeg not found":** If you see this error, FFmpeg is not installed or not added to your system Environment Variables (PATH). Restart your terminal after installing FFmpeg to ensure the changes take effect.
    
-   **Download fails:** YouTube frequently updates their backend. If the downloader stops working, run the following command to get the latest version of the library:
    
        pip install --upgrade yt-dlp

