# Lehigh Valley Wellness - Integrated Patient Communication Systems

A comprehensive digital transformation solution for Lehigh Valley Wellness, featuring a professional website, AI-powered patient communication tools, and automated practice management systems.

## 🏥 Project Overview

This repository contains the complete digital infrastructure for Lehigh Valley Wellness, designed to modernize patient communication and streamline practice operations following the transition to non-DEA services.

### Key Features

- **Professional Website** - Modern, responsive website with comprehensive service information
- **AI Chat Widget** - 24/7 intelligent patient support and consultation assistance
- **AI Receptionist** - Automated phone system with intelligent call routing
- **CRM Integration** - Comprehensive patient management and automation system
- **Admin Dashboard** - Secure portal for staff to manage patient information

## 🚀 Live Demo

**Website:** [https://nghki1cjo9kz.manus.space](https://nghki1cjo9kz.manus.space)

## 📁 Repository Structure

```
lehigh-valley-wellness-repo/
├── website/                 # React-based website application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── App.jsx        # Main application component
│   │   └── App.css        # Styling
│   ├── package.json       # Dependencies and scripts
│   └── vite.config.js     # Build configuration
├── ai-receptionist/        # Flask-based AI phone system
│   ├── src/
│   │   ├── models/        # Database models
│   │   ├── routes/        # API endpoints
│   │   ├── services/      # Business logic
│   │   └── main.py        # Application entry point
│   └── requirements.txt   # Python dependencies
├── crm-system/            # Customer relationship management
│   ├── src/
│   │   ├── models/        # Patient data models
│   │   ├── routes/        # CRM API endpoints
│   │   ├── services/      # Automation services
│   │   └── main.py        # CRM application
│   └── requirements.txt   # Python dependencies
└── docs/                  # Documentation
    ├── system_testing_report.md
    ├── staff_training_manual.md
    ├── voip_configuration_guide.md
    └── implementation_roadmap.md
```

## 🛠️ Technology Stack

### Frontend
- **React 18** - Modern UI framework
- **Vite** - Fast build tool and development server
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide Icons** - Beautiful icon library

### Backend
- **Flask** - Python web framework for AI services
- **SQLAlchemy** - Database ORM
- **OpenAI API** - AI-powered chat and voice responses
- **Twilio API** - Voice communication and SMS

### Infrastructure
- **Manus Platform** - Hosting and deployment
- **SQLite** - Database for development
- **HTTPS** - Secure communication

## 🚀 Quick Start

### Website Development

```bash
cd website
npm install
npm run dev
```

The website will be available at `http://localhost:5173`

### AI Receptionist System

```bash
cd ai-receptionist
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

The AI receptionist API will be available at `http://localhost:5000`

### CRM System

```bash
cd crm-system
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

The CRM API will be available at `http://localhost:5001`

## 🔧 Configuration

### Environment Variables

Create `.env` files in each system directory with the following variables:

**AI Receptionist (.env)**
```
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+14843571916
OPENAI_API_KEY=your_openai_key
BASE_URL=https://your-domain.com
```

**CRM System (.env)**
```
DATABASE_URL=sqlite:///database/app.db
EMAIL_API_KEY=your_email_service_key
PRACTICE_EMAIL=info@lehighvalleywellness.org
```

## 📋 Features

### Website Features
- Responsive design optimized for all devices
- Comprehensive service information and pricing
- Multi-step consultation request system
- Professional branding and messaging
- SEO-optimized content

### AI Chat Widget
- 24/7 availability for patient inquiries
- Natural language processing for intelligent responses
- Appointment scheduling assistance
- Seamless escalation to human staff
- Integration with CRM for patient data

### AI Receptionist
- Automated call answering and routing
- Speech recognition and text-to-speech
- Emergency detection and appropriate routing
- Consultation request creation via phone
- Complete call logging and analytics

### CRM Integration
- Automated patient record creation
- Email notification system
- Appointment tracking and management
- Patient communication history
- Reporting and analytics dashboard

## 🔒 Security Features

- Password-protected admin access
- HTTPS encryption for all communications
- Input validation and sanitization
- HIPAA-compliant data handling
- Secure API authentication

## 📊 System Requirements

### Development Environment
- Node.js 18+ for website development
- Python 3.8+ for backend services
- Git for version control
- Modern web browser for testing

### Production Environment
- Web hosting with HTTPS support
- Python hosting for Flask applications
- Database hosting (PostgreSQL recommended)
- Twilio account for phone services
- OpenAI API access for AI features

## 🚀 Deployment

### Website Deployment
The website is currently deployed on the Manus platform and can be redeployed using:

```bash
cd website
npm run build
# Deploy dist/ folder to your hosting provider
```

### Backend Services
Both the AI receptionist and CRM systems can be deployed to any Python hosting service:

```bash
# Install dependencies
pip install -r requirements.txt

# Run with production WSGI server
gunicorn -w 4 -b 0.0.0.0:8000 src.main:app
```

## 📖 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[System Testing Report](docs/system_testing_report.md)** - Complete testing results and system status
- **[Staff Training Manual](docs/staff_training_manual.md)** - User guide for practice staff
- **[VoIP Configuration Guide](docs/voip_configuration_guide.md)** - Technical setup for phone integration
- **[Implementation Roadmap](docs/implementation_roadmap.md)** - Project timeline and milestones

## 🤝 Support

For technical support or questions about the system:

- Review the documentation in the `docs/` directory
- Check the system testing report for known issues
- Refer to the staff training manual for usage instructions

## 📄 License

This project is proprietary software developed specifically for Lehigh Valley Wellness. All rights reserved.

## 🏆 Project Status

- ✅ Website: Fully operational
- ✅ AI Chat Widget: Fully operational  
- ✅ Consultation Request System: Fully operational
- ✅ AI Receptionist: Ready for phone integration
- ✅ CRM System: Architecturally complete
- 🔄 Admin Dashboard: Partially implemented
- 🔄 Phone System Integration: Pending Twilio setup

## 📞 Contact Information

**Lehigh Valley Wellness**
- Phone: (484) 357-1916
- Email: info@lehighvalleywellness.org
- Website: https://nghki1cjo9kz.manus.space

---

*Built with ❤️ for Lehigh Valley Wellness by Manus AI*
