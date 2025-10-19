import React, { useState, useRef, useEffect } from 'react';

const ChatWidget = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'ai',
      message: "Hello! I'm the AI assistant for Lehigh Valley Wellness. I can help you with appointment requests, service information, and answer questions about our wellness programs. How can I assist you today?",
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      message: inputMessage.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setIsTyping(true);

    try {
      // Simulate AI processing
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Process the message with AI
      const aiResponse = await processMessageWithAI(userMessage.message);

      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        message: aiResponse.message,
        timestamp: new Date(),
        intent: aiResponse.intent,
        actions: aiResponse.actions
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error processing message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'ai',
        message: "I apologize, but I'm having trouble processing your request right now. Please try again or call us at (484) 357-1916 for immediate assistance.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setIsTyping(false);
    }
  };

  const processMessageWithAI = async (message) => {
    // Detect intent and generate appropriate response
    const intent = detectIntent(message.toLowerCase());
    
    switch (intent) {
      case 'appointment_scheduling':
        return {
          intent: 'appointment_scheduling',
          message: "I'd be happy to help you request an appointment! We offer several services:\n\n• Psychiatry & Mental Health (60 min - $250)\n• Hormone Optimization (45 min - $200)\n• Medical Weight Loss (45 min - $175)\n• Peptide Therapy (30 min - $150)\n• Wellness Consultation (60 min - $200)\n\nWhich service interests you? You can also use the 'Request Consultation' button on our website to schedule directly.",
          actions: ['show_appointment_form']
        };

      case 'service_information':
        return {
          intent: 'service_information',
          message: "We offer comprehensive wellness services at Lehigh Valley Wellness:\n\n🧠 **Psychiatry & Mental Health** - Comprehensive mental health care including therapy and counseling (without controlled substances)\n\n💪 **Hormone Optimization** - Advanced hormone replacement therapy for both men and women using safe, effective protocols\n\n⚖️ **Medical Weight Loss** - Physician-supervised weight loss programs with personalized nutrition coaching\n\n🧬 **Peptide Therapy** - FDA-approved peptide treatments for anti-aging, recovery, and wellness optimization\n\n🌟 **Wellness Consultation** - Comprehensive wellness assessments and personalized optimization plans\n\nWould you like more details about any specific service?",
          actions: ['show_services']
        };

      case 'hours_location':
        return {
          intent: 'hours_location',
          message: "**Lehigh Valley Wellness**\n📍 6081 Hamilton Blvd Suite 600, Allentown, PA 18106\n📞 Phone: (484) 357-1916\n🌐 Website: lehighvalleywellness.org\n\n**Hours:**\nMonday - Friday: 8:00 AM - 6:00 PM\nWeekends: Closed\n\n**Parking:** Free parking available on-site\n**Accessibility:** Wheelchair accessible facility\n\nIs there anything specific about our location or hours you'd like to know?",
          actions: ['show_contact']
        };

      case 'insurance_payment':
        return {
          intent: 'insurance_payment',
          message: "We accept several insurance plans including:\n• Blue Cross Blue Shield\n• Aetna\n• Cigna\n• United Healthcare\n\n**Note:** Some services like Hormone Optimization and Peptide Therapy are typically not covered by insurance and require direct payment.\n\nFor specific insurance verification and payment options, please call us at (484) 357-1916 or mention your insurance during your consultation request.",
          actions: ['show_insurance']
        };

      case 'greeting':
        return {
          intent: 'greeting',
          message: "Hello! Welcome to Lehigh Valley Wellness. I'm here to help you with:\n\n• Requesting appointments for our wellness services\n• Information about our treatments and programs\n• Practice hours and location details\n• Insurance and payment questions\n\nWhat would you like to know about today?",
          actions: ['show_menu']
        };

      default:
        return {
          intent: 'general_inquiry',
          message: "Thank you for your question! I'm here to help with information about our wellness services, appointment scheduling, and practice details.\n\nFor specific medical questions or urgent matters, please call us directly at (484) 357-1916 to speak with our medical staff.\n\nIs there something specific about our services or practice that I can help you with?",
          actions: ['show_contact']
        };
    }
  };

  const detectIntent = (message) => {
    const appointmentKeywords = ['appointment', 'schedule', 'book', 'consultation', 'visit', 'see doctor', 'meet'];
    const serviceKeywords = ['service', 'treatment', 'therapy', 'hormone', 'weight loss', 'peptide', 'psychiatry', 'wellness'];
    const hoursKeywords = ['hours', 'open', 'closed', 'location', 'address', 'where', 'when', 'time'];
    const insuranceKeywords = ['insurance', 'cost', 'price', 'payment', 'covered', 'accept', 'billing'];
    const greetingKeywords = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'];

    if (greetingKeywords.some(keyword => message.includes(keyword))) {
      return 'greeting';
    } else if (appointmentKeywords.some(keyword => message.includes(keyword))) {
      return 'appointment_scheduling';
    } else if (serviceKeywords.some(keyword => message.includes(keyword))) {
      return 'service_information';
    } else if (hoursKeywords.some(keyword => message.includes(keyword))) {
      return 'hours_location';
    } else if (insuranceKeywords.some(keyword => message.includes(keyword))) {
      return 'insurance_payment';
    } else {
      return 'general_inquiry';
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatMessage = (message) => {
    // Convert markdown-style formatting to HTML
    return message
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/•/g, '•')
      .replace(/\n/g, '<br>');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-4 right-4 w-96 h-[600px] bg-white rounded-lg shadow-2xl border border-gray-200 flex flex-col z-50">
      {/* Header */}
      <div className="bg-blue-600 text-white p-4 rounded-t-lg flex items-center justify-between">
        <div className="flex items-center">
          <div className="w-3 h-3 bg-green-400 rounded-full mr-2 animate-pulse"></div>
          <div>
            <h3 className="font-semibold text-sm">AI Assistant</h3>
            <p className="text-xs opacity-90">Lehigh Valley Wellness</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-white hover:text-gray-200 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] p-3 rounded-lg ${
                message.type === 'user'
                  ? 'bg-blue-600 text-white rounded-br-none'
                  : 'bg-gray-100 text-gray-800 rounded-bl-none'
              }`}
            >
              <div
                className="text-sm whitespace-pre-wrap"
                dangerouslySetInnerHTML={{ __html: formatMessage(message.message) }}
              />
              <div className={`text-xs mt-1 ${message.type === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-800 p-3 rounded-lg rounded-bl-none">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <textarea
            ref={inputRef}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 resize-none border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={1}
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Press Enter to send • For urgent matters, call (484) 357-1916
        </p>
      </div>
    </div>
  );
};

export default ChatWidget;

