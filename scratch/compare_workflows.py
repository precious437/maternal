import httpx
import base64
import os

API_KEY = "VlMlrQc1hkjaUrctNPdh"
WORKSPACE = "preciouss-workspace-5hkb5"
IMAGE_PATH = "temp_uploads/test_scan.png"

def test_workflow(workflow_id):
    url = f"https://detect.roboflow.com/infer/workflows/{WORKSPACE}/{workflow_id}"
    
    with open(IMAGE_PATH, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
        
    payload = {
        "api_key": API_KEY,
        "inputs": {
            "image": {
                "type": "base64",
                "value": encoded
            }
        }
    }
    
    print(f"\n--- Testing {workflow_id} ---")
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("SUCCESS")
                # print(response.json())
            else:
                print(f"Error: {response.text}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    if os.path.exists(IMAGE_PATH):
        test_workflow("detect-count-and-visualize-6")
        test_workflow("detect-count-and-visualize")
    else:
        print(f"File {IMAGE_PATH} not found.")
