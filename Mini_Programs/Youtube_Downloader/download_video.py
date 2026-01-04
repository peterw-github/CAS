import yt_dlp


def download_video(url):
    # Options for the downloader
    ydl_opts = {
        # 'best' selects the best quality format that contains both video and audio.
        # If you have FFmpeg installed, you can change this to 'bestvideo+bestaudio/best'
        'format': 'best',

        # This names the file using the video title
        'outtmpl': '%(title)s.%(ext)s',

        # This prevents the script from stopping if it hits a minor error
        'ignoreerrors': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading: {url}...")
            ydl.download([url])
            print("\nDownload complete!")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    video_url = input("Enter the YouTube URL: ")
    download_video(video_url)