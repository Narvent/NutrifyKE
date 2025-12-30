import os
from functools import wraps
from flask import request, jsonify, g
from jose import jwt
import requests
from dotenv import load_dotenv

load_dotenv()

# Clerk Configuration
CLERK_FRONTEND_API = os.getenv('CLERK_FRONTEND_API')

def get_jwks_url():
    """Derives Clerk JWKS URL from Frontend API."""
    if not CLERK_FRONTEND_API:
        return os.getenv('CLERK_JWKS_URL')
    # Remove protocol if present just in case
    domain = CLERK_FRONTEND_API.replace('https://', '').replace('http://', '').split('/')[0]
    return f"https://{domain}/.well-known/jwks.json"

CLERK_JWKS_URL = get_jwks_url()

def verify_clerk_session(token):
    """Verifies the JWT token locally using Clerk's public keys."""
    if not CLERK_JWKS_URL:
        print("CRITICAL: CLERK_JWKS_URL or CLERK_FRONTEND_API not configured.")
        return None
        
    try:
        # 1. Fetch Clerk's public keys (In production, use caching!)
        jwks = requests.get(CLERK_JWKS_URL).json()
        
        # 2. Decode and verify the token
        payload = jwt.decode(
            token, 
            jwks, 
            algorithms=['RS256'], 
            audience=CLERK_FRONTEND_API
        )
        return payload 
    except Exception as e:
        print(f"JWT Verification Failed: {e}")
        return None

def clerk_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Check Authorization Header (Standard for APIs)
        auth_header = request.headers.get('Authorization')
        token = None
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            # 2. Fallback to Cookie (For browser-based requests)
            token = request.cookies.get('__session')

        if not token:
            return jsonify({"error": "Missing session token"}), 401

        # 3. Actually verify the token
        user_data = verify_clerk_session(token)
        if not user_data:
            return jsonify({"error": "Invalid or expired session"}), 401

        # 4. Store user info in Flask's global 'g' for use in the route
        g.user_id = user_data.get('sub')
        
        return f(*args, **kwargs)
    return decorated_function
