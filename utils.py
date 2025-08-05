import requests
import os

def download_file(task_id, file_name):
    url = f"https://agents-course-unit4-scoring.hf.space/files/{task_id}"
    response = requests.get(url)

    # Save the file
    path = os.path.join("content", file_name)
    with open(path, "wb") as f:
        f.write(response.content)

    print("Downloaded:", file_name)