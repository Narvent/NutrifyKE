
import json

try:
    with open('food_data.json', 'r') as f:
        data = json.load(f)
        
    for item in data:
        if item.get('serving_type') == 'composite':
            print(f"Found Composite: ID={item['id']}, Name='{item['name']}'")
            print(json.dumps(item, indent=2))
            break
            
except Exception as e:
    print(f"Error: {e}")
