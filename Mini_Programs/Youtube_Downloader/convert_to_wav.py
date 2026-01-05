import os
import subprocess


def convert_media_to_wav():
    # Extended list to include both VIDEO and AUDIO formats
    extensions = ('.mp4', '.mkv', '.webm', '.flv', '.avi', '.mov',
                  '.wav', '.mp3', '.flac', '.ogg', '.m4a')

    # Create an output folder to prevent overwriting original files
    output_folder = "converted_audio"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get all files in current directory
    files = [f for f in os.listdir('.') if f.lower().endswith(extensions)]

    if not files:
        print("No media files found in this directory.")
        return

    print(f"Found {len(files)} files. Converting to {output_folder}/...\n")

    for file in files:
        # Create output path
        file_name_without_ext = os.path.splitext(file)[0]
        output_path = os.path.join(output_folder, f"{file_name_without_ext}.wav")

        # FFmpeg command
        command = [
            'ffmpeg', '-i', file,
            '-vn',  # Disable video (if present)
            '-ac', '1',  # Force Mono
            '-ar', '24000',  # Resample to 24kHz
            '-acodec', 'pcm_s16le',  # Standard WAV
            '-y',  # Overwrite if exists in output folder
            output_path
        ]

        try:
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Processed: {file} -> {output_path}")
        except subprocess.CalledProcessError:
            print(f"Error converting: {file}")
        except FileNotFoundError:
            print("Error: FFmpeg not found.")
            return

    print(f"\nAll done! Check the '{output_folder}' folder.")


if __name__ == "__main__":
    convert_media_to_wav()