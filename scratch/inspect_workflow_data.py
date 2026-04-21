import httpx
import base64
import os
import json

API_KEY = "VlMlrQc1hkjaUrctNPdh"
WORKSPACE = "preciouss-workspace-5hkb5"
IMAGE_PATH = "temp_uploads/test_scan.png"

def test_workflow(workflow_id):
    url = f"https://detect.roboflow.com/infer/workflows/{WORKSPACE}/{workflow_id}"
    with open(IMAGE_PATH, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    payload = { "api_key": API_KEY, "inputs": { "image": { "type": "base64", "value": encoded } } }
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload)
            if response.status_code == 200:
                res_data = response.json()
                print(f"\n--- {workflow_id} Output Keys ---")
                outputs = res_data.get("outputs", [{}])[0]
                print(list(outputs.keys()))
                # Check for predictions in ANY of the keys
                for k, v in outputs.items():
                    if isinstance(v, dict) and "predictions" in v:
                        print(f"Key '{k}' contains {len(v['predictions'])} predictions")
            else:
                print(f"Error {workflow_id}: {response.status_code}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_workflow("detect-count-and-visualize-6")
    test_workflow("detect-count-and-visualize")
