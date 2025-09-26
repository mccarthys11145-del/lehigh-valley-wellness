import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.patient import Patient, ConsultationRequest, Appointment, Communication, EmailTemplate
from src.routes.user import user_bp
from src.routes.patients import patients_bp
from src.services.automation_service import AutomationService

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(patients_bp, url_prefix='/api')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initialize automation service
automation_service = AutomationService(app)

with app.app_context():
    db.create_all()
    
    # Create default email templates if they don't exist
    from src.services.email_service import EmailService
    email_service = EmailService()
    
    # Check if templates exist, create if not
    if not EmailTemplate.query.filter_by(name='consultation_request_confirmation').first():
        template = EmailTemplate(
            name='consultation_request_confirmation',
            subject='Consultation Request Received - Lehigh Valley Wellness',
            html_content='Default consultation request confirmation template',
            trigger_event='consultation_request_created'
        )
        db.session.add(template)
    
    if not EmailTemplate.query.filter_by(name='appointment_confirmation').first():
        template = EmailTemplate(
            name='appointment_confirmation',
            subject='Appointment Confirmed - {{appointment_date}} at {{appointment_time}}',
            html_content='Default appointment confirmation template',
            trigger_event='appointment_confirmed'
        )
        db.session.add(template)
    
    try:
        db.session.commit()
    except:
        db.session.rollback()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
