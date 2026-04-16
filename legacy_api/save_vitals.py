from flask import request, jsonify
import os
from supabase import create_client

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

def handler(req):
    if req.method != 'POST':
        return jsonify({'error': 'Method not allowed'}), 405

    try:
        data = req.get_json()
        
        result = supabase.table('patient_cases').insert({
            'maternal_bp': data.get('maternalBP'),
            'heart_rate': data.get('heartRate'),
            'fetal_hr': data.get('fetalHR'),
            'spo2': data.get('spo2')
        }).execute()

        return jsonify({'success': True, 'message': 'Vital signs saved successfully'})

    except Exception as e:
        print("Save vitals error:", str(e))
        return jsonify({'error': 'Failed to save vital signs'}), 500

