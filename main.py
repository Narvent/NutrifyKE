from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import check_password_hash
import utils
from google import genai
from PIL import Image
import json
import io
import os
import re
import base64
from dotenv import load_dotenv
import database_setup
import clerk_auth

app = Flask(__name__)

# --- RATE LIMITING ---
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# --- CONFIGURATION ---
load_dotenv()

def get_clerk_fapi(publishable_key):
    """Derives the Frontend API URL from a Clerk Publishable Key."""
    if not publishable_key: return None
    try:
        parts = publishable_key.split('_')
        if len(parts) < 3: return None
        # The data is the portion after the second underscore and before the suffix
        encoded = parts[2].split('$')[0]
        padding = '=' * (4 - (len(encoded) % 4))
        decoded = base64.b64decode(encoded + padding).decode('utf-8')
        return decoded.rstrip('$')
    except Exception:
        return None

# Support both naming conventions for secret key
SECRET_KEY = os.getenv('CLERK_SECRET_KEY') or os.getenv('SECRET_KEY') or 'dev-secret-key-change-in-prod'
app.secret_key = SECRET_KEY

# Clerk Frontend Config
CLERK_PUBLISHABLE_KEY = os.getenv('NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY') or os.getenv('CLERK_PUBLISHABLE_KEY') or os.getenv('PUBLIC_KEY')
CLERK_FRONTEND_API = os.getenv('CLERK_FRONTEND_API') or os.getenv('CLERK_API_URL') or get_clerk_fapi(CLERK_PUBLISHABLE_KEY)

# Strip protocol if present in FAPI
if CLERK_FRONTEND_API and CLERK_FRONTEND_API.startswith('http'):
    CLERK_FRONTEND_API = CLERK_FRONTEND_API.replace('https://', '').replace('http://', '').split('/')[0]

# Support both naming conventions for Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not found. AI features will not work.")
    client = None
else:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Error initializing AI client: {e}")
        client = None

# Load local data on startup
utils.load_data()
try:
    # On Vercel, the filesystem is read-only except /tmp
    # We wrap this to prevent crash if DB init attempts to write to the project root
    database_setup.init_db()
except Exception as e:
    print(f"DATABASE INIT WARNING: {e}")
    # If using Postgres (Neon), this should still work. If SQLite, it might fail if file doesn't exist.

# --- AUTHENTICATION SETUP ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, email, clerk_id=None, name=None):
        self.id = id
        self.email = email
        self.clerk_id = clerk_id
        self.name = name

    @property
    def display_name(self):
        if self.name:
            return self.name
        return self.email.split('@')[0]

@login_manager.user_loader
def load_user(user_id):
    user_data = database_setup.get_user_by_id(user_id)
    if user_data:
        name = user_data.get('display_name')
        return User(user_data['id'], user_data['email'], user_data.get('clerk_id'), name)
    return None

# --- AUTH ROUTES ---

@app.route('/login')
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('login.html', 
                          clerk_publishable_key=CLERK_PUBLISHABLE_KEY,
                          clerk_frontend_api=CLERK_FRONTEND_API)

@app.route('/register')
@limiter.limit("10 per minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('register.html', 
                          clerk_publishable_key=CLERK_PUBLISHABLE_KEY,
                          clerk_frontend_api=CLERK_FRONTEND_API)

@app.route('/logout')
def logout():
    logout_user()
    # Note: Frontend handles Clerk logout, but we clear the local session too
    return redirect(url_for('login'))

@app.route('/sync-user', methods=['POST'])
def sync_user():
    """Sync Clerk user data with local database after frontend login."""
    data = request.json
    clerk_id = data.get('clerk_id')
    email = data.get('email')
    name = data.get('name')
    
    if not clerk_id or not email:
        return jsonify({"success": False, "error": "Missing user data"}), 400
        
    user_data = database_setup.get_user_by_clerk_id(clerk_id)
    if not user_data:
        # Check if user exists by email (to migrate old local users to Clerk)
        user_data = database_setup.get_user_by_email(email)
        if user_data:
            # Update existing user with Clerk ID
            conn, db_type = database_setup.get_db_connection()
            c = conn.cursor()
            if db_type == 'postgres':
                c.execute('UPDATE users SET clerk_id = %s, display_name = %s WHERE id = %s', (clerk_id, name, user_data['id']))
            else:
                c.execute('UPDATE users SET clerk_id = ?, display_name = ? WHERE id = ?', (clerk_id, name, user_data['id']))
            conn.commit()
            conn.close()
        else:
            # Create new local record for Clerk user
            uid = database_setup.create_user(email, name=name, clerk_id=clerk_id)
            user_data = database_setup.get_user_by_id(uid)
            
    # Log in the user locally
    user = User(user_data['id'], user_data['email'], user_data.get('clerk_id'), user_data.get('display_name'))
    login_user(user, remember=True)
    return jsonify({"success": True})

# --- MAIN ROUTES ---

@app.route('/')
@login_required
def home():
    return render_template('index.html', 
                          user=current_user,
                          clerk_publishable_key=CLERK_PUBLISHABLE_KEY,
                          clerk_frontend_api=CLERK_FRONTEND_API)

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/foods')
@login_required
def get_foods():
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
@login_required
def search():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Missing query parameter 'q'"}), 400
    results = utils.search_food(query)
    return jsonify(results)

@app.route('/calculate', methods=['POST'])
@login_required
def calculate():
    data = request.get_json()
    if not data: return jsonify({"error": "Missing JSON body"}), 400

    food_id = data.get('id')
    quantity = data.get('quantity')
    
    if food_id is None or quantity is None:
        return jsonify({"error": "Missing parameters"}), 400

    try:
        food_id = int(food_id)
    except:
        return jsonify({"error": "Invalid ID format"}), 400

    if isinstance(quantity, str):
        try:
            quantity = json.loads(quantity)
        except:
            try:
                quantity = float(quantity)
            except:
                return jsonify({"error": "Invalid quantity format"}), 400
    
    result = utils.calculate_meal(food_id, quantity)
    if not result:
        return jsonify({"error": "Food not found"}), 404
        
    return jsonify(result)

