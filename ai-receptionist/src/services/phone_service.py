import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import requests
from flask import current_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PhoneService:
    """
    Service for handling phone calls, voice processing, and telephony integration.
    This service manages call routing, voice-to-text conversion, text-to-speech,
    and integration with VoIP providers.
    """
    
    def __init__(self):
        self.practice_phone = "484-357-1916"
        self.emergency_numbers = {
            'emergency': '911',
            'practice_emergency': '484-357-1916',  # Same number for now
            'on_call': '484-357-1916'  # Would be configured with actual on-call number
        }
        
        # Voice settings
        self.voice_settings = {
            'voice_id': 'female_voice',  # Default voice
            'speech_rate': 1.0,
            'speech_volume': 0.8,
            'language': 'en-US'
        }
        
        # Call routing rules
        self.routing_rules = {
            'business_hours': {
                'start': '08:00',
                'end': '18:00',
                'days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
            },
            'emergency_keywords': [
                'emergency', 'urgent', 'chest pain', 'can\'t breathe', 
                'bleeding', 'overdose', 'suicide', 'help me'
            ]
        }
    
    def initiate_call(self, phone_number: str, call_type: str = 'outbound') -> Dict:
        """
        Initiate an outbound call to a patient.
        This would integrate with a VoIP service like Twilio in production.
        """
        try:
            # In production, this would use Twilio or similar service
            call_data = {
                'call_id': f"call_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{phone_number[-4:]}",
                'phone_number': phone_number,
                'call_type': call_type,
                'status': 'initiated',
                'start_time': datetime.now().isoformat(),
                'direction': 'outbound'
            }
            
            logger.info(f"Initiating call to {phone_number}")
            
            # Simulate call initiation
            # In production: 
            # client = twilio.rest.Client(account_sid, auth_token)
            # call = client.calls.create(
            #     to=phone_number,
            #     from_=self.practice_phone,
            #     url='https://your-domain.com/voice/handle'
            # )
            
            return {
                'success': True,
                'call_id': call_data['call_id'],
                'message': f'Call initiated to {phone_number}',
                'call_data': call_data
            }
            
        except Exception as e:
            logger.error(f"Error initiating call to {phone_number}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to initiate call to {phone_number}'
            }
    
    def handle_incoming_call(self, call_data: Dict) -> Dict:
        """
        Handle an incoming call and determine routing.
        """
        try:
            caller_number = call_data.get('from', 'Unknown')
            call_id = call_data.get('call_id', f"incoming_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            logger.info(f"Handling incoming call from {caller_number}")
            
            # Check if it's business hours
            is_business_hours = self._is_business_hours()
            
            # Prepare call handling response
            response = {
                'call_id': call_id,
                'caller_number': caller_number,
                'is_business_hours': is_business_hours,
                'routing_decision': 'ai_receptionist',
                'greeting_message': self._generate_greeting(is_business_hours)
            }
            
            # Log call start
            logger.info(f"Call {call_id} routed to AI receptionist")
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling incoming call: {e}")
            return {
                'error': str(e),
                'routing_decision': 'voicemail',
                'greeting_message': "We're sorry, but we're experiencing technical difficulties. Please leave a message."
            }
    
    def convert_speech_to_text(self, audio_data: bytes, call_id: str) -> Dict:
        """
        Convert speech audio to text using speech recognition.
        In production, this would use services like Google Speech-to-Text or Azure Speech.
        """
        try:
            # Simulate speech-to-text conversion
            # In production, you would use:
            # - Google Cloud Speech-to-Text API
            # - Azure Cognitive Services Speech
            # - AWS Transcribe
            # - OpenAI Whisper API
            
            # For demonstration, we'll simulate the process
            simulated_text = "Hello, I'd like to schedule an appointment for hormone optimization therapy."
            
            result = {
                'success': True,
                'transcript': simulated_text,
                'confidence': 0.95,
                'language': 'en-US',
                'processing_time': 1.2,
                'call_id': call_id,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Speech-to-text completed for call {call_id}: {simulated_text[:50]}...")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in speech-to-text conversion for call {call_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'transcript': '',
                'confidence': 0.0
            }
    
    def convert_text_to_speech(self, text: str, call_id: str, voice_settings: Dict = None) -> Dict:
        """
        Convert text to speech audio for AI responses.
        In production, this would use TTS services like Google Text-to-Speech or Azure Speech.
        """
        try:
            if voice_settings is None:
                voice_settings = self.voice_settings
            
            # Simulate text-to-speech conversion
            # In production, you would use:
            # - Google Cloud Text-to-Speech API
            # - Azure Cognitive Services Speech
            # - AWS Polly
            # - OpenAI TTS API
            
            result = {
                'success': True,
                'audio_url': f'/audio/tts_{call_id}_{datetime.now().strftime("%H%M%S")}.wav',
                'text': text,
                'voice_settings': voice_settings,
                'duration': len(text.split()) * 0.6,  # Estimate 0.6 seconds per word
                'call_id': call_id,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Text-to-speech completed for call {call_id}: {len(text)} characters")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in text-to-speech conversion for call {call_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'audio_url': None
            }
    
    def transfer_call(self, call_id: str, transfer_type: str, reason: str = '') -> Dict:
        """
        Transfer a call to human staff or emergency services.
        """
        try:
            transfer_destinations = {
                'emergency': self.emergency_numbers['emergency'],
                'on_call': self.emergency_numbers['on_call'],
                'reception': self.practice_phone,
                'billing': self.practice_phone,  # Would be separate number in production
                'voicemail': 'voicemail_system'
            }
            
            destination = transfer_destinations.get(transfer_type, 'reception')
            
            logger.info(f"Transferring call {call_id} to {transfer_type}: {reason}")
            
            # In production, this would use telephony API to transfer the call
            result = {
                'success': True,
                'call_id': call_id,
                'transfer_type': transfer_type,
                'destination': destination,
                'reason': reason,
                'transfer_time': datetime.now().isoformat(),
                'message': f'Call transferred to {transfer_type}'
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error transferring call {call_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to transfer call {call_id}'
            }
    
    def end_call(self, call_id: str, reason: str = 'completed') -> Dict:
        """
        End a phone call and clean up resources.
        """
        try:
            logger.info(f"Ending call {call_id}: {reason}")
            
            result = {
                'success': True,
                'call_id': call_id,
                'end_reason': reason,
                'end_time': datetime.now().isoformat(),
                'message': 'Call ended successfully'
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error ending call {call_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Error ending call {call_id}'
            }
    
    def make_appointment_confirmation_call(self, patient_phone: str, appointment_data: Dict) -> Dict:
        """
        Make an outbound call to confirm an appointment.
        """
        try:
            call_result = self.initiate_call(patient_phone, 'appointment_confirmation')
            
            if call_result['success']:
                # Generate confirmation message
                service_name = appointment_data.get('service_name', 'consultation')
                appointment_date = appointment_data.get('date', 'your scheduled date')
                appointment_time = appointment_data.get('time', 'your scheduled time')
                
                message = f"""Hello, this is {current_app.config.get('PRACTICE_NAME', 'Lehigh Valley Wellness')} calling to confirm your {service_name} appointment scheduled for {appointment_date} at {appointment_time}.
                
Please press 1 to confirm, 2 to reschedule, or stay on the line to speak with our staff.

If you need to make any changes, you can also call us at {self.practice_phone}.

Thank you!"""
                
                # Convert message to speech
                tts_result = self.convert_text_to_speech(message, call_result['call_id'])
                
                return {
                    'success': True,
                    'call_id': call_result['call_id'],
                    'message': 'Appointment confirmation call initiated',
                    'confirmation_message': message,
                    'audio_url': tts_result.get('audio_url')
                }
            else:
                return call_result
                
        except Exception as e:
            logger.error(f"Error making appointment confirmation call: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to make appointment confirmation call'
            }
    
    def _is_business_hours(self) -> bool:
        """Check if current time is within business hours."""
        try:
            now = datetime.now()
            current_day = now.strftime('%A').lower()
            current_time = now.strftime('%H:%M')
            
            rules = self.routing_rules['business_hours']
            
            if current_day not in rules['days']:
                return False
            
            if rules['start'] <= current_time <= rules['end']:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking business hours: {e}")
            return False  # Default to closed if error
    
    def _generate_greeting(self, is_business_hours: bool) -> str:
        """Generate appropriate greeting based on time and business hours."""
        practice_name = "Lehigh Valley Wellness"
        
        if is_business_hours:
            return f"""Thank you for calling {practice_name}. I'm your AI assistant, and I'm here to help you with appointments, service information, and general questions.
            
How can I assist you today?"""
        else:
            return f"""Thank you for calling {practice_name}. Our office is currently closed. Our business hours are Monday through Friday, 8 AM to 6 PM.
            
I'm your AI assistant, and I can still help you with scheduling appointments, service information, and general questions. For emergencies, please hang up and dial 911.
            
How can I help you today?"""
    
    def detect_emergency_in_speech(self, transcript: str) -> Tuple[bool, str]:
        """
        Detect if the caller is describing an emergency situation.
        """
        transcript_lower = transcript.lower()
        
        for keyword in self.routing_rules['emergency_keywords']:
            if keyword in transcript_lower:
                return True, f"Emergency keyword detected: {keyword}"
        
        # Additional emergency detection logic could be added here
        # such as sentiment analysis or more sophisticated NLP
        
        return False, ""
    
    def get_call_analytics(self, date_range: Dict = None) -> Dict:
        """
        Get analytics data for phone calls.
        """
        try:
            # In production, this would query actual call data
            analytics = {
                'total_calls': 45,
                'answered_calls': 42,
                'missed_calls': 3,
                'average_call_duration': 4.2,  # minutes
                'ai_handled_calls': 38,
                'transferred_calls': 4,
                'emergency_calls': 1,
                'appointment_calls': 28,
                'information_calls': 14,
                'call_satisfaction': 4.6,  # out of 5
                'peak_hours': ['10:00-11:00', '14:00-15:00', '16:00-17:00']
            }
            
            return {
                'success': True,
                'analytics': analytics,
                'date_range': date_range or {'start': 'today', 'end': 'today'}
            }
            
        except Exception as e:
            logger.error(f"Error getting call analytics: {e}")
            return {
                'success': False,
                'error': str(e)
            }

