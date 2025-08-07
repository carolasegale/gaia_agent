# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
#from youtube_transcript_api import YouTubeTranscriptApi
from llama_index.core import Document
import whisper
import subprocess
import base64
from PIL import Image
from llama_index.core.tools import FunctionTool

# calculator tool
def calculate(input: dict) -> dict:
    """Simple calculator function"""

    expression = input['input']

    # Remove any potentially unsafe operations
    if any(unsafe in expression for unsafe in ["import", "exec", "eval", "compile", "open", "__"]):
        return {"error": "Unsafe expression"}

    try:
        # Use a safer approach to evaluate mathematical expressions
        # This is a simplified version - in production you'd want more safeguards
        allowed_symbols = {
            'sqrt': np.sqrt, 'pi': np.pi, 'e': np.e,
            'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
            'log': np.log, 'log10': np.log10, 'exp': np.exp,
            'floor': np.floor, 'ceil': np.ceil, 'abs': abs
        }

        # Replace common math operations with Python syntax
        expression = expression.replace('^', '**')
        result = eval(expression, {"__builtins__": {}}, allowed_symbols)
        return {"result": str(result)}
    except Exception as e:
        return {"error": f"Failed to calculate: {str(e)}"}

'''
# youtube tool --> eight now this does not work with free resources
def get_youtube_transcript(input: dict) -> dict:
    """Fetch transcript from YouTube based on video ID."""

    url = input['file_name']
    video_id = url.split("v=")[-1]

    try:
        ytt_api = YouTubeTranscriptApi()
        fetched_transcript = ytt_api.fetch(video_id) 
        text = "\n".join([t["text"] for t in fetched_transcript])
        document = Document(text=text)
        return {'result': document.text}
    except Exception as e:
        return {'error': f"Failed to fetch transcript: {str(e)}"}
'''

# audio tool
def get_audio_transcript(file_path: str, model_whisper=None) -> dict:
    """Transcribe audio file .mp3 or .mp4 and return the text."""

    if model_whisper is None:
        model_whisper = whisper.load_model("base")  # fallback, but shouldn't be used
    try:
        r = model_whisper.transcribe(file_path)
        return {"result": Document(text=r["text"]).text}
    except Exception as e:
        return {"error": str(e)}

# python file execution tool
def run_python_file(file_path: str) -> dict:
    """Runs a Python script in memory only and returns its final printed output. Takes as input:
        file_path = "path/to/code.py"
    """

    try:        
        result = subprocess.run(
            ["python", file_path],
            capture_output=True,
            text=True
        )
        output = result.stdout.strip()
        error = result.stderr.strip()

        if result.returncode != 0:# or 'error' in output.lower():
            return {'error': f"Script error:\n{error}"}

        last_output = output.split('\n')[-1]

        return {'result': f"Whole output of python code in {file_path}: '{output}'. Final numeric output: {last_output}"}

    except Exception as e:
        return {'error': f"Execution failed: {str(e)}"}

# Excel tool
def get_info_from_excel(file_path: str) -> dict:
    """Fetch information from an Excel file and output it in markdown table."""

    try:
        df = pd.read_excel(file_path)
        text = df.to_markdown()  # Convert DataFrame to Markdown for better readability
        document = Document(text=text)
        return {'result': document.text}
    except Exception as e:
        return {'error': f"Failed to fetch data from Excel: {str(e)}"}
    
# Image tool
def image_and_video_parser_tool(client_vision):

    def parse_image_or_video(input: dict) -> dict:
        """
        Tool wrapper that takes:
        input = {
            "file_path": "path/to/image_or_video, # image.png or video.mp4
            "input": "your question"
        }
        """
        file_path = input["file_path"]
        query = input["input"]

        
        myfile = client_vision.files.upload(file=file_path)

        try:
            response = client_vision.models.generate_content(
                model='gemini-2.5-pro',
                contents=[
                    myfile,
                    query,
                ]
            )
            return {"result": response.text}
        except Exception as e:
            return {"error": str(e)}

    return FunctionTool.from_defaults(
        fn=parse_image_or_video,
        name="image_and_video_parser",
        description="Answer queries based on image or video content using Gemini 2.5 Vision."
    )

