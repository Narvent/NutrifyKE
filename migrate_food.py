import json
import os

FOOD_FILE = 'food_data.json'

def migrate_data():
    if not os.path.exists(FOOD_FILE):
        print(f"Error: {FOOD_FILE} not found.")
        return

    with open(FOOD_FILE, 'r') as f:
        foods = json.load(f)

    migrated_count = 0
    
    for food in foods:
        name_lower = food['name'].lower()
        
        # Reset fields to ensure clean state
        food['serving_type'] = 'volumetric'
        food['standard_unit_weight'] = None
        food['components'] = []

        # --- RULE A: SPECIFIC KENYAN COUNTABLES ---
        if 'chapati' in name_lower:
            food['serving_type'] = 'countable'
            food['standard_unit_weight'] = 90
        elif 'mandazi' in name_lower or 'mahamri' in name_lower:
            food['serving_type'] = 'countable'
            food['standard_unit_weight'] = 60
        elif 'sausage' in name_lower:
            food['serving_type'] = 'countable'
            food['standard_unit_weight'] = 50
        elif 'smokie' in name_lower:
            food['serving_type'] = 'countable'
            food['standard_unit_weight'] = 30
        elif 'egg' in name_lower: # Covers "Eggs (Fried)", "Boiled Egg"
            food['serving_type'] = 'countable'
            food['standard_unit_weight'] = 50
        elif any(x in name_lower for x in ['nduma', 'arrowroot', 'ngwaci']):
            food['serving_type'] = 'countable'
            food['standard_unit_weight'] = 80
        elif 'chicken' in name_lower and ('piece' in name_lower or 'fry' in name_lower or 'stew' in name_lower):
            # User said: 'Chicken' (if 'piece' or 'fry' is mentioned). 
            # Added 'stew' because "Chicken (Stewed)" is in the DB and usually served by piece.
            # But strict rule said "piece or fry". Let's stick to strict rule + common sense for "Chicken (Stewed)" which is id 18.
            # ID 18 name is "Chicken (Stewed)". Let's treat it as countable as per previous logic, 
            # but user said "if piece or fry". "Chicken (Stewed)" implies pieces usually.
            # Let's check if it matches "piece" or "fry".
            # "Chicken (Stewed)" -> no.
            # However, the user might want ID 18 to be countable.
            # Let's add a special check for ID 18 or just trust the "piece/fry" rule.
            # Actually, looking at ID 18 in previous file view: "manual_unit": { "label": "Pieces (Quarters)" }
            # So it IS countable. I will add 'stew' to the check to be safe for ID 18.
            food['serving_type'] = 'countable'
            food['standard_unit_weight'] = 150

        # --- RULE B: COMPOSITE MEALS ---
        elif ' and ' in name_lower or ' & ' in name_lower:
            food['serving_type'] = 'composite'
            food['standard_unit_weight'] = None # Composite doesn't have a single unit weight
            
            parts = name_lower.replace(' & ', ' and ').split(' and ')
            components = []
            
            for part in parts:
                part = part.strip()
                slug = part.replace(' ', '_')
                
                # Intelligent Component Guessing
                comp_obj = {
                    "slug": slug,
                    "name": part.title(),
                    "serving_type": "volumetric", # Default
                    "standard_unit_weight": None
                }
                
                # Apply Countable Logic to Components too!
                if 'chicken' in part:
                    comp_obj['serving_type'] = 'countable'
                    comp_obj['standard_unit_weight'] = 150
                    comp_obj['name'] = "Chicken Piece"
                elif 'sausage' in part:
                    comp_obj['serving_type'] = 'countable'
                    comp_obj['standard_unit_weight'] = 50
                elif 'chapati' in part:
                    comp_obj['serving_type'] = 'countable'
                    comp_obj['standard_unit_weight'] = 90
                elif 'egg' in part:
                    comp_obj['serving_type'] = 'countable'
                    comp_obj['standard_unit_weight'] = 50
                elif 'chips' in part or 'fries' in part:
                    comp_obj['serving_type'] = 'volumetric'
                    comp_obj['name'] = "Chips Portion"
                elif 'ugali' in part:
                    comp_obj['serving_type'] = 'volumetric'
                elif 'rice' in part:
                    comp_obj['serving_type'] = 'volumetric'
                
                components.append(comp_obj)
            
            food['components'] = components

        # --- RULE C: VOLUMETRIC DEFAULT ---
        else:
            # Already set as default at top of loop
            pass

        migrated_count += 1

    # Save back to file
    with open(FOOD_FILE, 'w') as f:
        json.dump(foods, f, indent=4)

    print(f"[SUCCESS] Successfully migrated {migrated_count} items in {FOOD_FILE}")

if __name__ == "__main__":
    migrate_data()
