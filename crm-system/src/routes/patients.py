from flask import Blueprint, request, jsonify
from datetime import datetime, date, time
from src.models.user import db
from src.models.patient import Patient, ConsultationRequest, Appointment, Communication
from src.services.email_service import EmailService

patients_bp = Blueprint('patients', __name__)
email_service = EmailService()

@patients_bp.route('/patients', methods=['POST'])
def create_patient():
    """Create a new patient or return existing patient"""
    try:
        data = request.get_json()
        
        # Check if patient already exists by email
        existing_patient = Patient.query.filter_by(email=data.get('email')).first()
        if existing_patient:
            return jsonify({
                'success': True,
                'patient': existing_patient.to_dict(),
                'message': 'Patient already exists'
            }), 200
        
        # Create new patient
        patient = Patient(
            first_name=data.get('firstName'),
            last_name=data.get('lastName'),
            email=data.get('email'),
            phone=data.get('phone'),
            date_of_birth=datetime.strptime(data.get('dateOfBirth'), '%Y-%m-%d').date() if data.get('dateOfBirth') else None,
            insurance_provider=data.get('insurance'),
            preferred_contact_method=data.get('preferredContact', 'email')
        )
        
        db.session.add(patient)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'patient': patient.to_dict(),
            'message': 'Patient created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@patients_bp.route('/patients/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Get patient details with appointment history"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        
        # Get patient's consultation requests
        consultation_requests = ConsultationRequest.query.filter_by(patient_id=patient_id).order_by(ConsultationRequest.created_at.desc()).all()
        
        # Get patient's appointments
        appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.appointment_date.desc()).all()
        
        # Get patient's communications
        communications = Communication.query.filter_by(patient_id=patient_id).order_by(Communication.sent_at.desc()).limit(10).all()
        
        return jsonify({
            'success': True,
            'patient': patient.to_dict(),
            'consultation_requests': [req.to_dict() for req in consultation_requests],
            'appointments': [apt.to_dict() for apt in appointments],
            'recent_communications': [comm.to_dict() for comm in communications]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@patients_bp.route('/patients', methods=['GET'])
def list_patients():
    """List all patients with pagination and search"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        
        query = Patient.query
        
        if search:
            query = query.filter(
                db.or_(
                    Patient.first_name.ilike(f'%{search}%'),
                    Patient.last_name.ilike(f'%{search}%'),
                    Patient.email.ilike(f'%{search}%')
                )
            )
        
        patients = query.order_by(Patient.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'patients': [patient.to_dict() for patient in patients.items],
            'pagination': {
                'page': page,
                'pages': patients.pages,
                'per_page': per_page,
                'total': patients.total
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@patients_bp.route('/consultation-requests', methods=['POST'])
def create_consultation_request():
    """Create a new consultation request"""
    try:
        data = request.get_json()
        
        # Create or get patient
        patient_data = {
            'firstName': data.get('firstName'),
            'lastName': data.get('lastName'),
            'email': data.get('email'),
            'phone': data.get('phone'),
            'dateOfBirth': data.get('dateOfBirth'),
            'insurance': data.get('insurance'),
            'preferredContact': data.get('preferredContact')
        }
        
        # Check if patient exists
        patient = Patient.query.filter_by(email=data.get('email')).first()
        if not patient:
            patient = Patient(
                first_name=patient_data['firstName'],
                last_name=patient_data['lastName'],
                email=patient_data['email'],
                phone=patient_data.get('phone'),
                date_of_birth=datetime.strptime(patient_data['dateOfBirth'], '%Y-%m-%d').date() if patient_data.get('dateOfBirth') else None,
                insurance_provider=patient_data.get('insurance'),
                preferred_contact_method=patient_data.get('preferredContact', 'email')
            )
            db.session.add(patient)
            db.session.flush()  # Get patient ID
        
        # Create consultation request
        consultation_request = ConsultationRequest(
            patient_id=patient.id,
            service_type=data.get('serviceType'),
            preferred_date=datetime.strptime(data.get('preferredDate'), '%Y-%m-%d').date() if data.get('preferredDate') else None,
            preferred_time=datetime.strptime(data.get('preferredTime'), '%H:%M').time() if data.get('preferredTime') else None,
            reason_for_visit=data.get('reason'),
            priority=data.get('priority', 'normal')
        )
        
        db.session.add(consultation_request)
        db.session.commit()
        
        # Send confirmation email
        try:
            email_service.send_consultation_request_confirmation(patient, consultation_request)
        except Exception as email_error:
            print(f"Email sending failed: {email_error}")
            # Don't fail the request if email fails
        
        return jsonify({
            'success': True,
            'consultation_request': consultation_request.to_dict(),
            'patient': patient.to_dict(),
            'message': 'Consultation request submitted successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@patients_bp.route('/consultation-requests', methods=['GET'])
def list_consultation_requests():
    """List consultation requests with filtering"""
    try:
        status = request.args.get('status', 'pending')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = ConsultationRequest.query
        
        if status != 'all':
            query = query.filter_by(status=status)
        
        requests = query.order_by(ConsultationRequest.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'consultation_requests': [req.to_dict() for req in requests.items],
            'pagination': {
                'page': page,
                'pages': requests.pages,
                'per_page': per_page,
                'total': requests.total
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@patients_bp.route('/consultation-requests/<int:request_id>/confirm', methods=['PUT'])
def confirm_consultation_request(request_id):
    """Confirm a consultation request and convert to appointment"""
    try:
        data = request.get_json()
        consultation_request = ConsultationRequest.query.get_or_404(request_id)
        
        # Update consultation request
        consultation_request.status = 'confirmed'
        consultation_request.confirmed_at = datetime.utcnow()
        consultation_request.confirmed_date = datetime.strptime(data.get('confirmedDate'), '%Y-%m-%d').date()
        consultation_request.confirmed_time = datetime.strptime(data.get('confirmedTime'), '%H:%M').time()
        
        # Create appointment
        appointment = Appointment(
            patient_id=consultation_request.patient_id,
            consultation_request_id=consultation_request.id,
            service_type=consultation_request.service_type,
            appointment_date=consultation_request.confirmed_date,
            appointment_time=consultation_request.confirmed_time,
            duration_minutes=data.get('duration', 60),
            provider=data.get('provider'),
            notes=data.get('notes')
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        # Send confirmation email
        try:
            email_service.send_appointment_confirmation(consultation_request.patient, appointment)
        except Exception as email_error:
            print(f"Email sending failed: {email_error}")
        
        return jsonify({
            'success': True,
            'consultation_request': consultation_request.to_dict(),
            'appointment': appointment.to_dict(),
            'message': 'Consultation request confirmed and appointment created'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@patients_bp.route('/appointments', methods=['GET'])
def list_appointments():
    """List appointments with filtering"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        status = request.args.get('status', 'all')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        query = Appointment.query
        
        if start_date:
            query = query.filter(Appointment.appointment_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        
        if end_date:
            query = query.filter(Appointment.appointment_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        if status != 'all':
            query = query.filter_by(status=status)
        
        appointments = query.order_by(Appointment.appointment_date.asc(), Appointment.appointment_time.asc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'appointments': [apt.to_dict() for apt in appointments.items],
            'pagination': {
                'page': page,
                'pages': appointments.pages,
                'per_page': per_page,
                'total': appointments.total
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@patients_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        today = date.today()
        
        # Today's appointments
        todays_appointments = Appointment.query.filter_by(appointment_date=today).count()
        
        # Pending consultation requests
        pending_requests = ConsultationRequest.query.filter_by(status='pending').count()
        
        # Total patients
        total_patients = Patient.query.count()
        
        # This week's appointments
        from datetime import timedelta
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        weekly_appointments = Appointment.query.filter(
            Appointment.appointment_date >= week_start,
            Appointment.appointment_date <= week_end
        ).count()
        
        # Recent consultation requests (last 7 days)
        week_ago = today - timedelta(days=7)
        recent_requests = ConsultationRequest.query.filter(
            ConsultationRequest.created_at >= datetime.combine(week_ago, time.min)
        ).order_by(ConsultationRequest.created_at.desc()).limit(5).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'todays_appointments': todays_appointments,
                'pending_requests': pending_requests,
                'total_patients': total_patients,
                'weekly_appointments': weekly_appointments
            },
            'recent_requests': [req.to_dict() for req in recent_requests]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

