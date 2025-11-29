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
    # Use gemini-2.5-flash (latest model with credits)
    model = genai.GenerativeModel('gemini-2.5-flash')

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

        # 2. Use a smarter prompt that doesn't list all foods
        prompt = """
        You are a nutrition assistant for a Kenyan calorie tracker app.
        
        TASK: Identify ALL Kenyan foods visible in this image.
        
        Common Kenyan foods include: Ugali, Chapati, Rice, Githeri, Sukuma Wiki, Nyama Choma, 
        Pilau, Mandazi, Beans, Chicken, Fish, Beef Stew, Vegetables, etc.
        
        Return ONLY a raw JSON ARRAY (list). Do not use Markdown formatting or code blocks.
        Each item should have:
        - "food_name": The name of the food (be specific, e.g., "Ugali", "Chapati", "Rice", "Beef Stew")
        - "estimated_servings": A number representing portion size (1.0 = standard, 0.5 = half, 2.0 = double)
        
        Example JSON:
        [
          { "food_name": "Ugali", "estimated_servings": 1.0 },
          { "food_name": "Beef Stew", "estimated_servings": 0.5 }
        ]
        
        If only ONE food is visible, still return an array with one item.
        """

        response = model.generate_content([prompt, image])
        
        # 4. Robust JSON Extraction (handles both array and object responses)
        raw_text = response.text.strip()
        print(f"AI Raw Response: {raw_text[:200]}...")
        
        # Try to extract JSON array first
        json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
        
        # If no array found, try to extract object and wrap it in array
        if not json_match:
            json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if json_match:
                # Wrap single object in array
                clean_json_str = '[' + json_match.group(0) + ']'
            else:
                print("AI Output was not valid JSON:", raw_text)
                return jsonify({"error": "AI failed to return valid JSON"}), 500
        else:
            clean_json_str = json_match.group(0)
        
        ai_results = json.loads(clean_json_str)
        
        # Ensure it's a list
        if not isinstance(ai_results, list):
            ai_results = [ai_results]
        
        print(f"AI Detected {len(ai_results)} food item(s)")
        
        # 5. Process each detected food
        foods_found = []
        
        for ai_item in ai_results:
            detected_name = ai_item.get('food_name', '').strip()
            estimated_servings = ai_item.get('estimated_servings', 1.0)
            
            print(f"Processing: '{detected_name}' ({estimated_servings} servings)")
            
            # 6. SMART FUZZY MATCHING LOGIC
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
                print(f"WARNING: Could not match '{detected_name}' - skipping")
                continue
            
            print(f"✓ Matched: {matched_food['name']} (ID: {matched_food['id']})")
            
            # 7. Calculate nutrition using utils.calculate_meal
            meal_data = utils.calculate_meal(matched_food['id'], estimated_servings)
            
            if meal_data:
                foods_found.append(meal_data)
        
        # 8. Return the list of all detected foods
        if not foods_found:
            return jsonify({
                "status": "error",
                "error": "No foods could be matched from the image"
            }), 404
        
        print(f"SUCCESS: Returning {len(foods_found)} food(s)")
        
        return jsonify({
            "status": "success",
            "foods_found": foods_found
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
