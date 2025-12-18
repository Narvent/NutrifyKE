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
load_dotenv()

# Support both naming conventions
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') 

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

    # FIX: Ensure food_id is an integer (frontend sends string)
    try:
        food_id = int(food_id)
    except:
        return jsonify({"error": "Invalid ID format"}), 400

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

@app.route('/api/logs', methods=['GET'])
def get_logs():
    date_str = request.args.get('date')
    logs = database_setup.get_logs(date_str)
    
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
        return jsonify({"error": "No data provided"}), 400
        
    try:
        log_id = database_setup.add_log(
            food_name=data['name'],
            calories=data['calories'],
            protein=data.get('protein_g', 0),
            fat=data.get('fat_g', 0),
            carbs=data.get('carbs_g', 0),
            quantity_label=data.get('quantity_label'),
            timestamp_iso=data.get('timestamp'),  # Pass the client timestamp
            date_logged=data.get('date')          # Pass the client date
        )
        return jsonify({"success": True, "id": log_id}), 201
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
        data = request.get_json() or {}
        date_str = data.get('date')
        database_setup.clear_logs(date_str)
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
        
        # Create a list of all available food names for the AI to choose from
        food_names = [f["name"] for f in utils.FOOD_DATA]
        food_list_str = ", ".join(food_names)

        prompt = f"""
        You are an expert Kenyan Nutrition AI. Analyze the image for food intake.
        
        CRITICAL: GENUINE IDENTIFICATION REQUIRED
        You must identify ALL distinct foods in the image. You are RESTRICTED to choosing from the following list:
        [{food_list_str}]
        
        If a food matches (e.g., 'Beef Sausages' -> 'Smokies', 'Fried Fish' -> 'Fish (Tilapia - Dry Fried)'), USE THE EXACT NAME FROM THE LIST.

        Step 1: Detect Container & Layout
        - Discrete items (e.g., Samosas, Smokies, Mandazi, Chapatis)? -> Mode: COUNT.
        - Deep vessel (bowl) or amorphous mass? -> Mode: VOLUME.

        Step 2: Return strict JSON
        {{
          "items": [
            {{
              "food_name": "EXACT_NAME_FROM_LIST",
              "nutritional_info": {{ "calories": int, "protein": int, "carbs": int, "fat": int }},
              "layout": {{
                "mode": "count" | "volume",
                "container_type": "plate" | "sufuria" | "bowl" | "hand",
                "is_stacked": boolean,
                "visible_count": integer (null if volume),
                "fullness_index": float (0.0-1.0, null if count)
              }}
            }}
          ]
        }}
        
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
        
        # 5. Process Response
        results = []
        
        # Normalize to list of items
        detected_items = ai_result.get('items', [])
        if not detected_items:
            # Fallback for single object response if AI fails to follow list format
            if 'food_name' in ai_result:
                detected_items = [ai_result]

        for item_data in detected_items:
            food_name = item_data.get('food_name', '')
            if not food_name: continue

            # Match Logic
            matched_food = None
            search_term = food_name.lower()

            # Exact Match
            for db_item in utils.FOOD_DATA:
                if db_item['name'].lower() == search_term:
                    matched_food = db_item
                    break
            
            # Substring Match
            if not matched_food:
                for db_item in utils.FOOD_DATA:
                    if search_term in db_item['name'].lower():
                        matched_food = db_item
                        break
            
            # Token Match
            if not matched_food:
                search_tokens = set(re.findall(r'\w+', search_term))
                best_match = None
                max_overlap = 0
                for db_item in utils.FOOD_DATA:
                    item_tokens = set(re.findall(r'\w+', db_item['name'].lower()))
                    overlap = len(search_tokens.intersection(item_tokens))
                    if overlap > max_overlap:
                        max_overlap = overlap
                        best_match = db_item
                if best_match and max_overlap > 0:
                    matched_food = best_match

            # Construct result entry
            food_result = {
                "input_food_name": food_name,
                "analysis": {
                     "nutritional_info": item_data.get('nutritional_info', {}),
                     "layout": item_data.get('layout', {})
                }
            }
            
            if matched_food:
                food_result["matched_food"] = {
                    "id": matched_food['id'],
                    "name": matched_food['name'],
                    "calories_per_100g": matched_food['calories_per_100g'],
                    "protein_per_100g": matched_food['protein_per_100g'],
                    "fat_per_100g": matched_food['fat_per_100g'],
                    "carbs_per_100g": matched_food['carbs_per_100g'],
                    "serving_type": matched_food.get('serving_type', 'volumetric'),
                    "standard_unit_weight": matched_food.get('standard_unit_weight'),
                    "components": matched_food.get('components', []),
                    "portions": matched_food.get('portions', [])
                }
            else:
                 food_result["matched_food"] = None
                 
            results.append(food_result)

        return jsonify({
            "status": "success", 
            "results": results
        })

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
