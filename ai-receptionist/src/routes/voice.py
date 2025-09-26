from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import json
import logging

from src.services.ai_service import AIReceptionistService
from src.services.phone_service import PhoneService
from src.services.crm_integration import CRMIntegrationService
from src.models.call import Call, ConversationTurn, CallAnalytics, db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

voice_bp = Blueprint('voice', __name__)

# Initialize services
ai_service = AIReceptionistService()
phone_service = PhoneService()
crm_service = CRMIntegrationService()

@voice_bp.route('/incoming-call', methods=['POST'])
def handle_incoming_call():
    """
    Handle incoming phone calls and initiate AI conversation.
    This endpoint would be called by the telephony provider (e.g., Twilio).
    """
    try:
        call_data = request.get_json() or {}
        caller_number = call_data.get('From', request.form.get('From', 'Unknown'))
        call_sid = call_data.get('CallSid', request.form.get('CallSid', f'call_{datetime.now().strftime("%Y%m%d_%H%M%S")}'))
        
        logger.info(f"Incoming call from {caller_number}, CallSid: {call_sid}")
        
        # Handle the incoming call
        call_response = phone_service.handle_incoming_call({
            'from': caller_number,
            'call_id': call_sid
        })
        
        # Create call record in database
        call_record = Call(
            phone_number=caller_number,
            call_type='inbound',
            call_status='answered',
            call_start_time=datetime.utcnow(),
            conversation_summary='Call initiated',
            intent_detected='initial_greeting'
        )
        db.session.add(call_record)
        db.session.commit()
        
        # Look up patient by phone number
        patient_data = crm_service.find_patient_by_phone(caller_number)
        if patient_data:
            call_record.patient_id = patient_data['id']
            call_record.caller_name = f"{patient_data['first_name']} {patient_data['last_name']}"
            db.session.commit()
        
        # Generate greeting message
        greeting = call_response.get('greeting_message', 'Thank you for calling Lehigh Valley Wellness.')
        
        # Convert greeting to speech
        tts_result = phone_service.convert_text_to_speech(greeting, call_sid)
        
        # Log first conversation turn
        greeting_turn = ConversationTurn(
            call_id=call_record.id,
            turn_number=1,
            speaker='ai',
            message=greeting,
            intent='greeting',
            confidence_score=1.0
        )
        db.session.add(greeting_turn)
        db.session.commit()
        
        # Return TwiML response for Twilio (or similar for other providers)
        response_data = {
            'call_id': call_sid,
            'status': 'answered',
            'greeting': greeting,
            'audio_url': tts_result.get('audio_url'),
            'next_action': 'listen_for_speech'
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error handling incoming call: {e}")
        return jsonify({
            'error': str(e),
            'status': 'error',
            'message': 'Failed to handle incoming call'
        }), 500

@voice_bp.route('/process-speech', methods=['POST'])
def process_speech():
    """
    Process speech input from caller and generate AI response.
    """
    try:
        data = request.get_json() or {}
        call_id = data.get('call_id')
        speech_text = data.get('speech_text', '')
        audio_data = data.get('audio_data')  # Base64 encoded audio
        
        if not call_id:
            return jsonify({'error': 'Missing call_id'}), 400
        
        logger.info(f"Processing speech for call {call_id}: {speech_text[:50]}...")
        
        # Get call record
        call_record = Call.query.filter_by(id=call_id).first()
        if not call_record:
            return jsonify({'error': 'Call not found'}), 404
        
        # If audio_data provided, convert speech to text
        if audio_data and not speech_text:
            stt_result = phone_service.convert_speech_to_text(audio_data, call_id)
            if stt_result['success']:
                speech_text = stt_result['transcript']
            else:
                return jsonify({
                    'error': 'Speech recognition failed',
                    'details': stt_result.get('error')
                }), 500
        
        if not speech_text:
            return jsonify({'error': 'No speech text provided'}), 400
        
        # Check for emergency
        is_emergency, emergency_reason = phone_service.detect_emergency_in_speech(speech_text)
        if is_emergency:
            logger.warning(f"Emergency detected in call {call_id}: {emergency_reason}")
            
            # Transfer to emergency services
            transfer_result = phone_service.transfer_call(call_id, 'emergency', emergency_reason)
            
            # Update call record
            call_record.intent_detected = 'emergency'
            call_record.human_transfer_required = True
            call_record.transfer_reason = emergency_reason
            db.session.commit()
            
            return jsonify({
                'call_id': call_id,
                'action': 'transfer',
                'transfer_type': 'emergency',
                'reason': emergency_reason,
                'message': 'Transferring to emergency services'
            }), 200
        
        # Detect intent and extract entities
        intent, confidence = ai_service.detect_intent(speech_text)
        entities = ai_service.extract_entities(speech_text, intent)
        
        # Get conversation history
        conversation_history = ConversationTurn.query.filter_by(call_id=call_record.id).order_by(ConversationTurn.turn_number).all()
        history_list = [turn.to_dict() for turn in conversation_history]
        
        # Generate AI response
        ai_response = ai_service.generate_response(speech_text, intent, entities, history_list)
        
        # Check if human transfer is needed
        should_transfer, transfer_reason = ai_service.should_transfer_to_human(
            intent, confidence, len(conversation_history)
        )
        
        # Log patient's speech turn
        patient_turn = ConversationTurn(
            call_id=call_record.id,
            turn_number=len(conversation_history) + 1,
            speaker='patient',
            message=speech_text,
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
        call_record.ai_confidence_score = confidence
        call_record.set_entities(entities)
        
        if should_transfer:
            call_record.human_transfer_required = True
            call_record.transfer_reason = transfer_reason
        
        db.session.commit()
        
        # Handle specific intents
        response_data = {
            'call_id': call_id,
            'intent': intent,
            'confidence': confidence,
            'entities': entities,
            'ai_response': ai_response,
            'should_transfer': should_transfer,
            'transfer_reason': transfer_reason
        }
        
        # Process appointment scheduling
        if intent == 'appointment_scheduling' and entities:
            appointment_result = handle_appointment_scheduling(call_record, entities, speech_text)
            response_data['appointment_result'] = appointment_result
        
        # Convert AI response to speech
        tts_result = phone_service.convert_text_to_speech(ai_response, call_id)
        response_data['audio_url'] = tts_result.get('audio_url')
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error processing speech: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Failed to process speech'
        }), 500

