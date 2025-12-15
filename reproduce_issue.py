
import utils
import json

# Load data
utils.load_data()

# Test Case 1: Composite Meal (ID 43: Rice & Beans)
food_id = 43
quantity_payload = {
    "rice": 200,
    "beans_(mseto)": 150
}

print(f"Testing Calculate for Food ID {food_id} with payload: {quantity_payload}")

try:
    result = utils.calculate_meal(food_id, quantity_payload)
    print("Result:")
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
