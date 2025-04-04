import os
import PIL.Image
from google import genai
from google.genai.types import Part
from dotenv import load_dotenv

load_dotenv()


client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
pil_image = PIL.Image.open("images/sample_image.jpg")
response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents=[
        "What is shown in this image in Thai?",
        pil_image,
    ],
)
print(response.text)
