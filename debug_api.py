import os
import django
import asyncio
from asgiref.sync import async_to_sync

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maternal_gateway.settings')
django.setup()

from core_api.services.ai_service import AIService
from core_api.services.supabase_service import SupabaseService
from django.conf import settings

async def debug_upload():
    test_file = "temp_uploads/test_scan.png"
    if not os.path.exists(test_file):
        print(f"FAILED: {test_file} not found")
        return

    print("--- Testing AIService ---")
    try:
        ai_result = await AIService.analyze_scan(test_file)
        print(f"AI Result: {ai_result}")
    except Exception as e:
        print(f"AI Exception: {e}")

    print("\n--- Testing Supabase Upload ---")
    try:
        with open(test_file, 'rb') as f:
            # Mocking a file object for upload_file
            class MockFile:
                def __init__(self, file): self.file = file
                def read(self): return self.file.read()
            
            mock = MockFile(f)
            upload_result = await SupabaseService.upload_file(mock, "debug_test.png")
            print(f"Upload Result: {upload_result}")
    except Exception as e:
        print(f"Upload Exception: {e}")

if __name__ == "__main__":
    asyncio.run(debug_upload())
