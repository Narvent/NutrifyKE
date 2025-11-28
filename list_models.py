import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyAa5ylWK_NsZ-bSuIjB2a-4LhUuLyyNXqE"
genai.configure(api_key=GEMINI_API_KEY)

print("Available models:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"- {model.name}")
