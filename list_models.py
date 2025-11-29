import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyDkPpbplBpJY8IsjDzH5f-LBQH_kj_hUQ4"
genai.configure(api_key=GEMINI_API_KEY)

print("Available models:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"- {model.name}")
