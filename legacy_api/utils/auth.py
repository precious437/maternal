import jwt
from functools import wraps
from flask import request, jsonify
import os

JWT_SECRET = os.getenv('JWT_SECRET')

def verify_auth():
    cookie_header = request.headers.get('Cookie', '')
    token_match = None
    if 'authToken=' in cookie_header:
        token_match = cookie_header.split('authToken=')[1].split(';')[0]
    
    if not token_match:
        return None, "No token"

    try:
        decoded = jwt.decode(token_match, JWT_SECRET, algorithms=["HS256"])
        return decoded, None
    except:
        return None, "Invalid token"
