import httpx
import os
from django.conf import settings

class SupabaseService:
    @staticmethod
    def _validate_config():
        if not settings.SUPABASE_URL or not settings.SUPABASE_URL.startswith("http"):
            raise ValueError("SUPABASE_URL is not configured correctly in environment variables.")

    @staticmethod
    def get_headers(use_service_role=True):
        # Prefer Anon key for user-facing auth, Fallback to Service role if Anon is missing
        anon_key = getattr(settings, 'SUPABASE_ANON_KEY', '')
        service_key = settings.SUPABASE_SERVICE_ROLE_KEY
        
        key = service_key if use_service_role or not anon_key else anon_key
        
        return {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }

    @staticmethod
    def save_vitals(data):
        try:
            SupabaseService._validate_config()
            # Mapping frontend names to Supabase column names
            supabase_data = {
                "maternal_bp": data.get("maternal_bp"),
                "heart_rate": data.get("maternal_hr"),  # Field mapping fix
                "fetal_hr": data.get("fetal_hr"),
                "spo2": data.get("spo2")
            }
            url = f"{settings.SUPABASE_URL}/rest/v1/patient_cases"
            with httpx.Client() as client:
                response = client.post(url, json=supabase_data, headers=SupabaseService.get_headers())
                if response.status_code < 400:
                    try:
                        return response.json()
                    except:
                        return {"success": True} # Handle 201 Created with empty body
                return {"error": response.text}
        except Exception as e:
            return {"success": False, "error": f"Configuration Error: {str(e)}"}

    @staticmethod
    def upload_file(file_obj, filename):
        try:
            SupabaseService._validate_config()
            # Supabase Storage Upload
            url = f"{settings.SUPABASE_URL}/storage/v1/object/{settings.SUPABASE_BUCKET}/{filename}"
            headers = {
                "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
                "Content-Type": "application/octet-stream"
            }
            with httpx.Client() as client:
                response = client.post(url, content=file_obj.read(), headers=headers)
                if response.status_code < 400:
                    return {
                        "success": True,
                        "url": f"{settings.SUPABASE_URL}/storage/v1/object/public/{settings.SUPABASE_BUCKET}/{filename}"
                    }
                return {"success": False, "error": response.text}
        except Exception as e:
            return {"success": False, "error": f"Configuration Error: {str(e)}"}

    @staticmethod
    def save_scan_metadata(metadata):
        try:
            SupabaseService._validate_config()
            url = f"{settings.SUPABASE_URL}/rest/v1/medical_scans"
            with httpx.Client() as client:
                response = client.post(url, json=metadata, headers=SupabaseService.get_headers())
                if response.status_code < 400:
                    try:
                        return response.json()
                    except:
                        return {"success": True}
                return {"error": response.text}
        except Exception as e:
            return {"success": False, "error": f"Configuration Error: {str(e)}"}

    @staticmethod
    def get_scan_history():
        try:
            SupabaseService._validate_config()
            url = f"{settings.SUPABASE_URL}/rest/v1/medical_scans?select=*&order=created_at.desc&limit=10"
            with httpx.Client() as client:
                response = client.get(url, headers=SupabaseService.get_headers())
                return response.json() if response.status_code == 200 else []
        except:
            return []

    @staticmethod
    def verify_login(email, password):
        try:
            SupabaseService._validate_config()
            # Supabase Auth Login
            url = f"{settings.SUPABASE_URL}/auth/v1/token?grant_type=password"
            # Use Anon key for auth if available, otherwise Service Role (though Anon is preferred for user-auth)
            headers = SupabaseService.get_headers(use_service_role=False) 
            data = {"email": email, "password": password}
            with httpx.Client() as client:
                response = client.post(url, json=data, headers=headers)
                if response.status_code < 400:
                    return {"success": True, "token": response.json().get("access_token"), "user": response.json().get("user")}
                
                # Detailed error log for the admin
                error_data = response.json()
                msg = error_data.get("error_description", error_data.get("msg", "Login failed"))
                return {"success": False, "error": msg}
        except Exception as e:
            return {"success": False, "error": f"Auth Service unreachable: {str(e)}"}

    @staticmethod
    def signup_user(email, password):
        try:
            SupabaseService._validate_config()
            url = f"{settings.SUPABASE_URL}/auth/v1/signup"
            headers = SupabaseService.get_headers(use_service_role=False)
            data = {"email": email, "password": password}
            with httpx.Client() as client:
                response = client.post(url, json=data, headers=headers)
                if response.status_code < 400:
                    return {"success": True, "token": response.json().get("access_token"), "user": response.json().get("user")}
                
                error_data = response.json()
                msg = error_data.get("error_description", error_data.get("msg", "Signup failed"))
                return {"success": False, "error": msg}
        except Exception as e:
            return {"success": False, "error": f"Auth Service unreachable: {str(e)}"}

    @staticmethod
    def get_history():
        try:
            SupabaseService._validate_config()
            # Fetch from patient_cases table
            url = f"{settings.SUPABASE_URL}/rest/v1/patient_cases?select=*"
            with httpx.Client() as client:
                response = client.get(url, headers=SupabaseService.get_headers())
                if response.status_code < 400:
                    return {"success": True, "records": response.json()}
                return {"success": False, "error": response.text}
        except Exception as e:
            return {"success": False, "error": f"Configuration Error: {str(e)}"}
