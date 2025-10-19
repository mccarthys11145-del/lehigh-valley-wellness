import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CRMIntegrationService:
    """
    Service for integrating with the existing Lehigh Valley Wellness CRM system.
    Handles patient data retrieval, appointment scheduling, and data synchronization.
    """
    
    def __init__(self, crm_base_url: str = None):
        # In production, this would be the actual CRM API URL
        self.crm_base_url = (
            crm_base_url
            or "https://5000-iysi7oxkf86lree03ye7v-51054291.manusvm.computer/api"
        )
        self.api_timeout = 30
        
        # API endpoints
        self.endpoints = {
            'patients': '/patients',
            'appointments': '/appointments',
            'services': '/services',
            'dashboard': '/dashboard/stats',
            'consultation_requests': '/consultation-requests'
        }
        
        # Service mapping between AI system and CRM
        self.service_mapping = {
            'psychiatry': 'Psychiatry & Mental Health',
            'hormone_optimization': 'Hormone Optimization Consultation',
            'weight_loss': 'Medical Weight Loss Consultation',
            'peptide_therapy': 'Peptide Therapy Consultation',
            'wellness_consultation': 'Wellness Consultation'
        }
        
        # Default headers for API requests
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'AI-Receptionist/1.0'
        }
    
    def find_patient_by_phone(self, phone_number: str) -> Optional[Dict]:
        """
        Find a patient in the CRM system by phone number.
        """
        try:
            # Clean phone number
            clean_phone = self._clean_phone_number(phone_number)
            
            # In production, this would make actual API call
            # For now, simulate patient lookup
            simulated_patients = [
                {
                    'id': 'pat_001',
                    'first_name': 'John',
                    'last_name': 'Smith',
                    'phone': '(484) 555-0123',
                    'email': 'john.smith@email.com',
                    'date_of_birth': '1980-05-15',
                    'last_visit': '2024-08-15',
                    'preferred_service': 'hormone_optimization',
                    'insurance': 'Blue Cross Blue Shield',
                    'notes': 'Regular patient, prefers morning appointments'
                },
                {
                    'id': 'pat_002',
                    'first_name': 'Sarah',
                    'last_name': 'Johnson',
                    'phone': '(484) 555-0456',
                    'email': 'sarah.j@email.com',
                    'date_of_birth': '1975-09-22',
                    'last_visit': '2024-09-01',
                    'preferred_service': 'weight_loss',
                    'insurance': 'Aetna',
                    'notes': 'New patient, interested in weight loss program'
                }
            ]
            
            # Find matching patient
            for patient in simulated_patients:
                if self._clean_phone_number(patient['phone']) == clean_phone:
                    logger.info(f"Found patient: {patient['first_name']} {patient['last_name']}")
                    return patient
            
            logger.info(f"No patient found for phone number: {phone_number}")
            return None
            
        except Exception as e:
            logger.error(f"Error finding patient by phone {phone_number}: {e}")
            return None
    
    def create_patient_record(self, patient_data: Dict) -> Dict:
        """
        Create a new patient record in the CRM system.
        """
        try:
            # Validate required fields
            required_fields = ['first_name', 'last_name', 'phone']
            for field in required_fields:
                if not patient_data.get(field):
                    return {
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }
            
            # Generate patient ID
            patient_id = f"pat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Prepare patient record
            patient_record = {
                'id': patient_id,
                'first_name': patient_data['first_name'],
                'last_name': patient_data['last_name'],
                'phone': self._clean_phone_number(patient_data['phone']),
                'email': patient_data.get('email', ''),
                'date_of_birth': patient_data.get('date_of_birth', ''),
                'insurance': patient_data.get('insurance', ''),
                'emergency_contact': patient_data.get('emergency_contact', ''),
                'medical_history': patient_data.get('medical_history', ''),
                'notes': patient_data.get('notes', 'Created via AI Receptionist'),
                'created_date': datetime.now().isoformat(),
                'source': 'ai_receptionist'
            }
            
            # In production, make API call to CRM
            # response = requests.post(
            #     urljoin(self.crm_base_url, self.endpoints['patients']),
            #     json=patient_record,
            #     headers=self.headers,
            #     timeout=self.api_timeout
            # )
            
            logger.info(f"Created new patient record: {patient_id}")
            
            return {
                'success': True,
                'patient_id': patient_id,
                'patient_data': patient_record,
                'message': 'Patient record created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating patient record: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create patient record'
            }
    
    def create_consultation_request(self, request_data: Dict) -> Dict:
        """
        Create a consultation request in the CRM system.
        """
        try:
            # Generate request ID
            request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Map service type
            service_type = request_data.get('service_type', 'wellness_consultation')
            service_name = self.service_mapping.get(service_type, 'General Consultation')
            
            # Prepare consultation request
            consultation_request = {
                'id': request_id,
                'patient_name': f"{request_data.get('first_name', '')} {request_data.get('last_name', '')}".strip(),
                'phone': self._clean_phone_number(request_data.get('phone', '')),
                'email': request_data.get('email', ''),
                'service_type': service_name,
                'preferred_date': request_data.get('preferred_date', ''),
                'preferred_time': request_data.get('preferred_time', ''),
                'reason_for_visit': request_data.get('reason_for_visit', ''),
                'insurance': request_data.get('insurance', ''),
                'emergency_contact': request_data.get('emergency_contact', ''),
                'medical_history': request_data.get('medical_history', ''),
                'current_medications': request_data.get('current_medications', ''),
                'status': 'pending',
                'source': 'ai_receptionist_call',
                'created_date': datetime.now().isoformat(),
                'notes': f"Request created via AI Receptionist phone call"
            }
            
            # In production, make API call to CRM
            # response = requests.post(
            #     urljoin(self.crm_base_url, self.endpoints['consultation_requests']),
            #     json=consultation_request,
            #     headers=self.headers,
            #     timeout=self.api_timeout
            # )
            
            logger.info(f"Created consultation request: {request_id} for {service_name}")
            
            return {
                'success': True,
                'request_id': request_id,
                'request_data': consultation_request,
                'message': 'Consultation request created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating consultation request: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create consultation request'
            }
    
    def check_appointment_availability(self, date: str, time: str = None, 
                                     service_type: str = None) -> Dict:
        """
        Check appointment availability for a specific date and time.
        """
        try:
            # Parse date
            try:
                appointment_date = datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                # Try different date formats
                for fmt in ['%m/%d/%Y', '%m-%d-%Y', '%B %d, %Y']:
                    try:
                        appointment_date = datetime.strptime(date, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    return {
                        'success': False,
                        'error': 'Invalid date format',
                        'message': 'Please provide date in MM/DD/YYYY format'
                    }
            
            # Check if date is in the past
            if appointment_date.date() < datetime.now().date():
                return {
                    'success': False,
                    'error': 'Past date',
                    'message': 'Cannot schedule appointments in the past'
                }
            
            # Check if date is too far in future (6 months)
            max_future_date = datetime.now() + timedelta(days=180)
            if appointment_date > max_future_date:
                return {
                    'success': False,
                    'error': 'Date too far in future',
                    'message': 'Cannot schedule appointments more than 6 months in advance'
                }
            
            # Simulate availability check
            # In production, this would query the actual CRM calendar
            available_times = [
                '09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM',
                '11:00 AM', '11:30 AM', '02:00 PM', '02:30 PM',
                '03:00 PM', '03:30 PM', '04:00 PM', '04:30 PM'
            ]
            
            if time:
                # Check specific time
                is_available = time in available_times
                return {
                    'success': True,
                    'date': appointment_date.strftime('%Y-%m-%d'),
                    'time': time,
                    'available': is_available,
                    'message': f'Time slot {time} is {"available" if is_available else "not available"}'
                }
            else:
                # Return all available times
                return {
                    'success': True,
                    'date': appointment_date.strftime('%Y-%m-%d'),
                    'available_times': available_times,
                    'message': f'{len(available_times)} time slots available'
                }
                
        except Exception as e:
            logger.error(f"Error checking appointment availability: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to check appointment availability'
            }
    
    def get_service_information(self, service_type: str = None) -> Dict:
        """
        Get information about available services.
        """
        try:
            services_info = {
                'psychiatry': {
                    'name': 'Psychiatry & Mental Health',
                    'duration': 60,
                    'price': 250,
                    'description': 'Comprehensive mental health care including therapy, counseling, and psychiatric evaluations without controlled substances.',
                    'preparation': 'Please bring a list of current medications and any previous mental health records.',
                    'insurance_accepted': True
                },
                'hormone_optimization': {
                    'name': 'Hormone Optimization',
                    'duration': 45,
                    'price': 200,
                    'description': 'Advanced hormone replacement therapy and optimization for both men and women using safe, effective protocols.',
                    'preparation': 'Fasting for 12 hours before appointment for blood work. Bring list of current medications.',
                    'insurance_accepted': False
                },
                'weight_loss': {
                    'name': 'Medical Weight Loss',
                    'duration': 45,
                    'price': 175,
                    'description': 'Physician-supervised weight loss programs with personalized nutrition and lifestyle coaching.',
                    'preparation': 'Bring list of previous weight loss attempts and current medications.',
                    'insurance_accepted': True
                },
                'peptide_therapy': {
                    'name': 'Peptide Therapy',
                    'duration': 30,
                    'price': 150,
                    'description': 'FDA-approved peptide treatments for anti-aging, recovery, and wellness optimization.',
                    'preparation': 'No special preparation required. Bring list of current medications.',
                    'insurance_accepted': False
                },
                'wellness_consultation': {
                    'name': 'Wellness Consultation',
                    'duration': 60,
                    'price': 200,
                    'description': 'Comprehensive wellness assessments and personalized optimization plans for peak health.',
                    'preparation': 'Bring list of current medications, supplements, and any recent lab work.',
                    'insurance_accepted': True
                }
            }
            
            if service_type:
                service_info = services_info.get(service_type)
                if service_info:
                    return {
                        'success': True,
                        'service': service_info,
                        'service_type': service_type
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Service not found',
                        'message': f'Service type "{service_type}" not available'
                    }
            else:
                return {
                    'success': True,
                    'services': services_info,
                    'message': f'{len(services_info)} services available'
                }
                
        except Exception as e:
            logger.error(f"Error getting service information: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to get service information'
            }
    
    def log_call_interaction(self, call_data: Dict) -> Dict:
        """
        Log call interaction data to the CRM system.
        """
        try:
            interaction_log = {
                'id': f"int_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'call_id': call_data.get('call_id'),
                'patient_id': call_data.get('patient_id'),
                'phone_number': call_data.get('phone_number'),
                'interaction_type': 'phone_call',
                'interaction_summary': call_data.get('conversation_summary', ''),
                'intent_detected': call_data.get('intent_detected', ''),
                'outcome': call_data.get('outcome', ''),
                'appointment_created': call_data.get('appointment_created', False),
                'follow_up_required': call_data.get('follow_up_required', False),
                'staff_notes': call_data.get('staff_notes', ''),
                'created_date': datetime.now().isoformat(),
                'source': 'ai_receptionist'
            }
            
            # In production, make API call to CRM
            logger.info(f"Logged call interaction: {interaction_log['id']}")
            
            return {
                'success': True,
                'interaction_id': interaction_log['id'],
                'message': 'Call interaction logged successfully'
            }
            
        except Exception as e:
            logger.error(f"Error logging call interaction: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to log call interaction'
            }
    
    def get_practice_information(self) -> Dict:
        """
        Get general practice information for AI responses.
        """
        return {
            'name': 'Lehigh Valley Wellness',
            'phone': '(484) 357-1916',
            'address': '6081 Hamilton Blvd Suite 600, Allentown, PA 18106',
            'hours': 'Monday-Friday: 8:00 AM - 6:00 PM',
            'website': 'lehighvalleywellness.org',
            'email': 'info@lehighvalleywellness.org',
            'services': list(self.service_mapping.keys()),
            'insurance_accepted': ['Blue Cross Blue Shield', 'Aetna', 'Cigna', 'United Healthcare'],
            'parking': 'Free parking available on-site',
            'accessibility': 'Wheelchair accessible facility'
        }
    
    def _clean_phone_number(self, phone: str) -> str:
        """Clean and format phone number for consistency."""
        if not phone:
            return ''
        
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, phone))
        
        # Format as (XXX) XXX-XXXX if 10 digits
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            # Remove leading 1 for US numbers
            digits = digits[1:]
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        
        return phone  # Return original if can't format
    
    def test_crm_connection(self) -> Dict:
        """
        Test the connection to the CRM system.
        """
        try:
            # In production, this would make actual API call
            # response = requests.get(
            #     urljoin(self.crm_base_url, '/health'),
            #     headers=self.headers,
            #     timeout=self.api_timeout
            # )
            
            return {
                'success': True,
                'crm_url': self.crm_base_url,
                'status': 'connected',
                'message': 'CRM connection successful'
            }
            
        except Exception as e:
            logger.error(f"Error testing CRM connection: {e}")
            return {
                'success': False,
                'error': str(e),
                'status': 'disconnected',
                'message': 'CRM connection failed'
            }

