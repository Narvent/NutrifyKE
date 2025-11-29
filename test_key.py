import google.generativeai as genai
import sys

# --- PASTE YOUR REAL KEY INSIDE THE QUOTES BELOW ---
GEMINI_API_KEY = "AIzaSyDkPpbplBpJY8IsjDzH5f-LBQH_kj_hUQ4" 

# ---------------------------------------------------

# 1. Check if you actually followed instructions
if GEMINI_API_KEY == "":
    print("ERROR: The variable GEMINI_API_KEY is empty.")
    print("You must paste your AIza... key inside the quotes on line 5.")
    sys.exit()

print(f"Testing Key: {GEMINI_API_KEY[:5]}... (hidden)")

try:
    # 2. Configure Gemini with YOUR variable name
    genai.configure(api_key=GEMINI_API_KEY)
    
    # 3. Test the model
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content("Reply with the word SUCCESS if you hear me.")
    
    print(f"Gemini says: {response.text}")
    print("--- KEY IS VALID. YOU MAY NOW UPDATE MAIN.PY ---")

except Exception as e:
    print("\nCRITICAL FAILURE:")
    print(e)