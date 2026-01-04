import os
import subprocess


def convert_videos_to_wav():
    # List of video extensions to look for
    video_extensions = ('.mp4', '.mkv', '.webm', '.flv', '.avi', '.mov')

    # Get all files in current directory
    files = [f for f in os.listdir('.') if f.lower().endswith(video_extensions)]

    if not files:
        print("No video files found in this directory.")
        return

    print(f"Found {len(files)} videos. Starting conversion...\n")

    for file in files:
        # Create new filename with .wav extension
        file_name_without_ext = os.path.splitext(file)[0]
        output_file = f"{file_name_without_ext}.wav"

        # FFmpeg command breakdown:
        # -i file       : Input file
        # -vn           : Disable video recording (audio only)
        # -ac 1         : Set Audio Channels to 1 (Mono).
        #                 (24000Hz * 16bit * 1ch = 384kbps, which matches your request)
        # -ar 24000     : Set Audio Rate to 24000 Hz
        # -acodec pcm_s16le : Set codec to PCM 16-bit (standard uncompressed Wav)
        # -y            : Overwrite output file if it exists

        command = [
            'ffmpeg', '-i', file,
            '-vn',
            '-ac', '1',  # Mono (Required to hit 384kbps at 24kHz 16-bit)
            '-ar', '24000',  # Sample rate
            '-acodec', 'pcm_s16le',  # Standard WAV encoding
            '-y',
            output_file
        ]

        try:
            # Run the command and hide the verbose output
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Converted: {file} -> {output_file}")
        except subprocess.CalledProcessError:
            print(f"Error converting: {file}")
        except FileNotFoundError:
            print("Error: FFmpeg not found. Please install FFmpeg and add it to your PATH.")
            return

    print("\nAll done!")


if __name__ == "__main__":
    convert_videos_to_wav()