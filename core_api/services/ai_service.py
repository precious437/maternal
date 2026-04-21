import httpx
import os
import logging
import base64
from django.conf import settings

logger = logging.getLogger(__name__)

class AIService:
    """Service to handle Direct AI Inference via Roboflow Object Detection API"""
    
    # Switch from Workflows to Direct Inference for stability and permission bypass
    BASE_URL = "https://detect.roboflow.com"
    
    API_KEY = getattr(settings, 'ROBOFLOW_API_KEY', os.getenv("ROBOFLOW_API_KEY", "VlMlrQc1hkjaUrctNPdh"))
    # Use the model confirmed in the user screenshot
    PRIMARY_MODEL = "abnormal-fetal-gl9hv/1"
    
    @staticmethod
    def analyze_scan(file_path):
        """Send image directly to the Abnormal Fetal model"""
        if not AIService.API_KEY or AIService.API_KEY == "YOUR_API_KEY":
            logger.warning("AIService: No Roboflow API Key configured.")
            return {"success": False, "error": "AI Configuration missing"}

        if not os.path.exists(file_path):
            return {"success": False, "error": "Scan file not found"}

        try:
            url = f"{AIService.BASE_URL}/{AIService.PRIMARY_MODEL}"
            params = {"api_key": AIService.API_KEY}
            
            with open(file_path, "rb") as image_file:
                # Use multipart/form-data for the direct inference API
                files = {"file": image_file}
                with httpx.Client(timeout=30.0) as client:
                    response = client.post(url, params=params, files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        logger.info(f"Roboflow direct response: {result}")
                        return AIService.process_inference_result(result)
                    else:
                        logger.error(f"Roboflow API error: {response.status_code} - {response.text}")
                        return {"success": False, "error": f"AI Inference failed (Status {response.status_code})"}
                    
        except Exception as e:
            logger.error(f"AIService: Analysis failed: {str(e)}")
            return {"success": False, "error": "AI Service unreachable"}

    @staticmethod
    def process_inference_result(result):
        """Extract predictions from the Direct Inference API response"""
        predictions = result.get("predictions", [])
        img_info = result.get("image", {})
        img_w = img_info.get("width", 1024)
        img_h = img_info.get("height", 1024)
        
        if not predictions:
            return {"success": True, "anomalies": [], "count": 0, "status": "Clear Scan"}

        # Clinical Encyclopedia for detailed descriptions
        explanations = {
            "CSP": "Cavum Septum Pellucidum identified. Presence is a key indicator of normal midline brain development.",
            "ABNORMAL": "Pathological structural variance detected. Immediate clinical review advised.",
            "CYST": "Fluid-filled structure observed. Monitoring for progression or regression required.",
            "HYDROCEPHALUS": "Ventricle dilation detected with high confidence. Potential intracranial pressure monitoring needed.",
            "MIDLINE_FALX": "Midline Falx cerebri detected. Confirms symmetrical hemispheric division."
        }

        anomalies = []
        for pred in predictions:
            label = pred.get("class", "Target").upper()
            confidence = round(float(pred.get("confidence", 0)), 3)
            
            # Direct API returns center x,y + w,h
            cx = float(pred.get("x", 0))
            cy = float(pred.get("y", 0))
            bw = float(pred.get("width", 0))
            bh = float(pred.get("height", 0))
            
            is_anomaly = any(word in label.lower() for word in ["abnormal", "anomaly", "lesion", "defect", "cyst", "fluid"])
            
            detail = explanations.get(label, "Structural architecture identified for clinical mapping. Symmetry and density markers observed.")

            anomalies.append({
                "label":       label,
                "confidence":  confidence,
                "is_anomaly":  is_anomaly or (confidence > 0.85),
                "bbox": [
                    round(cx - bw / 2, 1), # x_left
                    round(cy - bh / 2, 1), # y_top
                    round(bw, 1),
                    round(bh, 1),
                ],
                "img_w": img_w,
                "img_h": img_h,
                "description": detail
            })

        return {
            "success":   True,
            "anomalies": anomalies,
            "count":     len(anomalies),
        }

    @staticmethod
    def apply_clinical_fallback():
        return {"success": True, "anomalies": [], "count": 0, "status": "Initialized"}
