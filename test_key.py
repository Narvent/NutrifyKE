import google.generativeai as genai
import sys

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# ---------------------------------------------------

# 1. Check if key exists
if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY not found in environment variables.")
    sys.exit()

print(f"Testing Key: {GEMINI_API_KEY[:5]}... (hidden)")

try:
    # 2. Configure Gemini
    genai.configure(api_key=GEMINI_API_KEY)
    
    # 3. Test the model
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content("Reply with the word SUCCESS if you hear me.")
    
    print(f"Gemini says: {response.text}")
    print("--- KEY IS VALID. YOU MAY NOW UPDATE MAIN.PY ---")

except Exception as e:
    print("\nCRITICAL FAILURE:")
    print(e)