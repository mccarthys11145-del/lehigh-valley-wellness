import openai
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIReceptionistService:
    """
    AI service for handling natural language processing, intent detection,
    and conversation management for the phone receptionist system.
    """
    
    def __init__(self):
        self.client = openai.OpenAI()
        self.conversation_context = {}
        
        # Define intents and their patterns
        self.intents = {
            'appointment_scheduling': [
                'schedule', 'appointment', 'book', 'available', 'when can i',
                'need to see', 'consultation', 'visit', 'come in'
            ],
            'appointment_modification': [
                'reschedule', 'cancel', 'change', 'move', 'different time',
                'postpone', 'earlier', 'later'
            ],
            'service_inquiry': [
                'what is', 'tell me about', 'how much', 'cost', 'price',
                'hormone', 'weight loss', 'peptide', 'therapy', 'treatment'
            ],
            'billing_inquiry': [
                'bill', 'payment', 'insurance', 'cost', 'charge', 'fee',
                'copay', 'deductible', 'coverage'
            ],
            'general_info': [
                'hours', 'location', 'address', 'phone', 'contact',
                'directions', 'parking'
            ],
            'emergency': [
                'emergency', 'urgent', 'pain', 'bleeding', 'chest pain',
                'can\'t breathe', 'overdose', 'suicide', 'help'
            ]
        }
        
        # Service information
        self.services = {
            'psychiatry': {
                'name': 'Psychiatry & Mental Health',
                'duration': 60,
                'price': 250,
                'description': 'Comprehensive mental health care including therapy and psychiatric evaluations'
            },
            'hormone_optimization': {
                'name': 'Hormone Optimization',
                'duration': 45,
                'price': 200,
                'description': 'Advanced hormone replacement therapy for men and women'
            },
            'weight_loss': {
                'name': 'Medical Weight Loss',
                'duration': 45,
                'price': 175,
                'description': 'Physician-supervised weight loss programs with personalized coaching'
            },
            'peptide_therapy': {
                'name': 'Peptide Therapy',
                'duration': 30,
                'price': 150,
                'description': 'FDA-approved peptide treatments for anti-aging and wellness'
            },
            'wellness_consultation': {
                'name': 'Wellness Consultation',
                'duration': 60,
                'price': 200,
                'description': 'Comprehensive wellness assessments and optimization plans'
            }
        }

        # Practice information
        self.practice_info = {
            'name': 'Lehigh Valley Wellness',
            'phone': '(484) 357-1916',
            'address': '6081 Hamilton Blvd Suite 600, Allentown, PA 18106',
            'hours': 'Monday-Friday: 8:00 AM - 6:00 PM',
            'website': 'lehighvalleywellness.org'
        }
    
    def detect_intent(self, message: str) -> Tuple[str, float]:
        """
        Detect the intent of a patient message using keyword matching and AI analysis.
        Returns tuple of (intent, confidence_score)
        """
        message_lower = message.lower()
        intent_scores = {}
        
        # Keyword-based intent detection
        for intent, keywords in self.intents.items():
            score = 0
            for keyword in keywords:
                if keyword in message_lower:
                    score += 1
            if score > 0:
                intent_scores[intent] = score / len(keywords)
        
        # If no clear intent from keywords, use AI analysis
        if not intent_scores:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": """You are an AI assistant helping to classify patient intents for a medical practice. 
                            Classify the following message into one of these categories:
                            - appointment_scheduling: Patient wants to schedule a new appointment
                            - appointment_modification: Patient wants to change/cancel existing appointment
                            - service_inquiry: Patient asking about services, treatments, or procedures
                            - billing_inquiry: Patient asking about costs, insurance, or billing
                            - general_info: Patient asking about practice hours, location, contact info
                            - emergency: Patient has urgent medical need or emergency
                            
                            Respond with only the category name."""
                        },
                        {"role": "user", "content": message}
                    ],
                    max_tokens=50,
                    temperature=0.1
                )
                
                ai_intent = response.choices[0].message.content.strip().lower()
                if ai_intent in self.intents:
                    return ai_intent, 0.8
                    
            except Exception as e:
                logger.error(f"Error in AI intent detection: {e}")
        
        # Return highest scoring intent or default
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            return best_intent, intent_scores[best_intent]
        
        return 'general_info', 0.3
    
    def extract_entities(self, message: str, intent: str) -> Dict:
        """
        Extract relevant entities from the message based on the detected intent.
        """
        entities = {}
        message_lower = message.lower()
        
        # Extract dates and times
        date_patterns = [
            r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'(tomorrow|today|next week|this week)',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}'
        ]
        
        time_patterns = [
            r'(\d{1,2}:\d{2}\s*(?:am|pm))',
            r'(\d{1,2}\s*(?:am|pm))',
            r'(morning|afternoon|evening)',
            r'(early|late)\s+(morning|afternoon)'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, message_lower)
            if matches:
                entities['preferred_date'] = matches[0]
                break
        
        for pattern in time_patterns:
            matches = re.findall(pattern, message_lower)
            if matches:
                entities['preferred_time'] = matches[0]
                break
        
        # Extract service types
        for service_key, service_info in self.services.items():
            service_keywords = service_info['name'].lower().split()
            if any(keyword in message_lower for keyword in service_keywords):
                entities['service_type'] = service_key
                break
        
        # Extract patient information
        phone_pattern = r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})'
        phone_matches = re.findall(phone_pattern, message)
        if phone_matches:
            entities['phone_number'] = phone_matches[0]
        
        name_pattern = r'my name is ([a-zA-Z\s]+)'
        name_matches = re.findall(name_pattern, message_lower)
        if name_matches:
            entities['patient_name'] = name_matches[0].strip()
        
        return entities
    
    def generate_response(self, message: str, intent: str, entities: Dict, 
                         conversation_history: List[Dict] = None) -> str:
        """
        Generate an appropriate response based on the message, intent, and entities.
        """
        if conversation_history is None:
            conversation_history = []
        
        # Handle emergency situations first
        if intent == 'emergency':
            return self._handle_emergency_response()
        
        # Generate context-aware response using AI
        try:
            system_prompt = f"""You are a professional AI receptionist for {self.practice_info['name']},
            a wellness practice offering hormone optimization, medical weight loss, psychiatry,
            peptide therapy, and wellness consultations.
            
            Practice Information:
            - Phone: {self.practice_info['phone']}
            - Hours: {self.practice_info['hours']}
            - Location: {self.practice_info['address']}
            
            Services and Pricing:
            {json.dumps(self.services, indent=2)}
            
            Guidelines:
            - Be professional, warm, and helpful
            - For appointment scheduling, ask for preferred date/time and service type
            - Provide accurate service information and pricing
            - For billing questions, direct to billing department
            - Always offer to help further
            - Keep responses concise but informative
            - If you can't help, offer to transfer to staff
            
            Current conversation intent: {intent}
            Extracted information: {json.dumps(entities)}
            """
            
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history
            for turn in conversation_history[-6:]:  # Last 6 turns for context
                messages.append({
                    "role": "user" if turn['speaker'] == 'patient' else "assistant",
                    "content": turn['message']
                })
            
            messages.append({"role": "user", "content": message})
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return self._get_fallback_response(intent)
    
    def _handle_emergency_response(self) -> str:
        """Handle emergency situations with appropriate response."""
        return """I understand this may be an emergency situation. If this is a life-threatening emergency, 
        please hang up and call 911 immediately. 
        
        For urgent medical concerns, I'm transferring you to our on-call provider right away. 
        Please stay on the line."""
    
    def _get_fallback_response(self, intent: str) -> str:
        """Provide fallback responses when AI generation fails."""
        fallback_responses = {
            'appointment_scheduling': f"""I'd be happy to help you schedule an appointment.
            We offer consultations for hormone optimization, medical weight loss, psychiatry,
            peptide therapy, and wellness consultations.
            
            What type of service are you interested in, and do you have a preferred date and time?
            
            You can also visit our website or call us at {self.practice_info['phone']}.""",
            
            'service_inquiry': f"""We offer several wellness services including:
            - Hormone Optimization ($200, 45 min)
            - Medical Weight Loss ($175, 45 min)
            - Psychiatry & Mental Health ($250, 60 min)
            - Peptide Therapy ($150, 30 min)
            - Wellness Consultations ($200, 60 min)
            
            Which service would you like to know more about?""",
            
            'general_info': f"""Here's our practice information:
            
            {self.practice_info['name']}
            Phone: {self.practice_info['phone']}
            Hours: {self.practice_info['hours']}
            Location: {self.practice_info['address']}
            
            How else can I help you today?""",
            
            'billing_inquiry': """For billing questions, insurance coverage, and payment information, 
            I'll connect you with our billing department. They can provide detailed information 
            about costs, insurance coverage, and payment options.
            
            Would you like me to transfer you now?"""
        }
        
        return fallback_responses.get(intent, 
            f"""Thank you for calling {self.practice_info['name']}. 
            I'm here to help with appointments, service information, and general questions. 
            How can I assist you today?""")
    
    def should_transfer_to_human(self, intent: str, confidence: float, 
                                conversation_turns: int) -> Tuple[bool, str]:
        """
        Determine if the call should be transferred to a human based on various factors.
        """
        # Always transfer emergencies
        if intent == 'emergency':
            return True, "Emergency situation requiring immediate human attention"
        
        # Transfer if AI confidence is very low
        if confidence < 0.3:
            return True, "Low confidence in understanding patient request"
        
        # Transfer if conversation is getting too long without resolution
        if conversation_turns > 10:
            return True, "Extended conversation requiring human assistance"
        
        # Transfer for complex billing or insurance questions
        if intent == 'billing_inquiry' and confidence > 0.7:
            return True, "Billing inquiry requiring specialist assistance"
        
        return False, ""
    
    def generate_conversation_summary(self, conversation_turns: List[Dict]) -> str:
        """Generate a summary of the conversation for CRM logging."""
        if not conversation_turns:
            return "No conversation recorded"
        
        try:
            conversation_text = "\n".join([
                f"{turn['speaker']}: {turn['message']}" 
                for turn in conversation_turns
            ])
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """Summarize this phone conversation between a patient and AI receptionist. 
                        Include: patient's main request, any appointments scheduled, information provided, 
                        and next steps. Keep it concise and professional."""
                    },
                    {"role": "user", "content": conversation_text}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating conversation summary: {e}")
            return f"Conversation with {len(conversation_turns)} exchanges - summary generation failed"

