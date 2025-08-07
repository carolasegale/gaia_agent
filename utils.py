import requests
import os
from pytubefix import YouTube
from pytubefix.cli import on_progress
import re

def download_file(task_id, file_name):
    url = f"https://agents-course-unit4-scoring.hf.space/files/{task_id}"
    response = requests.get(url)

    # Save the file
    path = os.path.join("content", file_name)
    with open(path, "wb") as f:
        f.write(response.content)
    
    print("Downloaded:", file_name)

def download_youtube_video(url, output_path = "content/"):
    try:
        yt = YouTube(url, on_progress_callback = on_progress)
        print(yt.title)
        
        ys = yt.streams.get_highest_resolution()
        ys.download(output_path)
        print(f"Video '{yt.title}.mp4' downloaded successfully!")
        print(os.listdir(output_path))
        return f"{yt.title}.mp4"
    except Exception as e:
        return str(e)
    
def extract_youtube_url(text):
    # Regular expression to match YouTube URLs
    pattern = r"(https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+)"
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None