# --- DATABASE LOGGING ROUTES (Multi-Tenant) ---

@app.route('/api/logs', methods=['GET'])
@login_required
def get_logs():
    date_str = request.args.get('date')
    # Pass current_user.id
    logs = database_setup.get_logs(current_user.id, date_str)
    
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
@login_required
def add_log():
    data = request.get_json()
    if not data: return jsonify({"error": "No data provided"}), 400
        
    try:
        # Pass current_user.id
        log_id = database_setup.add_log(
            user_id=current_user.id,
            food_name=data['name'],
            calories=data['calories'],
            protein=data.get('protein_g', 0),
            fat=data.get('fat_g', 0),
            carbs=data.get('carbs_g', 0),
            quantity_label=data.get('quantity_label'),
            timestamp_iso=data.get('timestamp'),
            date_logged=data.get('date')
        )
        return jsonify({"success": True, "id": log_id}), 201
    except Exception as e:
        print(f"Error adding log: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/logs/<int:log_id>', methods=['DELETE'])
@login_required
def delete_log(log_id):
    try:
        # Pass current_user.id
        database_setup.delete_log(log_id, current_user.id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reset', methods=['POST'])
@login_required
def reset_logs():
    try:
        data = request.get_json() or {}
        date_str = data.get('date')
        # Pass current_user.id
        database_setup.clear_logs(current_user.id, date_str)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/init-db', methods=['GET'])
def manual_init_db():
    try:
        database_setup.init_db()
        return jsonify({"status": "success", "message": "Database initialized successfully."})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

# --- MULTI-FOOD DETECTION ROUTE ---
@app.route('/analyze', methods=['POST'])
@login_required
@limiter.limit("5 per minute")
def analyze_image():
    # ... (Keep existing logic, just added @login_required)
    if client is None:
        return jsonify({"status": "error", "error": "AI service not configured."}), 503
    
    if 'image' not in request.files: return jsonify({"error": "No image part"}), 400
    file = request.files['image']
    if file.filename == '': return jsonify({"error": "No selected file"}), 400

    try:
        image = Image.open(file.stream)
        if image.mode != 'RGB': image = image.convert('RGB')
        max_size = 1024
        if image.width > max_size or image.height > max_size:
            image.thumbnail((max_size, max_size))

        food_names = [f["name"] for f in utils.FOOD_DATA]
        food_list_str = ", ".join(food_names)

        prompt = f"""
        You are an expert Afyniq Nutrition AI. Analyze the image for food intake.
        CRITICAL: GENUINE IDENTIFICATION REQUIRED
        You must identify ALL distinct foods in the image. You are RESTRICTED to choosing from the following list:
        [{food_list_str}]
        If a food matches, USE THE EXACT NAME FROM THE LIST.
        
        Step 1: Detect Container & Layout.
             - If the food is distinct items (e.g. eggs, samosas, chapatis, fruits, mandazi), Mode is COUNT. Count them precisely.
             - If the food is amorphous (e.g. rice, stew, ugali), Mode is VOLUME. Estimate fullness (0.0 to 1.0).
             
        Step 2: Return strict JSON:
        {{ 
            "items": [ 
                {{ 
                    "food_name": "EXACT_NAME", 
                    "nutritional_info": {{...}}, 
                    "layout": {{ 
                        "mode": "count" or "volume", 
                        "visible_count": INTEGER (REQUIRED for count mode, e.g. 2, 5, 10), 
                        "fullness_index": FLOAT (0.0-1.0, for volume mode),
                        "container_type": "plate"|"bowl"|"cup",
                        "is_stacked": BOOLEAN (true if items overlap)
                    }} 
                }} 
            ] 
        }}
        """

        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[prompt, image]
        )
        raw_text = response.text.strip()
        
        if raw_text.startswith("```json"): raw_text = raw_text[7:]
        if raw_text.startswith("```"): raw_text = raw_text[3:]
        if raw_text.endswith("```"): raw_text = raw_text[:-3]
        raw_text = raw_text.strip()

        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if json_match: raw_text = json_match.group(0)
        
        try:
            ai_result = json.loads(raw_text)
        except json.JSONDecodeError:
            return jsonify({"error": "Failed to parse AI response", "raw_data": raw_text}), 400
        
        results = []
        detected_items = ai_result.get('items', [])
        if not detected_items and 'food_name' in ai_result:
            detected_items = [ai_result]

        for item_data in detected_items:
            food_name = item_data.get('food_name', '')
            if not food_name: continue

            matched_food = None
            search_term = food_name.lower()
            
            for db_item in utils.FOOD_DATA:
                if db_item['name'].lower() == search_term:
                    matched_food = db_item
                    break
            
            if not matched_food:
                for db_item in utils.FOOD_DATA:
                    if search_term in db_item['name'].lower():
                        matched_food = db_item
                        break
            
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

        return jsonify({"status": "success", "results": results})

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        return jsonify({"error": f"Server Error: {str(e)}"}), 500

# Asset Links for Play Store (TWA)
@app.route('/.well-known/assetlinks.json')
def asset_links():
    # This file proves ownership to Google Play
    return jsonify([{
        "relation": ["delegate_permission/common.handle_all_urls"],
        "target": {
            "namespace": "android_app",
            "package_name": "com.afyniq.app", # Replace with actual package name later
            "sha256_cert_fingerprints": ["..."] # Replace with actual fingerprint later
        }
    }])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
