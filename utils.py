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
            print(f"[SUCCESS] Loaded {len(FOOD_DATA)} items from {file_path}")
            
    except Exception as e:
        print(f"[ERROR] Error loading data: {e}")
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

def calculate_meal(food_id, quantity_input):
    """
    Calculates the nutrition for a specific food ID and quantity.
    quantity_input can be:
      - float/int: for Volumetric (grams) or Countable (pieces)
      - dict: for Composite ({"component_slug": quantity, ...})
    """
    # 1. Find the food item
    food = get_food_by_id(food_id)
    if not food:
        return None

    serving_type = food.get('serving_type', 'volumetric')
    standard_unit_weight = food.get('standard_unit_weight')
    
    total_grams = 0
    unit_label = ""
    
    # --- LOGIC BRANCHING ---
    
    if serving_type == 'composite':
        # Composite Logic: Sum of all components
        # quantity_input should be a dict: {'chicken_piece': 2, 'chips_portion': 150}
        
        # Fallback: If float is passed (e.g. from manual log), assume it's a multiplier for "1 standard serving"
        # We define "1 standard serving" as 1 unit of each countable component and 150g of each volumetric component.
        multiplier = 1.0
        is_simple_multiplier = False
        
        if not isinstance(quantity_input, dict):
            try:
                multiplier = float(quantity_input)
                is_simple_multiplier = True
            except:
                return None
            
        total_calories = 0
        total_protein = 0
        total_fat = 0
        total_carbs = 0
        component_labels = []

        components = food.get('components', [])
        
        for comp in components:
            slug = comp.get('slug')
            
            if is_simple_multiplier:
                # Default logic
                comp_type = comp.get('serving_type', 'volumetric')
                if comp_type == 'countable':
                    q = 1 * multiplier
                else:
                    q = 150 * multiplier # Default 150g for volumetric part
            else:
                q = quantity_input.get(slug, 0) # Quantity from dict
            
            if q > 0:
                # Calculate weight for this component
                comp_type = comp.get('serving_type', 'volumetric')
                comp_weight = 0
                
                if comp_type == 'countable':
                    # q is count, weight = q * unit_weight
                    u_weight = comp.get('standard_unit_weight', 0)
                    if not u_weight: u_weight = 100 # Fallback
                    comp_weight = q * u_weight
                    component_labels.append(f"{q} x {comp['name']}")
                else:
                    # q is weight in grams (volumetric)
                    comp_weight = q
                    component_labels.append(f"{comp['name']} ({q}g)")
                
                total_grams += comp_weight
        
        unit_label = ", ".join(component_labels)

    elif serving_type == 'countable':
        # Countable Logic: (Input_Count * Standard_Unit_Weight * Calories_Per_100g) / 100
        try:
            count = float(quantity_input)
        except:
            count = 0
            
        weight_per_unit = standard_unit_weight if standard_unit_weight else 100 # Fallback
        total_grams = count * weight_per_unit
        unit_label = f"{count} pieces ({total_grams}g)"

    else:
        # Volumetric Logic: (Selected_Bowl_Weight * Calories_Per_100g) / 100
        # quantity_input is expected to be the Weight in Grams directly from the UI
        try:
            total_grams = float(quantity_input)
        except:
            total_grams = 0
        unit_label = f"{total_grams}g"

    # 3. Calculate Macros (The Math)
    # Using the parent food's macros for the total weight
    factor = total_grams / 100.0

    return {
        "name": food['name'],
        "calories": round(food['calories_per_100g'] * factor),
        "protein_g": round(food['protein_per_100g'] * factor, 1),
        "fat_g": round(food['fat_per_100g'] * factor, 1),
        "carbs_g": round(food['carbs_per_100g'] * factor, 1),
        "input_quantity": unit_label
    }
