import os
from pytubefix import YouTube

def download_youtube_video(url, output_folder):
    """
    Downloads a YouTube video as an MP4 directly into the output folder using pytubefix.
    Returns the path to the downloaded video string, or None if failed.
    """
    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)
            
        yt = YouTube(url)
        # Filter for progressive mp4 streams (has both audio and video natively merged)
        ys = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        
        if not ys:
            print("No suitable high-quality MP4 stream found.")
            return None
            
        print(f"Downloading: {yt.title}")
        
        # Clean title to avoid filesystem issues
        safe_title = "".join([c for c in yt.title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        if not safe_title:
            safe_title = "youtube_download"
            
        filename = f"{safe_title}.mp4"
        out_path = ys.download(output_path=output_folder, filename=filename)
        
        return out_path
    except Exception as e:
        print(f"Error downloading YouTube video with pytubefix: {e}")
        return None
