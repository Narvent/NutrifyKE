import json
import os

# --- GLOBAL DATA STORE ---
# This variable is what main.py is looking for.
FOOD_DATA = []

def load_data():
    """
    Loads the food database from 'food_data.json' into the global FOOD_DATA list.
    Call this once when the app starts.
    """
    global FOOD_DATA
    # Ensure this filename matches exactly what is in your VS Code explorer
    file_path = 'food_data.json' 
    
    try:
        if not os.path.exists(file_path):
            print(f"CRITICAL WARNING: {file_path} not found! Database is empty.")
            FOOD_DATA = []
            return

        with open(file_path, 'r') as f:
            FOOD_DATA = json.load(f)
            print(f"✅ Successfully loaded {len(FOOD_DATA)} items from {file_path}")
            
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        FOOD_DATA = []

def get_food_by_id(food_id):
    """Helper to find a food dictionary by its ID."""
    for food in FOOD_DATA:
        if food['id'] == food_id:
            return food
    return None

def search_food(query):
    """
    Searches for food by name using a fuzzy keyword match.
    Returns a list of matching food objects.
    """
    query = query.lower().strip()
    results = []
    
    for food in FOOD_DATA:
        food_name = food['name'].lower()
        # Check if query is inside name OR name is inside query
        if query in food_name or food_name in query:
            results.append(food)
            
    return results

def calculate_meal(food_id, quantity):
    """
    Calculates the nutrition for a specific food ID and quantity.
    Returns the specific keys required by index.html (name, protein_g, etc).
    """
    # 1. Find the food item
    food = None
    for item in FOOD_DATA:
        if item['id'] == food_id:
            food = item
            break
            
    if not food:
        return None

    # 2. Calculate the actual weight in grams
    amount_in_grams = 0
    unit_label = "grams"
    
    # Check if the food uses "pieces" (like Chapati) or "weight" (like Rice)
    manual_unit = food.get('manual_unit', {})
    unit_type = manual_unit.get('type', 'weight')

    if unit_type == 'piece':
        # Logic: User entered number of pieces (e.g. 2 chapatis)
        weight_per_piece = manual_unit.get('weight_per_unit_g', 100)
        amount_in_grams = quantity * weight_per_piece
        unit_label = f"{quantity} {manual_unit.get('label', 'pieces')}"
    else:
        # Logic: User entered weight or servings
        if quantity < 15: 
            # If number is small (e.g. 1.5), assume it's "Servings" of roughly 250g
            amount_in_grams = quantity * 250 
            unit_label = f"{quantity} Servings"
        else:
            # If number is large (e.g. 300), assume it's "Grams"
            amount_in_grams = quantity
            unit_label = f"{quantity}g"

    # 3. Calculate Macros (The Math)
    factor = amount_in_grams / 100.0

    # 4. Return Data (Matches index.html expectations)
    return {
        "name": food['name'],
        "calories": round(food['calories_per_100g'] * factor),
        "protein_g": round(food['protein_per_100g'] * factor, 1),
        "fat_g": round(food['fat_per_100g'] * factor, 1),
        "carbs_g": round(food['carbs_per_100g'] * factor, 1),
        "input_quantity": unit_label
    }
