# Phone System Integration Setup Guide
## Lehigh Valley Wellness AI Receptionist

This guide provides step-by-step instructions for setting up the phone system integration with Twilio for the Lehigh Valley Wellness AI receptionist system.

## Overview

The AI receptionist system is designed to handle incoming calls to the practice phone number (484-357-1916) and provide intelligent responses for:

- **Appointment scheduling** - Patients can request appointments for various services
- **Service information** - Information about available treatments and programs
- **Practice hours and location** - Basic practice information
- **Emergency handling** - Automatic detection and routing of emergency calls
- **Human transfer** - Seamless transfer to staff when needed

## Prerequisites

### 1. Twilio Account Setup
- Create a Twilio account at [twilio.com](https://www.twilio.com)
- Verify your account and add payment method
- Note your Account SID and Auth Token from the Console

### 2. Phone Number Configuration
- Purchase or port the practice phone number: **+14843571916**
- Configure the number for voice calls
- Set up webhook URLs (detailed below)

### 3. Environment Variables
Set the following environment variables in your deployment:

```bash
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+14843571916
BASE_URL=https://your-domain.com
```

## Webhook Configuration

Configure the following webhook URLs in your Twilio Console:

### Voice Configuration
- **Incoming Calls**: `https://your-domain.com/api/twilio/incoming-call`
- **Method**: POST
- **Fallback URL**: `https://your-domain.com/api/twilio/incoming-call`

### Status Callbacks
- **Status Callback URL**: `https://your-domain.com/api/twilio/call-status`
- **Status Callback Events**: `initiated`, `ringing`, `answered`, `completed`

## API Endpoints

The system provides the following endpoints:

### Twilio Webhooks
- `POST /api/twilio/incoming-call` - Handle incoming calls
- `POST /api/twilio/process-speech` - Process speech input
- `POST /api/twilio/call-status` - Handle call status updates
- `GET/POST /api/twilio/outbound-twiml` - Generate outbound call TwiML

### Management APIs
- `POST /api/twilio/make-outbound-call` - Initiate outbound calls
- `GET /api/voice/call-analytics` - View call analytics
- `GET /api/voice/call-history` - View call history

## Call Flow

### 1. Incoming Call Process
1. **Call Received** - Twilio receives call to practice number
2. **Emergency Notice** - AI plays emergency disclaimer
3. **Greeting** - AI introduces itself and asks how to help
4. **Speech Recognition** - Twilio converts speech to text
5. **Intent Detection** - AI analyzes request and determines intent
6. **Response Generation** - AI generates appropriate response
7. **Action Execution** - System performs requested actions (scheduling, etc.)
8. **Transfer or Continue** - Either transfer to human or continue conversation

### 2. Emergency Handling
- **Keyword Detection** - System monitors for emergency keywords
- **Immediate Transfer** - Automatic transfer to emergency services
- **Logging** - All emergency calls are logged for review

### 3. Appointment Scheduling
- **Information Gathering** - AI collects patient details and preferences
- **CRM Integration** - Creates consultation request in CRM system
- **Confirmation** - Provides confirmation and next steps
- **Follow-up** - Schedules follow-up call for confirmation

## Testing Procedures

### 1. Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TWILIO_ACCOUNT_SID=your_sid
export TWILIO_AUTH_TOKEN=your_token
export TWILIO_PHONE_NUMBER=+14843571916

# Run the application
python src/main.py

# Use ngrok for local webhook testing
ngrok http 5000
```

### 2. Test Scenarios
1. **Basic Greeting Test**
   - Call the number
   - Verify emergency message plays
   - Verify AI greeting plays
   - Test speech recognition

2. **Appointment Scheduling Test**
   - Request appointment for hormone therapy
   - Provide patient information
   - Verify consultation request is created
   - Check CRM integration

3. **Emergency Test**
   - Use emergency keywords ("chest pain", "emergency")
   - Verify immediate transfer occurs
   - Check logging and alerts

4. **Transfer Test**
   - Request to speak with staff
   - Verify smooth transfer occurs
   - Test fallback scenarios

## Deployment Checklist

### Pre-Deployment
- [ ] Twilio account configured
- [ ] Phone number purchased and configured
- [ ] Environment variables set
- [ ] Dependencies installed
- [ ] Database migrations run
- [ ] CRM integration tested

### Deployment
- [ ] Application deployed to production
- [ ] Public URL configured
- [ ] Webhook URLs updated in Twilio Console
- [ ] SSL certificate configured
- [ ] Health checks passing

### Post-Deployment
- [ ] Test incoming calls
- [ ] Test speech recognition
- [ ] Test appointment scheduling
- [ ] Test emergency handling
- [ ] Test human transfers
- [ ] Monitor call logs
- [ ] Set up alerts and monitoring

## Monitoring and Analytics

### Call Analytics
The system tracks:
- **Call Volume** - Number of calls per day/hour
- **Intent Distribution** - Most common call reasons
- **Success Rate** - Successful vs. transferred calls
- **Response Time** - AI response latency
- **Patient Satisfaction** - Based on call completion

### Logging
All calls are logged with:
- Call duration and status
- Conversation transcript
- Intent detection results
- Actions taken
- Transfer reasons
- Patient information (if available)

### Alerts
Set up alerts for:
- High call volume
- Emergency calls
- System errors
- Failed transfers
- Low speech recognition confidence

## Troubleshooting

### Common Issues

1. **Webhook Not Receiving Calls**
   - Check Twilio Console webhook configuration
   - Verify public URL is accessible
   - Check SSL certificate
   - Review server logs

2. **Speech Recognition Issues**
   - Check audio quality
   - Verify language settings
   - Review confidence scores
   - Test with different speakers

3. **Transfer Failures**
   - Verify transfer numbers are correct
   - Check network connectivity
   - Review transfer logic
   - Test fallback scenarios

4. **Database Issues**
   - Check database connectivity
   - Verify table structure
   - Review migration status
   - Check disk space

### Support Contacts
- **Twilio Support**: [support.twilio.com](https://support.twilio.com)
- **System Administrator**: Contact practice IT team
- **Emergency Escalation**: Practice manager

## Security Considerations

### Webhook Security
- Implement Twilio request validation
- Use HTTPS for all endpoints
- Validate all input parameters
- Log security events

### Data Protection
- Encrypt sensitive patient data
- Implement access controls
- Regular security audits
- HIPAA compliance measures

### Call Recording
- Obtain proper consent
- Secure storage of recordings
- Retention policy compliance
- Access logging

## Cost Management

### Twilio Pricing
- **Voice calls**: ~$0.0085 per minute
- **Speech recognition**: ~$0.02 per request
- **Phone number**: ~$1.00 per month

### Optimization Tips
- Monitor call duration
- Optimize speech recognition usage
- Use efficient TwiML responses
- Implement call routing logic

## Future Enhancements

### Planned Features
- **Multi-language support** - Spanish language option
- **Advanced analytics** - Detailed reporting dashboard
- **Integration expansion** - Additional CRM systems
- **Voice biometrics** - Patient identification by voice
- **Appointment reminders** - Automated outbound calls

### Technical Improvements
- **Load balancing** - Handle high call volumes
- **Redundancy** - Failover systems
- **Performance optimization** - Reduce response latency
- **Advanced AI** - Improved natural language processing

---

## Quick Start Commands

```bash
# Clone and setup
git clone <repository>
cd ai-receptionist

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your Twilio credentials

# Run database migrations
python -c "from src.main import app, db; app.app_context().push(); db.create_all()"

# Start the application
python src/main.py

# Test with ngrok (for development)
ngrok http 5000
```

For production deployment, use a proper WSGI server like Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
```
