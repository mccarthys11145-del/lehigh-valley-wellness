import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from src.models.patient import Communication, EmailTemplate
from src.models.user import db

class EmailService:
    def __init__(self):
        # Email configuration - in production, these should be environment variables
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_address = "info@lehighvalleywellness.org"
        self.email_password = "your_app_password"  # Use app password for Gmail
        self.from_name = "Lehigh Valley Wellness"
        
    def send_email(self, to_email, subject, html_content, text_content=None):
        """Send an email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.email_address}>"
            msg['To'] = to_email
            
            # Add text and HTML parts
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False
    
    def log_communication(self, patient_id, communication_type, subject, message, template_used=None, status='sent'):
        """Log communication in the database"""
        try:
            communication = Communication(
                patient_id=patient_id,
                communication_type=communication_type,
                subject=subject,
                message=message,
                template_used=template_used,
                status=status
            )
            db.session.add(communication)
            db.session.commit()
            return True
        except Exception as e:
            print(f"Failed to log communication: {e}")
            return False
    
    def render_template(self, template_content, variables):
        """Simple template rendering with variable substitution"""
        content = template_content
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value) if value else '')
        return content
    
    def send_consultation_request_confirmation(self, patient, consultation_request):
        """Send confirmation email for consultation request"""
        subject = "Consultation Request Received - Lehigh Valley Wellness"
        
        # Service type mapping for display
        service_display = {
            'psychiatry': 'Psychiatry & Mental Health',
            'hormone': 'Hormone Optimization Consultation',
            'weight-loss': 'Medical Weight Loss Consultation',
            'peptide': 'Peptide Therapy Consultation',
            'wellness': 'Wellness Consultation'
        }
        
        variables = {
            'patient_first_name': patient.first_name,
            'service_type': service_display.get(consultation_request.service_type, consultation_request.service_type),
            'preferred_date': consultation_request.preferred_date.strftime('%B %d, %Y') if consultation_request.preferred_date else 'Not specified',
            'preferred_time': consultation_request.preferred_time.strftime('%I:%M %p') if consultation_request.preferred_time else 'Not specified',
            'practice_phone': '(484) 357-1916'
        }
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #2563eb; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .details {{ background-color: #f8fafc; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ background-color: #f1f5f9; padding: 20px; text-align: center; color: #64748b; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Lehigh Valley Wellness</h1>
                <p>Your Consultation Request Has Been Received</p>
            </div>
            
            <div class="content">
                <p>Dear {variables['patient_first_name']},</p>
                
                <p>Thank you for your consultation request with Lehigh Valley Wellness. We're excited to help you on your wellness journey.</p>
                
                <div class="details">
                    <h3>Your Request Details:</h3>
                    <ul>
                        <li><strong>Service:</strong> {variables['service_type']}</li>
                        <li><strong>Preferred Date:</strong> {variables['preferred_date']}</li>
                        <li><strong>Preferred Time:</strong> {variables['preferred_time']}</li>
                    </ul>
                </div>
                
                <p>Our team will contact you within 24 hours to confirm your appointment details and answer any questions you may have.</p>
                
                <p><strong>In the meantime, please:</strong></p>
                <ul>
                    <li>Check your email for appointment confirmation</li>
                    <li>Prepare any questions about your health goals</li>
                    <li>Gather any relevant medical records</li>
                </ul>
                
                <p>If you have any immediate questions, please don't hesitate to call us at {variables['practice_phone']}.</p>
                
                <p>Best regards,<br>
                The Lehigh Valley Wellness Team</p>
            </div>
            
            <div class="footer">
                <p>Lehigh Valley Wellness | 6081 Hamilton Blvd Suite 600, Allentown, PA 18106 | {variables['practice_phone']}</p>
                <p>This email was sent to {patient.email}</p>
            </div>
        </body>
        </html>
        """
        
        # Send email
        success = self.send_email(patient.email, subject, html_content)
        
        # Log communication
        self.log_communication(
            patient.id,
            'email',
            subject,
            html_content,
            'consultation_request_confirmation',
            'sent' if success else 'failed'
        )
        
        return success
    
    def send_appointment_confirmation(self, patient, appointment):
        """Send appointment confirmation email"""
        subject = f"Appointment Confirmed - {appointment.appointment_date.strftime('%B %d')} at {appointment.appointment_time.strftime('%I:%M %p')}"
        
        # Service pricing mapping
        service_pricing = {
            'psychiatry': '$250',
            'hormone': '$200',
            'weight-loss': '$175',
            'peptide': '$150',
            'wellness': '$200'
        }

        # Service duration mapping
        service_duration = {
            'psychiatry': '60 minutes',
            'hormone': '45 minutes',
            'weight-loss': '45 minutes',
            'peptide': '30 minutes',
            'wellness': '60 minutes'
        }

        # Service preparation instructions
        service_prep = {
            'psychiatry': 'Please complete intake forms 24 hours before your appointment',
            'hormone': 'Fasting lab work may be required before your visit',
            'weight-loss': 'Please bring current medications and recent lab results',
            'peptide': 'Health history review and goal assessment',
            'wellness': 'Complete health questionnaire and bring recent lab work'
        }

        service_display = {
            'psychiatry': 'Psychiatry & Mental Health',
            'hormone': 'Hormone Optimization Consultation',
            'weight-loss': 'Medical Weight Loss Consultation',
            'peptide': 'Peptide Therapy Consultation',
            'wellness': 'Wellness Consultation'
        }
        
        variables = {
            'patient_first_name': patient.first_name,
            'appointment_date': appointment.appointment_date.strftime('%A, %B %d, %Y'),
            'appointment_time': appointment.appointment_time.strftime('%I:%M %p'),
            'service_type': service_display.get(appointment.service_type, appointment.service_type),
            'duration': service_duration.get(appointment.service_type, f'{appointment.duration_minutes} minutes'),
            'service_price': service_pricing.get(appointment.service_type, 'Please call for pricing'),
            'preparation_instructions': service_prep.get(appointment.service_type, 'No special preparation required'),
            'practice_phone': '(484) 357-1916',
            'practice_address': '6081 Hamilton Blvd Suite 600, Allentown, PA 18106'
        }
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #16a34a; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .appointment-details {{ background-color: #f0f9ff; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2563eb; }}
                .preparation {{ background-color: #fef3c7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ background-color: #f1f5f9; padding: 20px; text-align: center; color: #64748b; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>✓ Appointment Confirmed</h1>
                <p>Lehigh Valley Wellness</p>
            </div>
            
            <div class="content">
                <p>Dear {variables['patient_first_name']},</p>
                
                <p>Your consultation appointment has been confirmed! We're looking forward to meeting with you.</p>
                
                <div class="appointment-details">
                    <h3>📅 Appointment Details</h3>
                    <ul>
                        <li><strong>Date:</strong> {variables['appointment_date']}</li>
                        <li><strong>Time:</strong> {variables['appointment_time']}</li>
                        <li><strong>Service:</strong> {variables['service_type']}</li>
                        <li><strong>Duration:</strong> {variables['duration']}</li>
                        <li><strong>Investment:</strong> {variables['service_price']}</li>
                    </ul>
                </div>
                
                <h3>📍 Location</h3>
                <p>Lehigh Valley Wellness<br>
                {variables['practice_address']}</p>
                
                <div class="preparation">
                    <h3>📋 Before Your Visit</h3>
                    <p>{variables['preparation_instructions']}</p>
                </div>
                
                <p><strong>Need to reschedule or have questions?</strong><br>
                Please call us at {variables['practice_phone']} at least 24 hours in advance.</p>
                
                <p>We're excited to help you achieve your wellness goals!</p>
                
                <p>Best regards,<br>
                The Lehigh Valley Wellness Team</p>
            </div>
            
            <div class="footer">
                <p>Lehigh Valley Wellness | {variables['practice_address']} | {variables['practice_phone']}</p>
                <p>This email was sent to {patient.email}</p>
            </div>
        </body>
        </html>
        """
        
        # Send email
        success = self.send_email(patient.email, subject, html_content)
        
        # Log communication
        self.log_communication(
            patient.id,
            'email',
            subject,
            html_content,
            'appointment_confirmation',
            'sent' if success else 'failed'
        )
        
        return success
    
    def send_appointment_reminder(self, patient, appointment, hours_before=24):
        """Send appointment reminder email"""
        subject = f"Appointment Reminder - Tomorrow at {appointment.appointment_time.strftime('%I:%M %p')}"
        
        if hours_before == 48:
            subject = f"Appointment Reminder - {appointment.appointment_date.strftime('%A')} at {appointment.appointment_time.strftime('%I:%M %p')}"
        
        service_display = {
            'psychiatry': 'Psychiatry & Mental Health',
            'hormone': 'Hormone Optimization Consultation',
            'weight-loss': 'Medical Weight Loss Consultation',
            'peptide': 'Peptide Therapy Consultation',
            'wellness': 'Wellness Consultation'
        }
        
        variables = {
            'patient_first_name': patient.first_name,
            'appointment_date': appointment.appointment_date.strftime('%A, %B %d, %Y'),
            'appointment_time': appointment.appointment_time.strftime('%I:%M %p'),
            'service_type': service_display.get(appointment.service_type, appointment.service_type),
            'practice_phone': '(484) 357-1916'
        }
        
        time_reference = "tomorrow" if hours_before == 24 else appointment.appointment_date.strftime('%A')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #f59e0b; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .reminder-box {{ background-color: #fef3c7; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #f59e0b; }}
                .footer {{ background-color: #f1f5f9; padding: 20px; text-align: center; color: #64748b; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>⏰ Appointment Reminder</h1>
                <p>Lehigh Valley Wellness</p>
            </div>
            
            <div class="content">
                <p>Dear {variables['patient_first_name']},</p>
                
                <p>This is a friendly reminder that you have an appointment with Lehigh Valley Wellness {time_reference}.</p>
                
                <div class="reminder-box">
                    <h3>📅 Appointment Details</h3>
                    <ul>
                        <li><strong>Date:</strong> {variables['appointment_date']}</li>
                        <li><strong>Time:</strong> {variables['appointment_time']}</li>
                        <li><strong>Service:</strong> {variables['service_type']}</li>
                    </ul>
                </div>
                
                <p><strong>Please remember to:</strong></p>
                <ul>
                    <li>Arrive 10 minutes early for check-in</li>
                    <li>Bring a valid ID and insurance card</li>
                    <li>Complete any required forms beforehand</li>
                    <li>Bring any questions you may have</li>
                </ul>
                
                <p>If you need to reschedule, please call us at {variables['practice_phone']} as soon as possible.</p>
                
                <p>We look forward to seeing you {time_reference}!</p>
                
                <p>Best regards,<br>
                The Lehigh Valley Wellness Team</p>
            </div>
            
            <div class="footer">
                <p>Lehigh Valley Wellness | 6081 Hamilton Blvd Suite 600, Allentown, PA 18106 | {variables['practice_phone']}</p>
                <p>This email was sent to {patient.email}</p>
            </div>
        </body>
        </html>
        """
        
        # Send email
        success = self.send_email(patient.email, subject, html_content)
        
        # Log communication
        self.log_communication(
            patient.id,
            'email',
            subject,
            html_content,
            f'appointment_reminder_{hours_before}h',
            'sent' if success else 'failed'
        )
        
        return success

