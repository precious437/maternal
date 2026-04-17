import httpx
import os

# Configuration from .env
SUPABASE_URL = "https://piqgorbfudvcmgzxxklv.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBpcWdvcmJmdWR2Y21nenh4a2x2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ5OTM5MjMsImV4cCI6MjA5MDU2OTkyM30.ZQiYTl8WznhfYIkIEANTMHfJ_v17uvaDAMO96LbN2-8"

def verify_login(email, password):
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }
    data = {"email": email, "password": password}
    print(f"Testing login for: {email}")
    try:
        with httpx.Client() as client:
            response = client.post(url, json=data, headers=headers)
            if response.status_code == 200:
                print("[SUCCESS] Login verified.")
                return True
            else:
                print(f"[FAILURE] Login failed: {response.status_code}")
                print(response.text)
                return False
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        return False

if __name__ == "__main__":
    verify_login("kamauprecious84@gmail.com", "maternal01")
