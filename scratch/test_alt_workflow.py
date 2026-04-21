import httpx

API_KEY = "VlMlrQc1hkjaUrctNPdh"
WORKSPACE = "preciouss-workspace-5hkb5"
WORKFLOW_ID = "detect-count-and-visualize" # No -6

def test():
    url = f"https://detect.roboflow.com/infer/workflows/{WORKSPACE}/{WORKFLOW_ID}"
    payload = {
        "api_key": API_KEY,
        "inputs": {
            "image": {
                "type": "base64",
                "value": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BvAAMDAZ/8v9L9AAAAAElFTkSuQmCC"
            }
        }
    }
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(url, json=payload)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
