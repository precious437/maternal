from flask import request, jsonify
from supabase import create_client
import jwt
import os
from datetime import datetime, timedelta

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

JWT_SECRET = os.getenv('JWT_SECRET')

def handler(req):
    if req.method != 'POST':
        return jsonify({'error': 'Method not allowed'}), 405

    try:
        data = req.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # Check if user exists
        response = supabase.table('users').select('*').eq('email', email).execute()
        
        if not response.data:
            # Auto create user on first login
            new_user = supabase.table('users').insert({
                'email': email,
                'name': email.split('@')[0].capitalize(),
                'role': 'surgeon'
            }).execute()
            user = new_user.data[0]
        else:
            user = response.data[0]

        # Create JWT token
        token = jwt.encode({
            'userId': user['id'],
            'email': user['email'],
            'name': user['name'],
            'role': user['role'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, JWT_SECRET, algorithm='HS256')

        resp = jsonify({'success': True})
        resp.set_cookie('authToken', token, httponly=True, secure=True, samesite='Strict', max_age=86400)
        return resp

    except Exception as e:
        print("Login error:", str(e))
        return jsonify({'error': 'Internal server error'}), 500


   



