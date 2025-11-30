import google.generativeai as genai
from PIL import Image
import requests
from io import BytesIO

import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

print("Testing gemini-3-pro-preview model...")

try:
    model = genai.GenerativeModel('gemini-3-pro-preview')
    
    # Download a test food image
    url = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400"
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    
    prompt = "What food is in this image? Be specific."
    result = model.generate_content([prompt, img])
    
    print("SUCCESS! Model works!")
    print(f"AI Response: {result.text}")
    
except Exception as e:
    print(f"FAILED: {e}")
    print("\nTrying gemini-3-pro-preview (fallback) instead...")
    
    try:
        model = genai.GenerativeModel('gemini-3-pro-preview')
        result = model.generate_content([prompt, img])
        print("gemini-3-pro-preview works!")
        print(f"AI Response: {result.text}")
    except Exception as e2:
        print(f"Also failed: {e2}")
