"""
Twilio Voice Routes for Lehigh Valley Wellness AI Receptionist
Handles Twilio webhook endpoints for voice calls
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import json
import logging

from src.services.ai_service import AIReceptionistService
from src.services.twilio_integration import TwilioIntegrationService
from src.services.crm_integration import CRMIntegrationService
from src.models.call import Call, ConversationTurn, CallAnalytics, db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

twilio_voice_bp = Blueprint('twilio_voice', __name__)

# Initialize services
ai_service = AIReceptionistService()
twilio_service = TwilioIntegrationService()
crm_service = CRMIntegrationService()

@twilio_voice_bp.route('/incoming-call', methods=['POST'])
def handle_twilio_incoming_call():
    """
    Handle incoming calls from Twilio webhook.
    This is the main entry point for all incoming calls.
    """
    try:
        # Get Twilio request data
        caller_number = request.form.get('From', 'Unknown')
        call_sid = request.form.get('CallSid', f'call_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        call_status = request.form.get('CallStatus', 'initiated')
        
        logger.info(f"Twilio incoming call: {call_sid} from {caller_number}")
        
        # Validate webhook (in production)
        if not twilio_service.validate_webhook(request.form.to_dict()):
            logger.warning(f"Invalid webhook request for call {call_sid}")
            return "Unauthorized", 401
        
        # Create call record in database
        call_record = Call(
            phone_number=caller_number,
            call_type='inbound',
            call_status='answered',
            call_start_time=datetime.utcnow(),
            conversation_summary='Incoming call initiated',
            intent_detected='initial_greeting',
            external_call_id=call_sid
        )
        db.session.add(call_record)
        db.session.commit()
        
        # Look up patient by phone number
        patient_data = crm_service.find_patient_by_phone(caller_number)
        if patient_data:
            call_record.patient_id = patient_data['id']
            call_record.caller_name = f"{patient_data['first_name']} {patient_data['last_name']}"
            db.session.commit()
            logger.info(f"Found existing patient: {call_record.caller_name}")
        
        # Store call ID in session for subsequent requests
        # In production, you might use Redis or database for session management
        
        # Generate TwiML response for incoming call
        twiml_response = twilio_service.create_incoming_call_response(caller_number)
        
        # Log initial greeting turn
        greeting_turn = ConversationTurn(
            call_id=call_record.id,
            turn_number=1,
            speaker='ai',
            message='Initial greeting and emergency notice',
            intent='greeting',
            confidence_score=1.0
        )
        db.session.add(greeting_turn)
        db.session.commit()
        
        logger.info(f"Generated TwiML response for call {call_sid}")
        
        # Return TwiML response
        return twiml_response, 200, {'Content-Type': 'text/xml'}
        
    except Exception as e:
        logger.error(f"Error handling Twilio incoming call: {e}")
        # Return fallback TwiML
        fallback_response = twilio_service.create_ai_response(
            "I apologize, but I'm experiencing technical difficulties. Please call back in a few minutes.",
            should_continue=False
        )
        return fallback_response, 200, {'Content-Type': 'text/xml'}

@twilio_voice_bp.route('/process-speech', methods=['POST'])
def handle_twilio_speech():
    """
    Process speech input from Twilio and generate AI response.
    """
    try:
        # Get Twilio speech data
        call_sid = request.form.get('CallSid')
        speech_result = request.form.get('SpeechResult', '')
        confidence = float(request.form.get('Confidence', 0.0))
        
        logger.info(f"Processing speech for call {call_sid}: {speech_result[:50]}...")
        
        if not call_sid:
            logger.error("Missing CallSid in speech processing request")
            return "Bad Request", 400
        
        # Find call record by external call ID
        call_record = Call.query.filter_by(external_call_id=call_sid).first()
        if not call_record:
            logger.error(f"Call record not found for CallSid: {call_sid}")
            # Create a new call record if not found
            call_record = Call(
                phone_number=request.form.get('From', 'Unknown'),
                call_type='inbound',
                call_status='in_progress',
                call_start_time=datetime.utcnow(),
                external_call_id=call_sid
            )
            db.session.add(call_record)
            db.session.commit()
        
        # Check for emergency keywords
        emergency_keywords = ['emergency', 'urgent', 'chest pain', 'can\'t breathe', 'bleeding', 'help']
        is_emergency = any(keyword in speech_result.lower() for keyword in emergency_keywords)
        
        if is_emergency:
            logger.warning(f"Emergency detected in call {call_sid}: {speech_result}")
            
            # Update call record
            call_record.intent_detected = 'emergency'
            call_record.human_transfer_required = True
            call_record.transfer_reason = 'Emergency situation detected'
            db.session.commit()
            
            # Return emergency transfer TwiML
            emergency_response = twilio_service.create_transfer_response('emergency')
            return emergency_response, 200, {'Content-Type': 'text/xml'}
        
        # Process with AI service
        intent, ai_confidence = ai_service.detect_intent(speech_result)
        entities = ai_service.extract_entities(speech_result, intent)
        
        # Get conversation history
        conversation_history = ConversationTurn.query.filter_by(
            call_id=call_record.id
        ).order_by(ConversationTurn.turn_number).all()
        history_list = [turn.to_dict() for turn in conversation_history]
        
        # Generate AI response
        ai_response = ai_service.generate_response(speech_result, intent, entities, history_list)
        
        # Check if human transfer is needed
        should_transfer, transfer_reason = ai_service.should_transfer_to_human(
            intent, ai_confidence, len(conversation_history)
        )
        
        # Log patient's speech turn
        patient_turn = ConversationTurn(
            call_id=call_record.id,
            turn_number=len(conversation_history) + 1,
            speaker='patient',
            message=speech_result,
            intent=intent,
            entities=json.dumps(entities),
            confidence_score=confidence
        )
        db.session.add(patient_turn)
        
        # Log AI response turn
        ai_turn = ConversationTurn(
            call_id=call_record.id,
            turn_number=len(conversation_history) + 2,
            speaker='ai',
            message=ai_response,
            intent=f'response_to_{intent}',
            confidence_score=0.9
        )
        db.session.add(ai_turn)
        
        # Update call record
        call_record.intent_detected = intent
        call_record.ai_confidence_score = ai_confidence
        call_record.set_entities(entities)
        
        if should_transfer:
            call_record.human_transfer_required = True
            call_record.transfer_reason = transfer_reason
        
        db.session.commit()
        
        # Handle appointment scheduling
        if intent == 'appointment_scheduling' and entities:
            appointment_result = handle_appointment_scheduling(call_record, entities, speech_result)
            if appointment_result['success']:
                ai_response += f" I've created your consultation request and you'll receive a confirmation call within 24 hours."
        
        # Determine if conversation should continue
        should_continue = not should_transfer and intent not in ['goodbye', 'end_call']
        
        if should_transfer:
            # Transfer to human
            transfer_response = twilio_service.create_transfer_response('reception')
            return transfer_response, 200, {'Content-Type': 'text/xml'}
        else:
            # Continue AI conversation
            twiml_response = twilio_service.create_ai_response(ai_response, should_continue)
            return twiml_response, 200, {'Content-Type': 'text/xml'}
        
    except Exception as e:
        logger.error(f"Error processing Twilio speech: {e}")
        # Return fallback response
        fallback_response = twilio_service.create_ai_response(
            "I apologize, but I didn't understand that clearly. Could you please repeat your request?",
            should_continue=True
        )
        return fallback_response, 200, {'Content-Type': 'text/xml'}

@twilio_voice_bp.route('/call-status', methods=['POST'])
def handle_call_status():
    """
    Handle call status updates from Twilio.
    """
    try:
        call_sid = request.form.get('CallSid')
        call_status = request.form.get('CallStatus')
        call_duration = request.form.get('CallDuration', 0)
        
        logger.info(f"Call status update: {call_sid} - {call_status}")
        
        # Find call record
        call_record = Call.query.filter_by(external_call_id=call_sid).first()
        if call_record:
            call_record.call_status = call_status
            
            if call_status == 'completed':
                call_record.call_end_time = datetime.utcnow()
                call_record.call_duration = int(call_duration) if call_duration else 0
                
                # Generate conversation summary
                conversation_turns = ConversationTurn.query.filter_by(
                    call_id=call_record.id
                ).order_by(ConversationTurn.turn_number).all()
                
                if conversation_turns:
                    conversation_summary = ai_service.generate_conversation_summary(
                        [turn.to_dict() for turn in conversation_turns]
                    )
                    call_record.conversation_summary = conversation_summary
                
                # Log to CRM
                crm_log_data = {
                    'call_id': call_record.id,
                    'patient_id': call_record.patient_id,
                    'phone_number': call_record.phone_number,
                    'conversation_summary': call_record.conversation_summary,
                    'intent_detected': call_record.intent_detected,
                    'outcome': 'completed',
                    'appointment_created': call_record.appointment_created,
                    'follow_up_required': call_record.follow_up_required
                }
                
                crm_result = crm_service.log_call_interaction(crm_log_data)
                logger.info(f"Call logged to CRM: {crm_result['success']}")
            
            db.session.commit()
        
        return "OK", 200
        
    except Exception as e:
        logger.error(f"Error handling call status: {e}")
        return "Error", 500

@twilio_voice_bp.route('/outbound-twiml', methods=['GET', 'POST'])
def generate_outbound_twiml():
    """
    Generate TwiML for outbound calls.
    """
    try:
        message = request.args.get('message', 'Hello from Lehigh Valley Wellness.')
        
        # Create simple TwiML for outbound message
        twiml_response = twilio_service.create_ai_response(message, should_continue=False)
        
        return twiml_response, 200, {'Content-Type': 'text/xml'}
        
    except Exception as e:
        logger.error(f"Error generating outbound TwiML: {e}")
        return "Error generating TwiML", 500

@twilio_voice_bp.route('/make-outbound-call', methods=['POST'])
def make_outbound_call():
    """
    API endpoint to make outbound calls.
    """
    try:
        data = request.get_json() or {}
        phone_number = data.get('phone_number')
        message = data.get('message', 'Hello from Lehigh Valley Wellness.')
        call_type = data.get('call_type', 'general')
        
        if not phone_number:
            return jsonify({'error': 'Missing phone_number'}), 400
        
        logger.info(f"Making outbound call to {phone_number}")
        
        # Make the call using Twilio service
        call_result = twilio_service.make_outbound_call(phone_number, message)
        
        if call_result['success']:
            # Create call record
            call_record = Call(
                phone_number=phone_number,
                call_type='outbound',
                call_status='initiated',
                call_start_time=datetime.utcnow(),
                conversation_summary=f'Outbound {call_type} call',
                intent_detected=call_type,
                external_call_id=call_result['call_sid']
            )
            db.session.add(call_record)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'call_sid': call_result['call_sid'],
                'message': f'Outbound call initiated to {phone_number}'
            }), 200
        else:
            return jsonify(call_result), 500
        
    except Exception as e:
        logger.error(f"Error making outbound call: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Failed to make outbound call'
        }), 500

def handle_appointment_scheduling(call_record: Call, entities: dict, patient_message: str) -> dict:
    """
    Handle appointment scheduling logic during a call.
    """
    try:
        # Extract scheduling information
        service_type = entities.get('service_type', 'wellness_consultation')
        preferred_date = entities.get('preferred_date', '')
        preferred_time = entities.get('preferred_time', '')
        patient_name = entities.get('patient_name', call_record.caller_name or '')
        
        # Create consultation request
        request_data = {
            'first_name': patient_name.split()[0] if patient_name else '',
            'last_name': ' '.join(patient_name.split()[1:]) if len(patient_name.split()) > 1 else '',
            'phone': call_record.phone_number,
            'service_type': service_type,
            'preferred_date': preferred_date,
            'preferred_time': preferred_time,
            'reason_for_visit': patient_message,
            'source': 'ai_receptionist_call'
        }
        
        consultation_result = crm_service.create_consultation_request(request_data)
        
        if consultation_result['success']:
            call_record.appointment_created = True
            call_record.appointment_id = consultation_result['request_id']
            call_record.follow_up_required = True
            db.session.commit()
        
        return {
            'success': consultation_result['success'],
            'request_id': consultation_result.get('request_id'),
            'message': consultation_result.get('message', 'Consultation request processed')
        }
        
    except Exception as e:
        logger.error(f"Error handling appointment scheduling: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to process appointment request'
        }
