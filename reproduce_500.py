import os
import django
import asyncio
from asgiref.sync import async_to_sync

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maternal_gateway.settings')
django.setup()

from core_api.services.supabase_service import SupabaseService
from core_api.services.ai_service import AIService

async def test_upload_flow():
    test_file = 'login.html' # Just a dummy file for path testing
    print(f"Testing flow with {test_file}")
    
    try:
        print("1. Testing AI Analysis...")
        ai_result = await AIService.analyze_scan(test_file)
        print(f"AI Result: {ai_result}")
        
        print("2. Testing DB Metadata Save (Sanitized)...")
        db_metadata = {
            "filename": "test_repro.jpg",
            "image_url": "https://example.com/test.jpg",
            "maternal_id": "TEST_ID",
            "processed_as": "IMAGE"
        }
        db_result = await SupabaseService.save_scan_metadata(db_metadata)
        print(f"DB Result: {db_result}")
        
        print("SUCCESS: Full flow logic works.")
    except Exception as e:
        print(f"FAILURE: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_upload_flow())
