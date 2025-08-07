import requests
import os
import re

def download_file(task_id, file_name):
    url = f"https://agents-course-unit4-scoring.hf.space/files/{task_id}"
    response = requests.get(url)

    # Save the file
    path = os.path.join("content", file_name)
    with open(path, "wb") as f:
        f.write(response.content)
    
    print("Downloaded:", file_name)
   
def extract_youtube_url(text):
    # Regular expression to match YouTube URLs
    pattern = r"(https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+)"
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None