@voice_bp.route('/end-call', methods=['POST'])
def end_call():
    """
    End a phone call and generate summary.
    """
    try:
        data = request.get_json() or {}
        call_id = data.get('call_id')
        end_reason = data.get('reason', 'completed')
        
        if not call_id:
            return jsonify({'error': 'Missing call_id'}), 400
        
        logger.info(f"Ending call {call_id}: {end_reason}")
        
        # Get call record
        call_record = Call.query.filter_by(id=call_id).first()
        if not call_record:
            return jsonify({'error': 'Call not found'}), 404
        
        # Get conversation history
        conversation_turns = ConversationTurn.query.filter_by(call_id=call_record.id).order_by(ConversationTurn.turn_number).all()
        
        # Generate conversation summary
        conversation_summary = ai_service.generate_conversation_summary([turn.to_dict() for turn in conversation_turns])
        
        # Calculate call duration
        if call_record.call_start_time:
            call_duration = (datetime.utcnow() - call_record.call_start_time).total_seconds()
        else:
            call_duration = 0
        
        # Update call record
        call_record.call_end_time = datetime.utcnow()
        call_record.call_duration = int(call_duration)
        call_record.call_status = 'completed'
        call_record.conversation_summary = conversation_summary
        
        db.session.commit()
        
        # Log interaction to CRM
        crm_log_data = {
            'call_id': call_id,
            'patient_id': call_record.patient_id,
            'phone_number': call_record.phone_number,
            'conversation_summary': conversation_summary,
            'intent_detected': call_record.intent_detected,
            'outcome': end_reason,
            'appointment_created': call_record.appointment_created,
            'follow_up_required': call_record.follow_up_required
        }
        
        crm_result = crm_service.log_call_interaction(crm_log_data)
        
        # End call with phone service
        phone_result = phone_service.end_call(call_id, end_reason)
        
        return jsonify({
            'call_id': call_id,
            'status': 'ended',
            'duration': call_duration,
            'summary': conversation_summary,
            'crm_logged': crm_result['success'],
            'phone_ended': phone_result['success']
        }), 200
        
    except Exception as e:
        logger.error(f"Error ending call: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Failed to end call'
        }), 500

