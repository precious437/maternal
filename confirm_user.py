import httpx
import os

# Configuration from .env
SUPABASE_URL = "https://piqgorbfudvcmgzxxklv.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBpcWdvcmJmdWR2Y21nenh4a2x2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDk5MzkyMywiZXhwIjoyMDkwNTY5OTIzfQ.MAKC2uHzL2eJwIb9obP6F3xMb2fys3-bbvpTCfsX8G4"

headers = {
    "apikey": SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
    "Content-Type": "application/json"
}

def confirm_user(email):
    with httpx.Client() as client:
        # Find user ID first
        url_list = f"{SUPABASE_URL}/auth/v1/admin/users"
        user_id = None
        resp = client.get(url_list, headers=headers)
        if resp.status_code == 200:
            users = resp.json().get("users", [])
            for u in users:
                if u.get("email") == email:
                    user_id = u.get("id")
                    break
    
        if user_id:
            print(f"Confirming user: {email} (ID: {user_id})")
            url_update = f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}"
            data = {
                "email_confirm": True
            }
            resp = client.put(url_update, json=data, headers=headers)
            if resp.status_code == 200:
                print("[SUCCESS] User confirmed.")
                return True
            else:
                print(f"[FAILURE] Failed to confirm: {resp.status_code}")
                print(resp.text)
        else:
            print(f"[ERROR] User {email} not found.")
    return False

if __name__ == "__main__":
    confirm_user("kamauprecious84@gmail.com")
