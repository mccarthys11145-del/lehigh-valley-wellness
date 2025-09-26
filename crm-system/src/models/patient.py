from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    insurance_provider = db.Column(db.String(255))
    preferred_contact_method = db.Column(db.String(20), default='email')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='active')
    
    # Relationships
    consultation_requests = db.relationship('ConsultationRequest', backref='patient', lazy=True)
    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    communications = db.relationship('Communication', backref='patient', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'insurance_provider': self.insurance_provider,
            'preferred_contact_method': self.preferred_contact_method,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'status': self.status
        }
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class ConsultationRequest(db.Model):
    __tablename__ = 'consultation_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    service_type = db.Column(db.String(100), nullable=False)
    preferred_date = db.Column(db.Date)
    preferred_time = db.Column(db.Time)
    reason_for_visit = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    priority = db.Column(db.String(20), default='normal')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime)
    confirmed_date = db.Column(db.Date)
    confirmed_time = db.Column(db.Time)
    
    # Relationships
    appointment = db.relationship('Appointment', backref='consultation_request', uselist=False, lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.get_full_name() if self.patient else None,
            'service_type': self.service_type,
            'preferred_date': self.preferred_date.isoformat() if self.preferred_date else None,
            'preferred_time': self.preferred_time.isoformat() if self.preferred_time else None,
            'reason_for_visit': self.reason_for_visit,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'confirmed_at': self.confirmed_at.isoformat() if self.confirmed_at else None,
            'confirmed_date': self.confirmed_date.isoformat() if self.confirmed_date else None,
            'confirmed_time': self.confirmed_time.isoformat() if self.confirmed_time else None
        }


class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    consultation_request_id = db.Column(db.Integer, db.ForeignKey('consultation_requests.id'))
    service_type = db.Column(db.String(100), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    status = db.Column(db.String(20), default='scheduled')
    provider = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.get_full_name() if self.patient else None,
            'consultation_request_id': self.consultation_request_id,
            'service_type': self.service_type,
            'appointment_date': self.appointment_date.isoformat(),
            'appointment_time': self.appointment_time.isoformat(),
            'duration_minutes': self.duration_minutes,
            'status': self.status,
            'provider': self.provider,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }


class Communication(db.Model):
    __tablename__ = 'communications'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    communication_type = db.Column(db.String(50), nullable=False)  # email, sms, call
    subject = db.Column(db.String(255))
    message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='sent')
    template_used = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.get_full_name() if self.patient else None,
            'communication_type': self.communication_type,
            'subject': self.subject,
            'message': self.message,
            'sent_at': self.sent_at.isoformat(),
            'status': self.status,
            'template_used': self.template_used
        }


class EmailTemplate(db.Model):
    __tablename__ = 'email_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    html_content = db.Column(db.Text, nullable=False)
    text_content = db.Column(db.Text)
    trigger_event = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'subject': self.subject,
            'html_content': self.html_content,
            'text_content': self.text_content,
            'trigger_event': self.trigger_event,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

