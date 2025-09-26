"""
Twilio Integration Service for Lehigh Valley Wellness AI Receptionist
Handles voice calls, SMS, and telephony integration with Twilio's API
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from flask import request, current_app
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather, Say, Record
from twilio.base.exceptions import TwilioException
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TwilioIntegrationService:
    """
    Service for integrating with Twilio's Voice API for phone calls.
    Handles incoming/outgoing calls, voice recognition, and call routing.
    """
    
    def __init__(self):
        # Twilio credentials (would be set via environment variables in production)
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID', 'your_account_sid_here')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN', 'your_auth_token_here')
        self.phone_number = os.getenv('TWILIO_PHONE_NUMBER', '+14843571916')  # Practice number
        
        # Initialize Twilio client
        try:
            self.client = Client(self.account_sid, self.auth_token)
            logger.info("Twilio client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {e}")
            self.client = None
        
        # Voice settings
        self.voice_settings = {
            'voice': 'alice',  # Twilio voice options: alice, man, woman
            'language': 'en-US',
            'speech_timeout': 'auto',
            'enhanced': True
        }
        
        # Practice information
        self.practice_info = {
            'name': 'Lehigh Valley Wellness',
            'phone': '484-357-1916',
            'hours': 'Monday through Friday, 8 AM to 6 PM',
            'emergency_message': 'If this is a medical emergency, please hang up and dial 911 immediately.'
        }
    
    def create_incoming_call_response(self, caller_id: str = None) -> str:
        """
        Create TwiML response for incoming calls with AI greeting.
        """
        try:
            response = VoiceResponse()
            
            # Emergency check first
            response.say(
                self.practice_info['emergency_message'],
                voice=self.voice_settings['voice'],
                language=self.voice_settings['language']
            )
            
            # Pause for emergency consideration
            response.pause(length=2)
            
            # Main greeting
            greeting_text = (
                f"Hello and thank you for calling {self.practice_info['name']}. "
                f"I'm your AI assistant and I'm here to help you with appointment scheduling, "
                f"service information, and general inquiries. "
                f"Please tell me how I can assist you today."
            )
            
            # Use Gather to collect speech input
            gather = Gather(
                input='speech',
                timeout=10,
                speech_timeout='auto',
                action='/api/voice/process-speech',
                method='POST',
                enhanced=True,
                language=self.voice_settings['language']
            )
            
            gather.say(
                greeting_text,
                voice=self.voice_settings['voice'],
                language=self.voice_settings['language']
            )
            
            response.append(gather)
            
            # Fallback if no input received
            response.say(
                "I didn't hear anything. Please call back if you need assistance. Goodbye.",
                voice=self.voice_settings['voice'],
                language=self.voice_settings['language']
            )
            response.hangup()
            
            return str(response)
            
        except Exception as e:
            logger.error(f"Error creating incoming call response: {e}")
            # Fallback response
            response = VoiceResponse()
            response.say(
                f"Thank you for calling {self.practice_info['name']}. "
                f"Please call us back at {self.practice_info['phone']}. Goodbye.",
                voice='alice'
            )
            response.hangup()
            return str(response)
    
    def create_ai_response(self, ai_message: str, should_continue: bool = True) -> str:
        """
        Create TwiML response with AI-generated message and continue conversation.
        """
        try:
            response = VoiceResponse()
            
            if should_continue:
                # Continue conversation with speech input
                gather = Gather(
                    input='speech',
                    timeout=10,
                    speech_timeout='auto',
                    action='/api/voice/process-speech',
                    method='POST',
                    enhanced=True,
                    language=self.voice_settings['language']
                )
                
                gather.say(
                    ai_message,
                    voice=self.voice_settings['voice'],
                    language=self.voice_settings['language']
                )
                
                response.append(gather)
                
                # Fallback if no response
                response.say(
                    "I didn't hear a response. Is there anything else I can help you with?",
                    voice=self.voice_settings['voice'],
                    language=self.voice_settings['language']
                )
                
                # Final gather attempt
                final_gather = Gather(
                    input='speech',
                    timeout=5,
                    speech_timeout='auto',
                    action='/api/voice/process-speech',
                    method='POST'
                )
                final_gather.say("Please let me know if you need anything else.")
                response.append(final_gather)
                
                # End call if still no response
                response.say("Thank you for calling. Goodbye.")
                response.hangup()
            else:
                # End conversation
                response.say(
                    ai_message,
                    voice=self.voice_settings['voice'],
                    language=self.voice_settings['language']
                )
                response.hangup()
            
            return str(response)
            
        except Exception as e:
            logger.error(f"Error creating AI response: {e}")
            response = VoiceResponse()
            response.say("I apologize, but I'm having technical difficulties. Please call back later.")
            response.hangup()
            return str(response)
    
    def create_transfer_response(self, transfer_type: str = 'reception') -> str:
        """
        Create TwiML response for transferring calls to human staff.
        """
        try:
            response = VoiceResponse()
            
            if transfer_type == 'emergency':
                response.say(
                    "I'm transferring you to emergency services immediately.",
                    voice=self.voice_settings['voice']
                )
                # In production, this would dial 911 or emergency line
                response.dial('911')
            else:
                response.say(
                    "Let me transfer you to our reception staff who can better assist you. Please hold.",
                    voice=self.voice_settings['voice']
                )
                # Transfer to practice number (would be internal extension in production)
                response.dial(self.practice_info['phone'])
            
            return str(response)
            
        except Exception as e:
            logger.error(f"Error creating transfer response: {e}")
            response = VoiceResponse()
            response.say("I'm unable to transfer your call right now. Please call back.")
            response.hangup()
            return str(response)
    
    def make_outbound_call(self, to_number: str, message: str, callback_url: str = None) -> Dict:
        """
        Make an outbound call with a custom message.
        """
        try:
            if not self.client:
                return {'success': False, 'error': 'Twilio client not initialized'}
            
            # Create TwiML for outbound call
            twiml_url = self._create_outbound_twiml_url(message)
            
            call = self.client.calls.create(
                to=to_number,
                from_=self.phone_number,
                url=twiml_url,
                status_callback=callback_url,
                status_callback_event=['initiated', 'ringing', 'answered', 'completed']
            )
            
            logger.info(f"Outbound call initiated: {call.sid} to {to_number}")
            
            return {
                'success': True,
                'call_sid': call.sid,
                'status': call.status,
                'to': to_number,
                'from': self.phone_number
            }
            
        except TwilioException as e:
            logger.error(f"Twilio error making outbound call: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Error making outbound call: {e}")
            return {'success': False, 'error': str(e)}
    
    def make_appointment_confirmation_call(self, patient_phone: str, appointment_data: Dict) -> Dict:
        """
        Make an outbound call to confirm an appointment.
        """
        try:
            appointment_date = appointment_data.get('date', 'your scheduled date')
            appointment_time = appointment_data.get('time', 'your scheduled time')
            service_type = appointment_data.get('service', 'wellness consultation')
            patient_name = appointment_data.get('patient_name', '')
            
            message = (
                f"Hello{' ' + patient_name if patient_name else ''}. "
                f"This is {self.practice_info['name']} calling to confirm your "
                f"{service_type} appointment on {appointment_date} at {appointment_time}. "
                f"Please press 1 to confirm, or press 2 if you need to reschedule. "
                f"You can also call us back at {self.practice_info['phone']}."
            )
            
            return self.make_outbound_call(patient_phone, message)
            
        except Exception as e:
            logger.error(f"Error making appointment confirmation call: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_outbound_twiml_url(self, message: str) -> str:
        """
        Create a TwiML URL for outbound calls (in production, this would be a proper endpoint).
        """
        # In production, this would create a proper TwiML endpoint
        # For now, return a placeholder URL that would serve the TwiML
        base_url = os.getenv('BASE_URL', 'https://your-domain.com')
        return f"{base_url}/api/voice/outbound-twiml?message={message}"
    
    def get_call_details(self, call_sid: str) -> Dict:
        """
        Get details about a specific call.
        """
        try:
            if not self.client:
                return {'success': False, 'error': 'Twilio client not initialized'}
            
            call = self.client.calls(call_sid).fetch()
            
            return {
                'success': True,
                'call_sid': call.sid,
                'status': call.status,
                'direction': call.direction,
                'from': call.from_,
                'to': call.to,
                'start_time': call.start_time,
                'end_time': call.end_time,
                'duration': call.duration,
                'price': call.price
            }
            
        except TwilioException as e:
            logger.error(f"Twilio error getting call details: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Error getting call details: {e}")
            return {'success': False, 'error': str(e)}
    
    def end_call(self, call_sid: str) -> Dict:
        """
        End an active call.
        """
        try:
            if not self.client:
                return {'success': False, 'error': 'Twilio client not initialized'}
            
            call = self.client.calls(call_sid).update(status='completed')
            
            logger.info(f"Call ended: {call_sid}")
            
            return {
                'success': True,
                'call_sid': call_sid,
                'status': call.status
            }
            
        except TwilioException as e:
            logger.error(f"Twilio error ending call: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Error ending call: {e}")
            return {'success': False, 'error': str(e)}
    
    def send_sms(self, to_number: str, message: str) -> Dict:
        """
        Send an SMS message (for appointment confirmations, etc.).
        """
        try:
            if not self.client:
                return {'success': False, 'error': 'Twilio client not initialized'}
            
            message = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=to_number
            )
            
            logger.info(f"SMS sent: {message.sid} to {to_number}")
            
            return {
                'success': True,
                'message_sid': message.sid,
                'status': message.status,
                'to': to_number
            }
            
        except TwilioException as e:
            logger.error(f"Twilio error sending SMS: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return {'success': False, 'error': str(e)}
    
    def validate_webhook(self, request_data: Dict) -> bool:
        """
        Validate that the webhook request is from Twilio.
        """
        try:
            # In production, implement proper webhook validation
            # using Twilio's request validation
            return True
            
        except Exception as e:
            logger.error(f"Error validating webhook: {e}")
            return False

# Configuration helper
def setup_twilio_environment():
    """
    Setup instructions for Twilio integration.
    """
    setup_instructions = {
        'environment_variables': {
            'TWILIO_ACCOUNT_SID': 'Your Twilio Account SID',
            'TWILIO_AUTH_TOKEN': 'Your Twilio Auth Token',
            'TWILIO_PHONE_NUMBER': '+14843571916',  # Practice phone number
            'BASE_URL': 'https://your-domain.com'  # Your application's public URL
        },
        'webhook_urls': {
            'incoming_calls': '/api/voice/incoming-call',
            'speech_processing': '/api/voice/process-speech',
            'call_status': '/api/voice/call-status',
            'outbound_twiml': '/api/voice/outbound-twiml'
        },
        'required_packages': [
            'twilio>=8.0.0',
            'flask>=2.0.0',
            'flask-cors>=4.0.0'
        ],
        'setup_steps': [
            '1. Create Twilio account and get credentials',
            '2. Purchase phone number (484-357-1916)',
            '3. Set environment variables',
            '4. Configure webhook URLs in Twilio Console',
            '5. Deploy application with public URL',
            '6. Test incoming and outgoing calls'
        ]
    }
    
    return setup_instructions
