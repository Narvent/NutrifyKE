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
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not found. AI features will not work.")
    model = None
else:
    genai.configure(api_key=GEMINI_API_KEY)
    # Use gemini-3-pro-preview (latest available model)
    model = genai.GenerativeModel('gemini-3-pro-preview')

# Load local data on startup
utils.load_data()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/foods')
def get_foods():
    # Helper to prevent crashes if utils.FOOD_DATA is empty
    if not hasattr(utils, 'FOOD_DATA'):
        utils.load_data()
    foods = [{"id": item["id"], "name": item["name"]} for item in utils.FOOD_DATA]
    return jsonify(foods)

@app.route('/search')
def search():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Missing query parameter 'q'"}), 400
    results = utils.search_food(query)
    return jsonify(results)

@app.route('/calculate')
def calculate():
    food_id = request.args.get('id', type=int)
    quantity = request.args.get('quantity', type=float)
    if food_id is None or quantity is None:
        return jsonify({"error": "Missing parameters"}), 400
    result = utils.calculate_meal(food_id, quantity)
    if not result:
        return jsonify({"error": "Food not found"}), 404
    return jsonify(result)

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
          "confidence": float,
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
        
        # Try to extract JSON object
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        
        if not json_match:
            print("AI Output was not valid JSON:", raw_text)
            return jsonify({"error": "AI failed to return valid JSON"}), 500
            
        clean_json_str = json_match.group(0)
        ai_result = json.loads(clean_json_str)
        
        print(f"AI Analysis: {ai_result}")
        
        # 5. Match the food name to our database
        detected_name = ai_result.get('food_name', '').strip()
        matched_food = None
        search_term = detected_name.lower()

        # Step A: Exact Match (Case Insensitive)
        for item in utils.FOOD_DATA:
            if item['name'].lower() == search_term:
                matched_food = item
                break
        
        # Step B: AI name is INSIDE Database name
        if not matched_food:
            for item in utils.FOOD_DATA:
                db_name = item['name'].lower()
                if search_term in db_name:
                    matched_food = item
                    break
        
        # Step C: Database name is INSIDE AI name
        if not matched_food:
            for item in utils.FOOD_DATA:
                db_name = item['name'].lower()
                if db_name in search_term and len(db_name) > 3:
                    matched_food = item
                    break

        if not matched_food:
            return jsonify({
                "status": "error",
                "error": f"Could not match food '{detected_name}' to database."
            }), 404
        
        print(f"✓ Matched: {matched_food['name']} (ID: {matched_food['id']})")
        
        # 6. Return the analysis + matched food details
        return jsonify({
            "status": "success",
            "analysis": ai_result,
            "matched_food": {
                "id": matched_food['id'],
                "name": matched_food['name'],
                "calories_per_100g": matched_food['calories_per_100g'],
                "manual_unit": matched_food.get('manual_unit'),
                "portions": matched_food.get('portions', [])
            }
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
