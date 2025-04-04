import os
import PIL.Image
from google import genai
from google.genai import types
from google.genai.types import Part
from dotenv import load_dotenv

load_dotenv()


client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=["How does AI work?"],
    config=types.GenerateContentConfig(
            max_output_tokens=200,
    ),
)
print(response.text)

