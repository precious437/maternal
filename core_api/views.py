from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.shortcuts import render
from .services.supabase_service import SupabaseService
from .services.ai_service import AIService
import os
import asyncio
import uuid
from asgiref.sync import async_to_sync

# Import the existing DICOM processor
import sys
sys.path.append(os.path.join(settings.BASE_DIR))
from dicom_processor import DICOMProcessor

class VitalsView(APIView):
    def post(self, request):
        try:
            data = request.data
            result = async_to_sync(SupabaseService.save_vitals)(data)
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class FileUploadView(APIView):
    def post(self, request):
        temp_path = None
        try:
            if 'image' not in request.FILES:
                return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
            
            uploaded_file = request.FILES['image']
            original_filename = os.path.basename(uploaded_file.name)
            file_ext = os.path.splitext(original_filename)[1].lower()
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            
            # 1. Prepare temp upload path
            temp_dir = os.path.join(settings.BASE_DIR, 'temp_uploads')
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, unique_filename)
            
            # Default metadata for non-DICOM
            metadata = {
                "filename": original_filename,
                "type": "2D Clinical Scan",
                "timestamp": str(uuid.uuid4())[:8]
            }
            
            # Save file to temp location
            with open(temp_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # 2. Process DICOM metadata (Only if .dcm)
            if file_ext == '.dcm':
                try:
                    processor = DICOMProcessor()
                    dicom_data = processor.process_dicom_file(temp_path)
                    metadata.update(dicom_data)
                except Exception as dex:
                    print(f"DICOM Parsing Skip: {str(dex)}")

            # 3. Upload to Supabase Storage (Core Task)
            uploaded_file.seek(0)
            upload_result = async_to_sync(SupabaseService.upload_file)(uploaded_file, unique_filename)
            
            if not upload_result.get("success"):
                return Response({"error": f"Storage failure: {upload_result.get('error')}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 4. AI Analysis (Isolated Task)
            ai_result = {"success": False, "error": "AI evaluation skipped"}
            try:
                ai_result = async_to_sync(AIService.analyze_scan)(temp_path)
            except Exception as aix:
                print(f"AI Service Skip: {str(aix)}")

            # 5. Save metadata to DB (History)
            db_metadata = {
                "filename": original_filename,
                "image_url": upload_result.get("url"),
                "processed_as": "DICOM" if file_ext == '.dcm' else "IMAGE",
                "analysis_results": ai_result  # Save findings for later inspection
            }
            
            async_to_sync(SupabaseService.save_scan_metadata)(db_metadata)

            return Response({
                "success": True,
                "metadata": metadata,
                "digital_twin": ai_result,
                "image_url": upload_result.get("url")
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"CRITICAL UPLOAD ERROR: {str(e)}")
            return Response({"error": f"Critical upload failure: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if temp_path:
                # Ensure file is closed before removal
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except Exception as rex:
                    print(f"Laten Cleanup Warning: {str(rex)}")

class LoginView(APIView):
    def post(self, request):
        try:
            email = request.data.get("email")
            password = request.data.get("password")
            result = async_to_sync(SupabaseService.verify_login)(email, password)
            if result.get("success"):
                return Response(result, status=status.HTTP_200_OK)
            return Response(result, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class SignupView(APIView):
    def post(self, request):
        try:
            email = request.data.get("email")
            password = request.data.get("password")
            result = async_to_sync(SupabaseService.signup_user)(email, password)
            if result.get("success"):
                return Response(result, status=status.HTTP_201_CREATED)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class HistoryView(APIView):
    def get(self, request):
        try:
            result = async_to_sync(SupabaseService.get_scan_history)()
            return Response({"success": True, "history": result}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# --- FRONTEND VIEWS ---
def home_view(request):
    return render(request, 'index.html')

def surgical_view(request):
    return render(request, 'surgical.html')

def login_view(request):
    return render(request, 'login.html')

def settings_view(request):
    return render(request, 'settings.html')

def help_view(request):
    return render(request, 'help.html')
