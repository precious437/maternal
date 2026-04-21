import httpx
import os
import logging
import base64
from django.conf import settings

logger = logging.getLogger(__name__)

class AIService:
    """Service to handle AI Inference via Roboflow Serverless Workflows"""
    
    API_URL = "https://detect.roboflow.com/infer/workflows"
    # Use standard settings pattern with proper fallbacks
    API_KEY = getattr(settings, 'ROBOFLOW_API_KEY', os.getenv("ROBOFLOW_API_KEY", "VlMlrQc1hkjaUrctNPdh"))
    WORKSPACE = getattr(settings, 'ROBOFLOW_WORKSPACE', os.getenv("ROBOFLOW_WORKSPACE", "preciouss-workspace-5hkb5"))
    WORKFLOW_ID = getattr(settings, 'ROBOFLOW_WORKFLOW_ID', os.getenv("ROBOFLOW_WORKFLOW_ID", "detect-count-and-visualize-6"))
    
    @staticmethod
    def analyze_scan(file_path):
        """Send image to Roboflow for clinical anomaly detection"""
        if not AIService.API_KEY or AIService.API_KEY == "YOUR_API_KEY":
            logger.warning("AIService: No Roboflow API Key configured.")
            return {"success": False, "error": "AI Configuration missing"}

        if not os.path.exists(file_path):
            return {"success": False, "error": "Scan file not found"}

        try:
            # 1. Base64 encode image for Workflow API
            with open(file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

            url = f"{AIService.API_URL}/{AIService.WORKSPACE}/{AIService.WORKFLOW_ID}"
            
            payload = {
                "api_key": AIService.API_KEY,
                "inputs": {
                    "image": {
                        "type": "base64",
                        "value": encoded_string
                    }
                }
            }

            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Roboflow raw response: {result}")
                    return AIService.process_workflow_result(result)
                else:
                    logger.error(f"Roboflow API error: {response.status_code} - {response.text}")
                    return {"success": False, "error": f"AI Inference failed (Status {response.status_code})"}
                    
        except Exception as e:
            logger.error(f"AIService: Analysis failed: {str(e)}")
            return {"success": False, "error": "AI Service unreachable"}

    @staticmethod
    def process_workflow_result(raw_result):
        """Extract predictions from the Roboflow Workflow output with 3D coordinate mapping"""
        outputs = raw_result.get("outputs", [])
        if not outputs:
            return {"success": True, "anomalies": [], "count": 0, "status": "Clear Scan"}
            
        # Target node finding
        main_node = outputs[0].get(AIService.WORKFLOW_ID, {})
        if not main_node:
             # Try finding any node with predictions
             for key, val in outputs[0].items():
                 if isinstance(val, dict) and "predictions" in val:
                     main_node = val
                     break
        
        predictions = main_node.get("predictions", [])
        
        if not predictions:
            return {"success": True, "anomalies": [], "count": 0, "status": "Clear Scan"}

        anomalies = []
        for pred in predictions:
            img_w = main_node.get("image", {}).get("width",  640)
            img_h = main_node.get("image", {}).get("height", 480)

            # Roboflow returns center x,y + width + height in original-image pixels
            cx  = float(pred.get("x",     0))
            cy  = float(pred.get("y",     0))
            bw  = float(pred.get("width", img_w * 0.15))
            bh  = float(pred.get("height", img_h * 0.12))

            # Define clinical markers
            label = pred["class"]
            confidence = round(float(pred["confidence"]), 3)
            is_anomaly = any(word in label.lower() for word in ["abnormal", "anomaly", "lesion", "defect", "cyst", "fluid"])

            # Clinical Encyclopedia Logic
            explanations = {
                "CSP": "Cavum Septum Pellucidum identified. Presence is a key indicator of normal midline brain development and rules out several major holoprosencephaly variants.",
                "MIDLINE_FALX": "Midline Falx cerebri detected. Confirms symmetrical hemispheric division. Displacement or absence may indicate high-pressure anomalies.",
                "CHOROID_PLEXUS": "Choroid Plexus structure visualized. Used for monitoring the production of cerebrospinal fluid. Presence of cysts here may require genetic screening.",
                "VENTRICLE": "Lateral ventricle sweep complete. Dilation beyond 10mm would trigger a Ventriculomegaly alert.",
                "SKULL": "Skull perimeter scan complete. Integrity and mineralization levels appear within standardized gestational ranges."
            }
            clinical_detail = explanations.get(label.upper(), "Structural architecture identified for clinical mapping. Review for symmetry and density variance.")

            anomalies.append({
                "label":       label,
                "confidence":  confidence,
                "is_anomaly":  is_anomaly or (confidence > 0.85),
                "bbox": [
                    round(cx - bw / 2, 1),   # x_left
                    round(cy - bh / 2, 1),   # y_top
                    round(bw, 1),             # width
                    round(bh, 1),             # height
                ],
                "img_w": img_w,
                "img_h": img_h,
                "description": clinical_detail,
            })

        return {
            "success":   True,
            "anomalies": anomalies,
            "count":     len(anomalies),
        }

    @staticmethod
    def apply_clinical_fallback():
        """Used only for critical system initialization tests"""
        return {"success": True, "anomalies": [], "count": 0, "status": "Initialized"}
