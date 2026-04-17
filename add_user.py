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

def get_user_id(email):
    url = f"{SUPABASE_URL}/auth/v1/admin/users"
    with httpx.Client() as client:
        response = client.get(url, headers=headers)
        if response.status_code == 200:
            users = response.json().get("users", [])
            for user in users:
                if user.get("email") == email:
                    return user.get("id")
        return None

def add_or_update_user(email, password):
    user_id = get_user_id(email)
    
    if user_id:
        print(f"[INFO] User {email} already exists (ID: {user_id}). Updating password...")
        url = f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}"
        data = {"password": password}
        with httpx.Client() as client:
            response = client.put(url, json=data, headers=headers)
            if response.status_code == 200:
                print("[SUCCESS] Password updated successfully.")
            else:
                print(f"[FAILURE] Failed to update password: {response.status_code}")
                print(response.text)
    else:
        print(f"Attempting to create user: {email}")
        url = f"{SUPABASE_URL}/auth/v1/admin/users"
        data = {
            "email": email,
            "password": password,
            "email_confirm": True
        }
        with httpx.Client() as client:
            response = client.post(url, json=data, headers=headers)
            if response.status_code == 201:
                print("[SUCCESS] User created successfully.")
            else:
                print(f"[FAILURE] Failed to create user: {response.status_code}")
                print(response.text)

if __name__ == "__main__":
    add_or_update_user("kamauprecious84@gmail.com", "maternal01")