@voice_bp.route('/transfer-call', methods=['POST'])
def transfer_call():
    """
    Transfer a call to human staff or emergency services.
    """
    try:
        data = request.get_json() or {}
        call_id = data.get('call_id')
        transfer_type = data.get('transfer_type', 'reception')
        reason = data.get('reason', 'Patient request')
        
        if not call_id:
            return jsonify({'error': 'Missing call_id'}), 400
        
        logger.info(f"Transferring call {call_id} to {transfer_type}: {reason}")
        
        # Get call record
        call_record = Call.query.filter_by(id=call_id).first()
        if not call_record:
            return jsonify({'error': 'Call not found'}), 404
        
        # Transfer call
        transfer_result = phone_service.transfer_call(call_id, transfer_type, reason)
        
        # Update call record
        call_record.human_transfer_required = True
        call_record.transfer_reason = reason
        call_record.call_status = 'transferred'
        
        db.session.commit()
        
        return jsonify({
            'call_id': call_id,
            'transfer_result': transfer_result,
            'status': 'transferred'
        }), 200
        
    except Exception as e:
        logger.error(f"Error transferring call: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Failed to transfer call'
        }), 500

@voice_bp.route('/outbound-call', methods=['POST'])
def make_outbound_call():
    """
    Initiate an outbound call (e.g., appointment confirmation).
    """
    try:
        data = request.get_json() or {}
        phone_number = data.get('phone_number')
        call_type = data.get('call_type', 'appointment_confirmation')
        message = data.get('message', '')
        appointment_data = data.get('appointment_data', {})
        
        if not phone_number:
            return jsonify({'error': 'Missing phone_number'}), 400
        
        logger.info(f"Making outbound call to {phone_number}: {call_type}")
        
        # Initiate call
        if call_type == 'appointment_confirmation':
            call_result = phone_service.make_appointment_confirmation_call(phone_number, appointment_data)
        else:
            call_result = phone_service.initiate_call(phone_number, call_type)
        
        if call_result['success']:
            # Create call record
            call_record = Call(
                phone_number=phone_number,
                call_type='outbound',
                call_status='initiated',
                call_start_time=datetime.utcnow(),
                conversation_summary=f'Outbound {call_type} call',
                intent_detected=call_type
            )
            db.session.add(call_record)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'call_id': call_result['call_id'],
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
        
        # Check availability if date/time provided
        availability_result = None
        if preferred_date:
            availability_result = crm_service.check_appointment_availability(
                preferred_date, preferred_time, service_type
            )
        
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
            'availability': availability_result,
            'message': 'Appointment request processed'
        }
        
    except Exception as e:
        logger.error(f"Error handling appointment scheduling: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to process appointment request'
        }

@voice_bp.route('/call-analytics', methods=['GET'])
def get_call_analytics():
    """
    Get call analytics and performance metrics.
    """
    try:
        # Get analytics from phone service
        analytics = phone_service.get_call_analytics()
        
        # Get database analytics
        total_calls = Call.query.count()
        answered_calls = Call.query.filter_by(call_status='completed').count()
        transferred_calls = Call.query.filter_by(human_transfer_required=True).count()
        
        db_analytics = {
            'total_calls_db': total_calls,
            'answered_calls_db': answered_calls,
            'transferred_calls_db': transferred_calls,
            'ai_success_rate': (answered_calls - transferred_calls) / max(answered_calls, 1) * 100
        }
        
        return jsonify({
            'success': True,
            'phone_analytics': analytics,
            'database_analytics': db_analytics
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting call analytics: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Failed to get call analytics'
        }), 500

@voice_bp.route('/test-services', methods=['GET'])
def test_services():
    """
    Test all AI receptionist services.
    """
    try:
        # Test CRM connection
        crm_test = crm_service.test_crm_connection()
        
        # Test AI service
        ai_test_intent, ai_test_confidence = ai_service.detect_intent("I need to schedule an appointment")
        
        # Test phone service analytics
        phone_test = phone_service.get_call_analytics()
        
        return jsonify({
            'success': True,
            'crm_service': crm_test,
            'ai_service': {
                'status': 'working',
                'test_intent': ai_test_intent,
                'test_confidence': ai_test_confidence
            },
            'phone_service': {
                'status': 'working',
                'analytics_available': phone_test['success']
            },
            'message': 'All services tested successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error testing services: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Service testing failed'
        }), 500

