import utils
import json

print("--- Testing load_data ---")
utils.load_data()
print(f"Loaded {len(utils.FOOD_DATA)} items.")

print("\n--- Testing calculate_meal (Unrounded) ---")
# ID 1: Chapati (White) - 509 kcal
# Quantity 1.5
# Expected: 509 * 1.5 = 763.5
meal = utils.calculate_meal(1, 1.5)
print(f"Meal calculation for ID 1, quantity 1.5: {json.dumps(meal, indent=2)}")

if meal and meal['calories'] == 763.5:
    print("\nSUCCESS: Calculation is correct and unrounded (509 * 1.5 = 763.5)")
else:
    print(f"\nWARNING: Calculation might be incorrect. Expected 763.5, got {meal['calories'] if meal else 'None'}")
