import sys, os
from src.core.config import ConfigManager
from google import genai
from google.genai import types
import traceback

try:
    client = genai.Client(api_key=ConfigManager().get_api_key())
    resp = client.models.generate_content(
        model='gemini-3.1-pro-preview',
        contents='test JSON generation: return {"style_parameters": {"k": "v"}}',
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            response_schema={'type': 'OBJECT', 'properties': {'style_parameters': {'type': 'OBJECT'}}, 'required': ['style_parameters']}
        )
    )
    print("RES:", resp.text)
except Exception as e:
    traceback.print_exc()
