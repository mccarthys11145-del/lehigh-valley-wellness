from datetime import datetime, timedelta, date, time
from apscheduler.schedulers.background import BackgroundScheduler
from src.models.patient import Patient, Appointment, Communication
from src.models.user import db
from src.services.email_service import EmailService
import atexit

class AutomationService:
    def __init__(self, app=None):
        self.scheduler = BackgroundScheduler()
        self.email_service = EmailService()
        self.app = app
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize automation service with Flask app"""
        self.app = app
        
        # Schedule automated tasks
        self.scheduler.add_job(
            func=self.send_appointment_reminders,
            trigger="cron",
            hour=9,  # Run at 9 AM daily
            minute=0,
            id='daily_appointment_reminders'
        )
        
        self.scheduler.add_job(
            func=self.send_followup_communications,
            trigger="cron",
            hour=10,  # Run at 10 AM daily
            minute=0,
            id='daily_followup_communications'
        )
        
        # Start the scheduler
        self.scheduler.start()
        
        # Shut down the scheduler when exiting the app
        atexit.register(lambda: self.scheduler.shutdown())
    
    def send_appointment_reminders(self):
        """Send appointment reminders for upcoming appointments"""
        with self.app.app_context():
            try:
                # Get appointments for tomorrow (24-hour reminder)
                tomorrow = date.today() + timedelta(days=1)
                tomorrow_appointments = Appointment.query.filter_by(
                    appointment_date=tomorrow,
                    status='scheduled'
                ).all()
                
                for appointment in tomorrow_appointments:
                    # Check if reminder already sent
                    existing_reminder = Communication.query.filter_by(
                        patient_id=appointment.patient_id,
                        template_used='appointment_reminder_24h'
                    ).filter(
                        Communication.sent_at >= datetime.combine(date.today(), time.min)
                    ).first()
                    
                    if not existing_reminder:
                        success = self.email_service.send_appointment_reminder(
                            appointment.patient, 
                            appointment, 
                            hours_before=24
                        )
                        print(f"24h reminder sent to {appointment.patient.email}: {'Success' if success else 'Failed'}")
                
                # Get appointments for day after tomorrow (48-hour reminder)
                day_after_tomorrow = date.today() + timedelta(days=2)
                future_appointments = Appointment.query.filter_by(
                    appointment_date=day_after_tomorrow,
                    status='scheduled'
                ).all()
                
                for appointment in future_appointments:
                    # Check if reminder already sent
                    existing_reminder = Communication.query.filter_by(
                        patient_id=appointment.patient_id,
                        template_used='appointment_reminder_48h'
                    ).filter(
                        Communication.sent_at >= datetime.combine(date.today(), time.min)
                    ).first()
                    
                    if not existing_reminder:
                        success = self.email_service.send_appointment_reminder(
                            appointment.patient, 
                            appointment, 
                            hours_before=48
                        )
                        print(f"48h reminder sent to {appointment.patient.email}: {'Success' if success else 'Failed'}")
                        
            except Exception as e:
                print(f"Error sending appointment reminders: {e}")
    
    def send_followup_communications(self):
        """Send follow-up communications based on appointment completion"""
        with self.app.app_context():
            try:
                # Get completed appointments from yesterday for same-day follow-up
                yesterday = date.today() - timedelta(days=1)
                completed_appointments = Appointment.query.filter_by(
                    appointment_date=yesterday,
                    status='completed'
                ).all()
                
                for appointment in completed_appointments:
                    # Check if same-day follow-up already sent
                    existing_followup = Communication.query.filter_by(
                        patient_id=appointment.patient_id,
                        template_used='post_appointment_followup'
                    ).filter(
                        Communication.sent_at >= datetime.combine(date.today(), time.min)
                    ).first()
                    
                    if not existing_followup:
                        success = self.send_post_appointment_followup(appointment.patient, appointment)
                        print(f"Post-appointment follow-up sent to {appointment.patient.email}: {'Success' if success else 'Failed'}")
                
                # Get completed appointments from 3 days ago for care instructions
                three_days_ago = date.today() - timedelta(days=3)
                care_instruction_appointments = Appointment.query.filter_by(
                    appointment_date=three_days_ago,
                    status='completed'
                ).all()
                
                for appointment in care_instruction_appointments:
                    # Check if care instructions already sent
                    existing_care = Communication.query.filter_by(
                        patient_id=appointment.patient_id,
                        template_used='followup_care_instructions'
                    ).filter(
                        Communication.sent_at >= datetime.combine(date.today(), time.min)
                    ).first()
                    
                    if not existing_care:
                        success = self.send_followup_care_instructions(appointment.patient, appointment)
                        print(f"Follow-up care instructions sent to {appointment.patient.email}: {'Success' if success else 'Failed'}")
                
                # Get completed appointments from 1 week ago for satisfaction survey
                one_week_ago = date.today() - timedelta(days=7)
                survey_appointments = Appointment.query.filter_by(
                    appointment_date=one_week_ago,
                    status='completed'
                ).all()
                
                for appointment in survey_appointments:
                    # Check if survey already sent
                    existing_survey = Communication.query.filter_by(
                        patient_id=appointment.patient_id,
                        template_used='satisfaction_survey'
                    ).filter(
                        Communication.sent_at >= datetime.combine(date.today(), time.min)
                    ).first()
                    
                    if not existing_survey:
                        success = self.send_satisfaction_survey(appointment.patient, appointment)
                        print(f"Satisfaction survey sent to {appointment.patient.email}: {'Success' if success else 'Failed'}")
                        
            except Exception as e:
                print(f"Error sending follow-up communications: {e}")
    
    def send_post_appointment_followup(self, patient, appointment):
        """Send post-appointment follow-up email"""
        subject = "Thank You for Visiting Lehigh Valley Wellness"
        
        service_display = {
            'psychiatry': 'Psychiatry & Mental Health',
            'hormone': 'Hormone Optimization Consultation',
            'weight-loss': 'Medical Weight Loss Consultation',
            'peptide': 'Peptide Therapy Consultation',
            'iv-therapy': 'IV Therapy Session',
            'wellness': 'Wellness Consultation'
        }
        
        # Service-specific next steps
        next_steps = {
            'psychiatry': 'Continue with prescribed therapy sessions and medication as discussed. Monitor your mood and energy levels.',
            'hormone': 'Follow the hormone optimization protocol as outlined. Schedule follow-up lab work in 6-8 weeks.',
            'weight-loss': 'Begin your personalized nutrition plan and track your progress. Weigh yourself weekly at the same time.',
            'peptide': 'Start your peptide therapy regimen as instructed. Monitor for any side effects and benefits.',
            'iv-therapy': 'Stay hydrated and maintain a healthy diet to maximize the benefits of your IV therapy.',
            'wellness': 'Implement the wellness recommendations discussed. Focus on sleep, nutrition, and stress management.'
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
                .next-steps {{ background-color: #f0f9ff; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2563eb; }}
                .footer {{ background-color: #f1f5f9; padding: 20px; text-align: center; color: #64748b; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Thank You for Your Visit!</h1>
                <p>Lehigh Valley Wellness</p>
            </div>
            
            <div class="content">
                <p>Dear {patient.first_name},</p>
                
                <p>Thank you for choosing Lehigh Valley Wellness for your {service_display.get(appointment.service_type, appointment.service_type)} consultation today. It was a pleasure meeting with you and discussing your health goals.</p>
                
                <div class="next-steps">
                    <h3>📋 Your Next Steps</h3>
                    <p>{next_steps.get(appointment.service_type, 'Follow the personalized recommendations we discussed during your visit.')}</p>
                </div>
                
                <p><strong>Important Reminders:</strong></p>
                <ul>
                    <li>Take any prescribed medications as directed</li>
                    <li>Follow up with recommended lab work or tests</li>
                    <li>Contact us with any questions or concerns</li>
                    <li>Schedule your follow-up appointment as recommended</li>
                </ul>
                
                <p>If you have any questions or concerns, please don't hesitate to contact us at (484) 357-1916. We're here to support your wellness journey every step of the way.</p>
                
                <p>We look forward to seeing you at your next appointment!</p>
                
                <p>Best regards,<br>
                The Lehigh Valley Wellness Team</p>
            </div>
            
            <div class="footer">
                <p>Lehigh Valley Wellness | Lehigh Valley, PA | (484) 357-1916</p>
                <p>This email was sent to {patient.email}</p>
            </div>
        </body>
        </html>
        """
        
        # Send email
        success = self.email_service.send_email(patient.email, subject, html_content)
        
        # Log communication
        self.email_service.log_communication(
            patient.id,
            'email',
            subject,
            html_content,
            'post_appointment_followup',
            'sent' if success else 'failed'
        )
        
        return success
    
    def send_followup_care_instructions(self, patient, appointment):
        """Send follow-up care instructions 3 days after appointment"""
        subject = "Your Wellness Plan - Next Steps"
        
        service_display = {
            'psychiatry': 'Psychiatry & Mental Health',
            'hormone': 'Hormone Optimization Consultation',
            'weight-loss': 'Medical Weight Loss Consultation',
            'peptide': 'Peptide Therapy Consultation',
            'iv-therapy': 'IV Therapy Session',
            'wellness': 'Wellness Consultation'
        }
        
        # Service-specific care instructions
        care_instructions = {
            'psychiatry': 'Continue monitoring your mental health progress. Practice the coping strategies we discussed and maintain your medication schedule.',
            'hormone': 'You should start noticing initial improvements in energy and mood. Continue with your hormone protocol and prepare for follow-up testing.',
            'weight-loss': 'Focus on consistent meal timing and portion control. Track your food intake and celebrate small victories along the way.',
            'peptide': 'Monitor your response to peptide therapy. Note any improvements in recovery, energy, or other targeted areas.',
            'iv-therapy': 'Maintain proper hydration and nutrition to extend the benefits of your IV therapy session.',
            'wellness': 'Implement the lifestyle changes gradually. Focus on one area at a time for sustainable results.'
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
                .care-box {{ background-color: #fef3c7; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #f59e0b; }}
                .footer {{ background-color: #f1f5f9; padding: 20px; text-align: center; color: #64748b; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Your Wellness Journey Continues</h1>
                <p>Lehigh Valley Wellness</p>
            </div>
            
            <div class="content">
                <p>Dear {patient.first_name},</p>
                
                <p>It's been a few days since your {service_display.get(appointment.service_type, appointment.service_type)} appointment. We wanted to check in and provide some additional guidance for your wellness journey.</p>
                
                <div class="care-box">
                    <h3>🎯 Focus This Week</h3>
                    <p>{care_instructions.get(appointment.service_type, 'Continue following your personalized wellness plan as discussed.')}</p>
                </div>
                
                <p><strong>This Week's Goals:</strong></p>
                <ul>
                    <li>Stay consistent with your treatment plan</li>
                    <li>Monitor and track your progress</li>
                    <li>Maintain healthy lifestyle habits</li>
                    <li>Prepare any questions for your next visit</li>
                </ul>
                
                <p><strong>Need Support?</strong><br>
                Remember, we're here to help you succeed. If you have any questions about your treatment plan or experience any concerns, please call us at (484) 357-1916.</p>
                
                <p>Keep up the great work on your wellness journey!</p>
                
                <p>Best regards,<br>
                The Lehigh Valley Wellness Team</p>
            </div>
            
            <div class="footer">
                <p>Lehigh Valley Wellness | Lehigh Valley, PA | (484) 357-1916</p>
                <p>This email was sent to {patient.email}</p>
            </div>
        </body>
        </html>
        """
        
        # Send email
        success = self.email_service.send_email(patient.email, subject, html_content)
        
        # Log communication
        self.email_service.log_communication(
            patient.id,
            'email',
            subject,
            html_content,
            'followup_care_instructions',
            'sent' if success else 'failed'
        )
        
        return success
    
    def send_satisfaction_survey(self, patient, appointment):
        """Send satisfaction survey 1 week after appointment"""
        subject = "How Was Your Experience? - Lehigh Valley Wellness"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #7c3aed; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .survey-box {{ background-color: #f3e8ff; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; }}
                .button {{ background-color: #7c3aed; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px; }}
                .footer {{ background-color: #f1f5f9; padding: 20px; text-align: center; color: #64748b; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>We Value Your Feedback</h1>
                <p>Lehigh Valley Wellness</p>
            </div>
            
            <div class="content">
                <p>Dear {patient.first_name},</p>
                
                <p>It's been a week since your visit to Lehigh Valley Wellness, and we hope you're feeling great about your wellness journey!</p>
                
                <p>Your feedback is incredibly important to us and helps us continue providing exceptional care to all our patients.</p>
                
                <div class="survey-box">
                    <h3>📝 Quick 2-Minute Survey</h3>
                    <p>Please take a moment to share your experience with us:</p>
                    <a href="#" class="button">Take Survey</a>
                </div>
                
                <p><strong>We'd also love if you could:</strong></p>
                <ul>
                    <li>Leave us a review on Google</li>
                    <li>Share your experience with friends and family</li>
                    <li>Follow us on social media for wellness tips</li>
                </ul>
                
                <p>If you experienced any issues during your visit or have suggestions for improvement, please don't hesitate to call us directly at (484) 357-1916. We're committed to providing the best possible care.</p>
                
                <p>Thank you for choosing Lehigh Valley Wellness for your health and wellness needs!</p>
                
                <p>Best regards,<br>
                The Lehigh Valley Wellness Team</p>
            </div>
            
            <div class="footer">
                <p>Lehigh Valley Wellness | Lehigh Valley, PA | (484) 357-1916</p>
                <p>This email was sent to {patient.email}</p>
            </div>
        </body>
        </html>
        """
        
        # Send email
        success = self.email_service.send_email(patient.email, subject, html_content)
        
        # Log communication
        self.email_service.log_communication(
            patient.id,
            'email',
            subject,
            html_content,
            'satisfaction_survey',
            'sent' if success else 'failed'
        )
        
        return success
    
    def send_wellness_checkin(self, patient, appointment):
        """Send wellness check-in 1 month after appointment"""
        subject = "Your Wellness Journey - Monthly Check-In"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #059669; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .checkin-box {{ background-color: #ecfdf5; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #059669; }}
                .button {{ background-color: #059669; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 5px; }}
                .footer {{ background-color: #f1f5f9; padding: 20px; text-align: center; color: #64748b; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>How Are You Feeling?</h1>
                <p>Lehigh Valley Wellness Monthly Check-In</p>
            </div>
            
            <div class="content">
                <p>Dear {patient.first_name},</p>
                
                <p>It's been a month since your visit to Lehigh Valley Wellness! We hope you're continuing to see positive results from your wellness plan.</p>
                
                <div class="checkin-box">
                    <h3>🌟 Monthly Wellness Check-In</h3>
                    <p>We'd love to hear about your progress and see if there's anything we can do to support your continued success.</p>
                    
                    <p><strong>Quick questions:</strong></p>
                    <ul>
                        <li>How are you feeling overall?</li>
                        <li>Are you seeing the results you expected?</li>
                        <li>Do you have any new health goals?</li>
                        <li>Would you like to schedule a follow-up?</li>
                    </ul>
                </div>
                
                <div style="text-align: center;">
                    <a href="#" class="button">Schedule Follow-Up</a>
                    <a href="#" class="button" style="background-color: #2563eb;">Share Progress</a>
                </div>
                
                <p><strong>Remember:</strong> Consistency is key to achieving lasting wellness results. If you have any questions or concerns about your progress, we're here to help adjust your plan as needed.</p>
                
                <p>Thank you for trusting Lehigh Valley Wellness with your health journey. We're honored to be part of your wellness story!</p>
                
                <p>Best regards,<br>
                The Lehigh Valley Wellness Team</p>
            </div>
            
            <div class="footer">
                <p>Lehigh Valley Wellness | Lehigh Valley, PA | (484) 357-1916</p>
                <p>This email was sent to {patient.email}</p>
            </div>
        </body>
        </html>
        """
        
        # Send email
        success = self.email_service.send_email(patient.email, subject, html_content)
        
        # Log communication
        self.email_service.log_communication(
            patient.id,
            'email',
            subject,
            html_content,
            'wellness_checkin',
            'sent' if success else 'failed'
        )
        
        return success

