from flask import Flask, jsonify, request, render_template
import utils
import google.generativeai as genai
from PIL import Image
import json
import io
import os
import re
from dotenv import load_dotenv

app = Flask(__name__)

# --- CONFIGURATION ---
# Load environment variables from .env file
# Load environment variables from .env file
load_dotenv()

# Support both naming conventions
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY (or GOOGLE_API_KEY) not found. AI features will not work.")
    model = None
else:
    # DEBUG: Print key info to Vercel logs (safe)
    key_len = len(GEMINI_API_KEY)
    key_start = GEMINI_API_KEY[:4] if key_len >= 4 else "****"
    print(f"DEBUG: API Key loaded. Length: {key_len}, Starts with: {key_start}...")
    
    # Check for accidental quotes which is a common Vercel error
    if GEMINI_API_KEY.startswith('"') or GEMINI_API_KEY.startswith("'"):
        print("CRITICAL WARNING: API Key appears to be quoted! Remove quotes in Vercel.")
    
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Use gemini-3-pro-preview (ensure this model is enabled in your Google Cloud)
    try:
        model = genai.GenerativeModel('gemini-3-pro-preview')
    except Exception as e:
        print(f"Error initializing model: {e}")
        model = None

# Load local data on startup
utils.load_data()
import database_setup
database_setup.init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/foods')
def get_foods():
    # Helper to prevent crashes if utils.FOOD_DATA is empty
    if not hasattr(utils, 'FOOD_DATA'):
        utils.load_data()
    foods = []
    for item in utils.FOOD_DATA:
        foods.append({
            "id": item["id"], 
            "name": item["name"],
            "serving_type": item.get("serving_type", "volumetric"),
            "standard_unit_weight": item.get("standard_unit_weight"),
            "components": item.get("components", []),
            "portions": item.get("portions", [])
        })
    return jsonify(foods)

@app.route('/search')
def search():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Missing query parameter 'q'"}), 400
    results = utils.search_food(query)
    return jsonify(results)

@app.route('/calculate', methods=['POST'])
def calculate():
    # CHANGED: Read from JSON body instead of URL parameters
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    food_id = data.get('id')
    quantity = data.get('quantity')
    serving_type = data.get('serving_type', 'volumetric') # Default to volumetric
    
    if food_id is None or quantity is None:
        return jsonify({"error": "Missing parameters"}), 400

    # Quantity handling (already robust, but ensuring it works with JSON types)
    # If quantity is a string (legacy), try to parse it. If it's already a number/dict, use as is.
    if isinstance(quantity, str):
        try:
            quantity = json.loads(quantity)
        except:
            try:
                quantity = float(quantity)
            except:
                return jsonify({"error": "Invalid quantity format"}), 400
    
    # Pass serving_type if your utils.calculate_meal supports it, 
    # otherwise utils.calculate_meal likely just needs id and quantity.
    # Assuming utils.calculate_meal handles the logic based on food_id.
    result = utils.calculate_meal(food_id, quantity)
    
    if not result:
        return jsonify({"error": "Food not found"}), 404
        
    return jsonify(result)

# --- DATABASE LOGGING ROUTES ---

@app.route('/api/logs/today', methods=['GET'])
def get_logs():
    logs = database_setup.get_todays_logs()
    
    # Calculate totals
    totals = {
        "calories": sum(l['calories'] for l in logs),
        "protein": sum(l['protein_g'] for l in logs),
        "fat": sum(l['fat_g'] for l in logs),
        "carbs": sum(l['carbs_g'] for l in logs)
    }
    
    return jsonify({
        "logs": logs,
        "totals": totals
    })

