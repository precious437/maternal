import httpx
import base64
import os
import json

# 1. Configuration (matches original yolo_api.py logic)
# We use the REST endpoint directly for Python 3.13 compatibility
API_URL = "https://detect.roboflow.com/infer/workflows"
API_KEY = "VlMlrQc1hkjaUrctNPdh"
WORKSPACE = "preciouss-workspace-5hkb5"
WORKFLOW_ID = "detect-count-and-visualize"
IMAGE_PATH = os.path.join("temp_uploads", "test_scan.png")

def run_analysis():
    # 2. Prepare the image
    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_image_path = os.path.join(current_dir, IMAGE_PATH)
    
    if not os.path.exists(full_image_path):
        print(f"Error: {full_image_path} not found.")
        return

    with open(full_image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

    # 3. Construct the request
    url = f"{API_URL}/{WORKSPACE}/{WORKFLOW_ID}"
    payload = {
        "api_key": API_KEY,
        "inputs": {
            "image": {
                "type": "base64",
                "value": encoded_string
            }
        }
    }

    # 4. Execute the call
    print(f"Analyzing {IMAGE_PATH} via Roboflow Serverless Workflows...")
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # 5. Output results
            print("\n--- ANALYSIS RESULTS ---")
            print(json.dumps(result, indent=2))
            
    except Exception as e:
        print(f"Analysis failed: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Response Details: {e.response.text}")

if __name__ == "__main__":
    run_analysis()
