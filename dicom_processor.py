"""
DICOM File Processing Module
Handles medical image processing from MRI machines
"""

import os
from datetime import datetime
import pydicom
from pathlib import Path

class DICOMProcessor:
    """Process DICOM files from medical imaging devices"""
    
    def __init__(self):
        self.dicom_folder = 'dicom_files'
        if not os.path.exists(self.dicom_folder):
            os.makedirs(self.dicom_folder)
    
    def process_dicom_file(self, file_path):
        """Extract metadata from DICOM file"""
        try:
            dicom_file = pydicom.dcmread(file_path)
            
            # Extract key medical information
            metadata = {
                'success': True,
                'patient_name': str(dicom_file.get('PatientName', 'Unknown')),
                'patient_id': str(dicom_file.get('PatientID', 'Unknown')),
                'modality': str(dicom_file.get('Modality', 'MRI')),
                'study_date': str(dicom_file.get('StudyDate', 'Unknown')),
                'study_time': str(dicom_file.get('StudyTime', 'Unknown')),
                'manufacturer': str(dicom_file.get('Manufacturer', 'Unknown')),
                'manufacturer_model': str(dicom_file.get('ManufacturerModelName', 'Unknown')),
                'body_part_examined': str(dicom_file.get('BodyPartExamined', 'Unknown')),
                'protocol_name': str(dicom_file.get('ProtocolName', 'Unknown')),
                'acquisition_date': str(dicom_file.get('AcquisitionDate', datetime.now().strftime('%Y%m%d'))),
                'pixel_spacing': str(dicom_file.get('PixelSpacing', 'Unknown')),
                'bits_allocated': str(dicom_file.get('BitsAllocated', 'Unknown')),
                'processing_timestamp': datetime.now().isoformat()
            }
            
            return metadata
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_timestamp': datetime.now().isoformat()
            }
    
    def save_dicom(self, file_data, filename):
        """Save uploaded DICOM file"""
        try:
            # Sanitize filename to prevent path injection
            safe_filename = os.path.basename(filename)
            file_path = os.path.join(self.dicom_folder, safe_filename)
            with open(file_path, 'wb') as f:
                f.write(file_data)
            return {'success': True, 'path': file_path}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_dicom_list(self):
        """Get list of all stored DICOM files"""
        try:
            files = []
            for file in os.listdir(self.dicom_folder):
                if file.endswith('.dcm'):
                    file_path = os.path.join(self.dicom_folder, file)
                    files.append({
                        'filename': file,
                        'path': file_path,
                        'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                    })
            return files
        except Exception as e:
            return []