@app.route('/api/logs', methods=['POST'])
def add_log():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing data"}), 400
        
    try:
        log_id = database_setup.add_log(
            food_name=data['name'],
            calories=data['calories'],
            protein=data.get('protein_g', 0),
            fat=data.get('fat_g', 0),
            carbs=data.get('carbs_g', 0),
            quantity_label=data.get('input_quantity', '1 serving')
        )
        return jsonify({"success": True, "id": log_id})
    except Exception as e:
        print(f"Error adding log: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/logs/<int:log_id>', methods=['DELETE'])
def delete_log(log_id):
    try:
        database_setup.delete_log(log_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset_logs():
    try:
        database_setup.clear_todays_logs()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- MULTI-FOOD DETECTION ROUTE ---
@app.route('/analyze', methods=['POST'])
def analyze_image():
    print("--- PHOTO RECEIVED (MULTI-FOOD MODE) ---")
    
    # Check if AI is configured
    if model is None:
        return jsonify({
            "status": "error",
            "error": "AI service not configured. Please contact support."
        }), 503
    
    if 'image' not in request.files:
        return jsonify({"error": "No image part"}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # 1. Convert the uploaded file to a format Gemini understands
        image = Image.open(file.stream)

        # --- OPTIMIZATION: Resize image to max 1024px to prevent Vercel 4.5MB limit ---
        # Convert to RGB to handle PNG alpha channels correctly
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        # Resize if larger than 1024px
        max_size = 1024
        if image.width > max_size or image.height > max_size:
            image.thumbnail((max_size, max_size))
            print(f"Image resized to {image.width}x{image.height}")
        # -----------------------------------------------------------------------------

        # 2. Use the new Container-Aware System Prompt
        prompt = """
        You are an expert Kenyan Nutrition AI. Analyze the image for food intake.

        Step 1: Detect the Container & Layout
        - Is the food on a flat surface (plate, board, table)? -> Mode: COUNT.
        - Is the food in a deep vessel (sufuria, bakuli, pot, tupperware, cup)? -> Mode: VOLUME.

        Step 2: Analyze Quantity based on Mode
        - If COUNT: Count visible items. Strictly check for stacking/piles. If items overlap significantly or form a heap (like a pile of mandazis/samosas), set is_stacked to true.
        - If VOLUME: Identify the container type (e.g., 'standard_bowl', 'sufuria'). Estimate fullness from 0.0 to 1.0 (where 1.0 is brim-full).

        Step 3: Return strict JSON
        {
          "food_name": "string (e.g. Beef Samosa)",
          "nutritional_info": { "calories": int, "protein": int, "carbs": int, "fat": int },
          "layout": {
            "mode": "count" | "volume",
            "container_type": "plate" | "sufuria" | "bowl" | "hand",
            "is_stacked": boolean (True if pile detected),
            "visible_count": integer (null if volume mode),
            "fullness_index": float (0.0-1.0, null if count mode)
          }
        }
        
        Return ONLY the raw JSON object. Do not use Markdown formatting.
        """

        response = model.generate_content([prompt, image])
        
        # 4. Robust JSON Extraction
        raw_text = response.text.strip()
        print(f"AI Raw Response: {raw_text[:200]}...")
        
        # Clean markdown backticks if present
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        
        raw_text = raw_text.strip()

        # Try to extract JSON object using regex as a fallback
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if json_match:
            raw_text = json_match.group(0)
        
        try:
            ai_result = json.loads(raw_text)
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
            print(f"Faulty JSON: {raw_text}")
            return jsonify({"error": "Failed to parse AI response", "raw_data": raw_text}), 400
        
        print(f"AI Analysis: {ai_result}")
        
        # 5. Safe Extraction with Defaults
        food_name = ai_result.get('food_name', 'Unknown Food')
        nutrition = ai_result.get('nutritional_info', {})
        layout = ai_result.get('layout', {})

        # 6. Match the food name to our database (Optional but good for consistency)
        # We will use the AI provided nutrition if available, otherwise fallback to DB
        matched_food = None
        search_term = food_name.lower()

        # Try to find in DB to get ID and other metadata
        for item in utils.FOOD_DATA:
            if item['name'].lower() == search_term:
                matched_food = item
                break
        
        if not matched_food:
             for item in utils.FOOD_DATA:
                if search_term in item['name'].lower():
                    matched_food = item
                    break
        
        if not matched_food:
            # Token Overlap Fallback
            search_tokens = set(re.findall(r'\w+', search_term.lower()))
            best_match = None
            max_overlap = 0
            
            for item in utils.FOOD_DATA:
                item_tokens = set(re.findall(r'\w+', item['name'].lower()))
                overlap = len(search_tokens.intersection(item_tokens))
                
                if overlap > max_overlap:
                    max_overlap = overlap
                    best_match = item
            
            if best_match and max_overlap > 0:
                matched_food = best_match
                print(f"Matched via Token Overlap: {matched_food['name']}")

        # Construct the response
        response_data = {
            "status": "success",
            "analysis": ai_result,
            "matched_food": {
                "id": matched_food['id'] if matched_food else 999, # 999 for unknown
                "name": food_name,
                "calories_per_100g": nutrition.get('calories', 0), # Use AI estimate or 0
                "protein_g": nutrition.get('protein', 0),
                "carbs_g": nutrition.get('carbs', 0),
                "fat_g": nutrition.get('fat', 0),
                "serving_type": matched_food.get('serving_type', 'volumetric') if matched_food else 'volumetric',
                "standard_unit_weight": matched_food.get('standard_unit_weight') if matched_food else None,
                "components": matched_food.get('components', []) if matched_food else [],
                "portions": matched_food.get('portions', []) if matched_food else []
            }
        }
        
        return jsonify(response_data)

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server Error: {str(e)}"}), 500

# Ensure data is loaded on startup
if not hasattr(utils, 'FOOD_DATA') or not utils.FOOD_DATA:
    utils.load_data()

# For Vercel deployment, the app object is used directly
# For local development, run with debug mode
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
