import httpx
import base64
import os

API_KEY = "VlMlrQc1hkjaUrctNPdh"
MODEL_ID = "abnormal-fetal-gl9hv/1"
IMAGE_PATH = "temp_uploads/test_scan.png"

def test_direct_model():
    if not os.path.exists(IMAGE_PATH):
        print(f"File {IMAGE_PATH} not found.")
        return

    url = f"https://detect.roboflow.com/{MODEL_ID}"
    
    with open(IMAGE_PATH, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
        
    params = {
        "api_key": API_KEY,
    }
    
    # Roboflow direct API expects image as part of params or as raw data
    # For simplicity, we'll try the standard POST with b64 in body per their docs
    try:
        with httpx.Client(timeout=30.0) as client:
            # We send the b64 string directly as the body for some model types
            response = client.post(url, params=params, content=encoded)
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("SUCCESS: Direct Model Access Granted")
                print(response.json())
            else:
                print(f"Failed: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_direct_model()
