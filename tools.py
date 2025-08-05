# -*- coding: utf-8 -*-

import pandas as pd
import json
import random
import os
import numpy as np
#from youtube_transcript_api import YouTubeTranscriptApi
from llama_index.core import Document
import whisper
import io
import contextlib


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
    if model_whisper is None:
        model_whisper = whisper.load_model("base")  # fallback, but shouldn't be used
    try:
        r = model_whisper.transcribe(file_path)
        return {"result": Document(text=r["text"]).text}
    except Exception as e:
        return {"error": str(e)}

# python file execution tool
def run_python_file(file_path: str) -> dict:
    """Safely runs a Python script and returns its final printed numeric output."""

    try:
        python_code = open(file_path).read()

        # Create a buffer to capture stdout
        buffer = io.StringIO()

        # Redirect stdout to the buffer
        with contextlib.redirect_stdout(buffer):
            exec(python_code)

        # Get everything that was printed in the script
        output = buffer.getvalue()
        print(output)
        last_output = output.split('\n')[-2]

        if 'error' in output.lower():
            return {'error': f"Error running script:\n{output}"}

        return {'result': f" Whole output: '{output}'. Final numeric output: {last_output}"}

    except Exception as e:
        return {'error': f"Execution failed: {str(e)}"}

# Excel tool
def get_info_from_excel(file_path: str) -> dict:
    """Fetch information from an Excel file."""

    try:
        df = pd.read_excel(file_path)
        text = df.to_markdown()  # Convert DataFrame to Markdown for better readability
        document = Document(text=text)
        return {'result': document.text}
    except Exception as e:
        return {'error': f"Failed to fetch data from Excel: {str(e)}"}

