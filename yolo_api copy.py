# 1. Import the library
from inference_sdk import InferenceHTTPClient

# 2. Connect to your workflow
client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="VlMlrQc1hkjaUrctNPdh"
)

# 3. Run your workflow on an image
result = client.run_workflow(
    workspace_name="preciouss-workspace-5hkb5",
    workflow_id="detect-count-and-visualize",
    images={
        "image": "YOUR_IMAGE.jpg" # Path to your image file
    },
    use_cache=True # Speeds up repeated requests
)

# 4. Get your results
print(result)



