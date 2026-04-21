import httpx
import os

API_KEY = "VlMlrQc1hkjaUrctNPdh"
MODEL_ID = "abnormal-fetal-gl9hv/1"
IMAGE_PATH = "temp_uploads/test_scan.png"

def test_direct_model_form():
    if not os.path.exists(IMAGE_PATH):
        print(f"File {IMAGE_PATH} not found.")
        return

    # Standard Object Detection URL
    url = f"https://detect.roboflow.com/{MODEL_ID}"
    params = {"api_key": API_KEY}
    
    try:
        with open(IMAGE_PATH, "rb") as f:
            files = {"file": f}
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, params=params, files=files)
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    print("SUCCESS")
                    print(response.json())
                else:
                    print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_direct_model_form()
