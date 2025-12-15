import requests
import json

url = "http://127.0.0.1:5000/calculate"
headers = {"Content-Type": "application/json"}
data = {
    "id": 101, # Chapati
    "quantity": 2,
    "serving_type": "countable"
}

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Verification Successful: Backend accepted POST JSON")
    else:
        print("❌ Verification Failed")
except Exception as e:
    print(f"Error: {e}")
    print("Ensure the server is running!")
