from google import genai
from google.genai import types
import httpx
import os
from dotenv import load_dotenv

load_dotenv()


client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

doc_url = "https://secdocumentstorage.blob.core.windows.net/fundfactsheet/M0370_2563.pdf"  

# Retrieve and encode the PDF byte
doc_data = httpx.get(doc_url).content

prompt = "Summarize this document in Thai"
response = client.models.generate_content(
  model="gemini-1.5-flash",
  contents=[
      types.Part.from_bytes(
        data=doc_data,
        mime_type='application/pdf',
      ),
      prompt])
print(response.text)