import requests

def download_file(task_id, file_name):
    url = f"https://agents-course-unit4-scoring.hf.space/files/{task_id}"
    response = requests.get(url)

    # Save the file
    with open('/content/'+file_name, "wb") as f:
        f.write(response.content)

    print("Downloaded:", file_name)