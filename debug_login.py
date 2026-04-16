import os
import django
import httpx
import asyncio

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maternal_gateway.settings')
django.setup()

from django.conf import settings

async def debug_login(email, password):
    url = f"{settings.SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {
        "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
        "Content-Type": "application/json"
    }
    data = {"email": email, "password": password}
    
    print(f"Attempting login for: {email} at {url}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data, headers=headers)
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text}")
        except Exception as e:
            print(f"Network error: {str(e)}")

if __name__ == "__main__":
    import sys
    email = sys.argv[1] if len(sys.argv) > 1 else "doctor@medical.com"
    password = sys.argv[2] if len(sys.argv) > 2 else "password123"
    asyncio.run(debug_login(email, password))
