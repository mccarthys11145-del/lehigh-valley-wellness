from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Call(db.Model):
    __tablename__ = 'calls'
    
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)
    caller_name = db.Column(db.String(100))
    call_type = db.Column(db.String(20), nullable=False)  # inbound, outbound
    call_status = db.Column(db.String(20), nullable=False)  # answered, missed, completed, failed
    call_duration = db.Column(db.Integer, default=0)  # in seconds
    call_start_time = db.Column(db.DateTime, default=datetime.utcnow)
    call_end_time = db.Column(db.DateTime)
    
    # AI Conversation Data
    conversation_transcript = db.Column(db.Text)
    conversation_summary = db.Column(db.Text)
    intent_detected = db.Column(db.String(100))
    entities_extracted = db.Column(db.Text)  # JSON string
    
    # CRM Integration
    patient_id = db.Column(db.String(50))
    appointment_created = db.Column(db.Boolean, default=False)
    appointment_id = db.Column(db.String(50))
    follow_up_required = db.Column(db.Boolean, default=False)
    
    # Call Recording and Audio
    recording_url = db.Column(db.String(500))
    audio_quality_score = db.Column(db.Float)
    
    # System Metadata
    ai_confidence_score = db.Column(db.Float)
    human_transfer_required = db.Column(db.Boolean, default=False)
    transfer_reason = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'phone_number': self.phone_number,
            'caller_name': self.caller_name,
            'call_type': self.call_type,
            'call_status': self.call_status,
            'call_duration': self.call_duration,
            'call_start_time': self.call_start_time.isoformat() if self.call_start_time else None,
            'call_end_time': self.call_end_time.isoformat() if self.call_end_time else None,
            'conversation_summary': self.conversation_summary,
            'intent_detected': self.intent_detected,
            'patient_id': self.patient_id,
            'appointment_created': self.appointment_created,
            'appointment_id': self.appointment_id,
            'follow_up_required': self.follow_up_required,
            'ai_confidence_score': self.ai_confidence_score,
            'human_transfer_required': self.human_transfer_required,
            'transfer_reason': self.transfer_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def set_entities(self, entities_dict):
        """Store extracted entities as JSON string"""
        self.entities_extracted = json.dumps(entities_dict)
    
    def get_entities(self):
        """Retrieve extracted entities as dictionary"""
        if self.entities_extracted:
            return json.loads(self.entities_extracted)
        return {}

class ConversationTurn(db.Model):
    __tablename__ = 'conversation_turns'
    
    id = db.Column(db.Integer, primary_key=True)
    call_id = db.Column(db.Integer, db.ForeignKey('calls.id'), nullable=False)
    turn_number = db.Column(db.Integer, nullable=False)
    speaker = db.Column(db.String(10), nullable=False)  # 'patient' or 'ai'
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # AI Processing Data
    intent = db.Column(db.String(100))
    entities = db.Column(db.Text)  # JSON string
    confidence_score = db.Column(db.Float)
    processing_time = db.Column(db.Float)  # in milliseconds
    
    call = db.relationship('Call', backref=db.backref('conversation_turns', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'call_id': self.call_id,
            'turn_number': self.turn_number,
            'speaker': self.speaker,
            'message': self.message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'intent': self.intent,
            'entities': json.loads(self.entities) if self.entities else {},
            'confidence_score': self.confidence_score,
            'processing_time': self.processing_time
        }

class CallAnalytics(db.Model):
    __tablename__ = 'call_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    
    # Call Volume Metrics
    total_calls = db.Column(db.Integer, default=0)
    inbound_calls = db.Column(db.Integer, default=0)
    outbound_calls = db.Column(db.Integer, default=0)
    answered_calls = db.Column(db.Integer, default=0)
    missed_calls = db.Column(db.Integer, default=0)
    
    # AI Performance Metrics
    ai_handled_calls = db.Column(db.Integer, default=0)
    human_transfer_calls = db.Column(db.Integer, default=0)
    average_ai_confidence = db.Column(db.Float, default=0.0)
    average_call_duration = db.Column(db.Float, default=0.0)
    
    # Appointment Metrics
    appointments_scheduled = db.Column(db.Integer, default=0)
    appointment_success_rate = db.Column(db.Float, default=0.0)
    
    # Intent Distribution
    scheduling_intents = db.Column(db.Integer, default=0)
    information_intents = db.Column(db.Integer, default=0)
    billing_intents = db.Column(db.Integer, default=0)
    emergency_intents = db.Column(db.Integer, default=0)
    other_intents = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'total_calls': self.total_calls,
            'inbound_calls': self.inbound_calls,
            'outbound_calls': self.outbound_calls,
            'answered_calls': self.answered_calls,
            'missed_calls': self.missed_calls,
            'ai_handled_calls': self.ai_handled_calls,
            'human_transfer_calls': self.human_transfer_calls,
            'average_ai_confidence': self.average_ai_confidence,
            'average_call_duration': self.average_call_duration,
            'appointments_scheduled': self.appointments_scheduled,
            'appointment_success_rate': self.appointment_success_rate,
            'scheduling_intents': self.scheduling_intents,
            'information_intents': self.information_intents,
            'billing_intents': self.billing_intents,
            'emergency_intents': self.emergency_intents,
            'other_intents': self.other_intents
        }

