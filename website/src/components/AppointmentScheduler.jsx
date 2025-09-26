import React, { useState } from 'react';
import { Button } from '@/components/ui/button.jsx';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Input } from '@/components/ui/input.jsx';
import { Textarea } from '@/components/ui/textarea.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import { buildCrmApiUrl, getCrmApiBaseUrlCandidates } from '@/lib/api.js';
import { buildCrmApiUrl } from '@/lib/api.js';
import { 
  Calendar, 
  Clock, 
  User, 
  Phone, 
  Mail, 
  CheckCircle, 
  ArrowLeft,
  ArrowRight,
  CalendarDays,
  Stethoscope,
  Brain,
  Heart,
  Zap,
  Activity,
  Shield
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_CRM_API_URL || 'http://localhost:5001/api';

const AppointmentScheduler = ({ isOpen, onClose }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedService, setSelectedService] = useState(null);
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedTime, setSelectedTime] = useState(null);
  const [patientInfo, setPatientInfo] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    dateOfBirth: '',
    reason: '',
    insurance: '',
    preferredContact: 'phone'
  });
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const services = [
    {
      id: 'psychiatry',
      name: 'Psychiatry & Mental Health',
      duration: '60 minutes',
      price: '$250',
      icon: <Brain className="w-6 h-6 text-blue-600" />,
      description: 'Comprehensive mental health evaluation and treatment planning',
      preparation: 'Please complete intake forms 24 hours before your appointment'
    },
    {
      id: 'hormone',
      name: 'Hormone Optimization Consultation',
      duration: '45 minutes',
      price: '$200',
      icon: <Zap className="w-6 h-6 text-green-600" />,
      description: 'Initial consultation for hormone replacement therapy',
      preparation: 'Fasting lab work may be required before your visit'
    },
    {
      id: 'weight-loss',
      name: 'Medical Weight Loss Consultation',
      duration: '45 minutes',
      price: '$175',
      icon: <Heart className="w-6 h-6 text-red-600" />,
      description: 'Comprehensive weight loss evaluation and program planning',
      preparation: 'Please bring current medications and recent lab results'
    },
    {
      id: 'peptide',
      name: 'Peptide Therapy Consultation',
      duration: '30 minutes',
      price: '$150',
      icon: <Activity className="w-6 h-6 text-purple-600" />,
      description: 'Evaluation for peptide therapy protocols',
      preparation: 'Health history review and goal assessment'
    },
    {
      id: 'iv-therapy',
      name: 'IV Therapy Session',
      duration: '90 minutes',
      price: '$125',
      icon: <Stethoscope className="w-6 h-6 text-teal-600" />,
      description: 'Intravenous nutrient therapy treatment',
      preparation: 'Please eat a light meal before your appointment'
    },
    {
      id: 'wellness',
      name: 'Wellness Consultation',
      duration: '60 minutes',
      price: '$200',
      icon: <Shield className="w-6 h-6 text-orange-600" />,
      description: 'Comprehensive health optimization assessment',
      preparation: 'Complete health questionnaire and bring recent lab work'
    }
  ];

  // Generate available time slots
  const generateTimeSlots = () => {
    const slots = [];
    const startHour = 8; // 8 AM
    const endHour = 18; // 6 PM
    const interval = 30; // 30-minute intervals

    for (let hour = startHour; hour < endHour; hour++) {
      for (let minute = 0; minute < 60; minute += interval) {
        const time = new Date();
        time.setHours(hour, minute, 0, 0);
        const value = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;
        const label = time.toLocaleTimeString('en-US', {
          hour: 'numeric',
          minute: '2-digit',
          hour12: true
        });
        slots.push({ value, label });
      }
    }
    return slots;
  };

  // Generate calendar days for the current month
  const generateCalendarDays = () => {
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());
    
    const days = [];
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    for (let i = 0; i < 42; i++) {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + i);
      
      const isCurrentMonth = date.getMonth() === month;
      const isPast = date < today;
      const isWeekend = date.getDay() === 0 || date.getDay() === 6;
      const isAvailable = isCurrentMonth && !isPast && !isWeekend;
      
      days.push({
        date: date,
        day: date.getDate(),
        isCurrentMonth,
        isPast,
        isWeekend,
        isAvailable,
        isSelected: selectedDate && date.toDateString() === selectedDate.toDateString()
      });
    }
    
    return days;
  };

  const handleServiceSelect = (service) => {
    setSelectedService(service);
    setCurrentStep(2);
  };

  const handleDateSelect = (day) => {
    if (day.isAvailable) {
      setSelectedDate(day.date);
      setCurrentStep(3);
    }
  };

  const handleTimeSelect = (time) => {
    setSelectedTime(time);
    setCurrentStep(4);
  };

  const handleInputChange = (field, value) => {
    setPatientInfo(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      // Prepare data for CRM API
      const requestData = {
        firstName: patientInfo.firstName,
        lastName: patientInfo.lastName,
        email: patientInfo.email,
        phone: patientInfo.phone,
        dateOfBirth: patientInfo.dateOfBirth,
        insurance: patientInfo.insurance,
        preferredContact: patientInfo.preferredContact,
        serviceType: selectedService.id,
        preferredDate: selectedDate.toISOString().split('T')[0],
        preferredTime: selectedTime?.value,
        reason: patientInfo.reason,
        priority: 'normal'
      };


      const attemptedEndpoints = new Set();
      const candidateEndpoints = [
        ...getCrmApiBaseUrlCandidates().map((base) => `${base}/consultation-requests`),
        buildCrmApiUrl('/consultation-requests'),
        '/api/consultation-requests'
      ].filter(Boolean);

      let lastError;

      for (const endpoint of candidateEndpoints) {
        if (attemptedEndpoints.has(endpoint)) {
          continue;
        }

        attemptedEndpoints.add(endpoint);

        try {
          const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
          });

          if (!response.ok) {
            const errorText = await response.text();
            lastError = new Error(`Request failed: ${response.status} ${errorText}`);
            continue;
          }

          const result = await response.json();

          if (result?.success) {
            setIsSubmitting(false);
            setIsSubmitted(true);
            return;
          }

          lastError = new Error(result?.error || 'Failed to submit consultation request');
        } catch (fetchError) {
          lastError = fetchError;
        }
      }

      if (lastError) {
        throw lastError;
=======
      // Submit to CRM API
      const response = await fetch(buildCrmApiUrl('/consultation-requests'), {
      const response = await fetch(`${API_BASE_URL}/consultation-requests`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Request failed: ${response.status} ${errorText}`);
      }

      const result = await response.json();
      
      if (result.success) {
        setIsSubmitting(false);
        setIsSubmitted(true);
      } else {
        throw new Error(result.error || 'Failed to submit consultation request');

      }

      throw new Error('Unable to submit consultation request. No CRM endpoints responded successfully.');
    } catch (error) {
      console.error('Error submitting consultation request:', error);
      setIsSubmitting(false);
      // You might want to show an error message to the user here
      alert('There was an error submitting your request. Please try again or call us at (484) 357-1916.');
    }
  };

  const nextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1));
  };

  const prevMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1));
  };

  const resetScheduler = () => {
    setCurrentStep(1);
    setSelectedService(null);
    setSelectedDate(null);
    setSelectedTime(null);
    setPatientInfo({
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
      dateOfBirth: '',
      reason: '',
      insurance: '',
      preferredContact: 'phone'
    });
    setIsSubmitted(false);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Request Your Appointment</h2>
              <p className="text-gray-600">Submit your consultation request - we'll contact you to confirm details</p>
            </div>
            <Button variant="outline" onClick={onClose}>
              ✕
            </Button>
          </div>

          {/* Progress Indicator */}
          {!isSubmitted && (
            <div className="flex items-center justify-center mb-8">
              {[1, 2, 3, 4].map((step) => (
                <div key={step} className="flex items-center">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                    currentStep >= step 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-200 text-gray-600'
                  }`}>
                    {step}
                  </div>
                  {step < 4 && (
                    <div className={`w-12 h-1 mx-2 ${
                      currentStep > step ? 'bg-blue-600' : 'bg-gray-200'
                    }`} />
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Step Content */}
          {isSubmitted ? (
            // Confirmation Screen
            <div className="text-center py-12">
              <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Consultation Request Submitted!</h3>
              <p className="text-gray-600 mb-6">
                Thank you for your consultation request. Our team will contact you within 24 hours to confirm your appointment details and answer any questions.
              </p>
              
              <Card className="max-w-md mx-auto mb-6">
                <CardHeader>
                  <CardTitle className="text-lg">Requested Appointment Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-left">
                  <div className="flex justify-between">
                    <span className="font-medium">Service:</span>
                    <span>{selectedService?.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Date:</span>
                    <span>{selectedDate?.toLocaleDateString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Time:</span>
                    <span>{selectedTime?.label}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Duration:</span>
                    <span>{selectedService?.duration}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Investment:</span>
                    <span>{selectedService?.price}</span>
                  </div>
                </CardContent>
              </Card>

              <div className="space-y-3">
                <Button onClick={resetScheduler} className="bg-blue-600 hover:bg-blue-700">
                  Request Another Consultation
                </Button>
                <Button variant="outline" onClick={onClose}>
                  Close
                </Button>
              </div>
            </div>
          ) : currentStep === 1 ? (
            // Service Selection
            <div>
              <h3 className="text-xl font-semibold mb-4">Select Your Service</h3>
              <div className="grid md:grid-cols-2 gap-4">
                {services.map((service) => (
                  <Card 
                    key={service.id} 
                    className="cursor-pointer hover:shadow-lg transition-shadow"
                    onClick={() => handleServiceSelect(service)}
                  >
                    <CardHeader>
                      <div className="flex items-center mb-2">
                        {service.icon}
                        <CardTitle className="ml-3 text-lg">{service.name}</CardTitle>
                      </div>
                      <div className="flex gap-2">
                        <Badge variant="secondary">{service.duration}</Badge>
                        <Badge variant="outline">{service.price}</Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <CardDescription className="mb-2">
                        {service.description}
                      </CardDescription>
                      <p className="text-xs text-gray-500">
                        <strong>Preparation:</strong> {service.preparation}
                      </p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          ) : currentStep === 2 ? (
            // Date Selection
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold">Select Date</h3>
                <Button variant="outline" onClick={() => setCurrentStep(1)}>
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back
                </Button>
              </div>
              
              <Card className="mb-4">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-4">
                    <Button variant="outline" size="sm" onClick={prevMonth}>
                      <ArrowLeft className="w-4 h-4" />
                    </Button>
                    <h4 className="text-lg font-semibold">
                      {currentMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                    </h4>
                    <Button variant="outline" size="sm" onClick={nextMonth}>
                      <ArrowRight className="w-4 h-4" />
                    </Button>
                  </div>
                  
                  <div className="grid grid-cols-7 gap-1 mb-2">
                    {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                      <div key={day} className="p-2 text-center text-sm font-medium text-gray-500">
                        {day}
                      </div>
                    ))}
                  </div>
                  
                  <div className="grid grid-cols-7 gap-1">
                    {generateCalendarDays().map((day, index) => (
                      <button
                        key={index}
                        onClick={() => handleDateSelect(day)}
                        disabled={!day.isAvailable}
                        className={`p-2 text-sm rounded-md transition-colors ${
                          day.isSelected
                            ? 'bg-blue-600 text-white'
                            : day.isAvailable
                            ? 'hover:bg-blue-50 text-gray-900'
                            : day.isCurrentMonth
                            ? 'text-gray-400 cursor-not-allowed'
                            : 'text-gray-300 cursor-not-allowed'
                        }`}
                      >
                        {day.day}
                      </button>
                    ))}
                  </div>
                  
                  <div className="mt-4 text-xs text-gray-500">
                    <p>• Available appointments: Monday - Friday</p>
                    <p>• Weekend appointments available by special request</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : currentStep === 3 ? (
            // Time Selection
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold">Select Time</h3>
                <Button variant="outline" onClick={() => setCurrentStep(2)}>
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back
                </Button>
              </div>
              
              <Card className="mb-4">
                <CardHeader>
                  <CardTitle className="text-lg">
                    {selectedDate?.toLocaleDateString('en-US', { 
                      weekday: 'long', 
                      year: 'numeric', 
                      month: 'long', 
                      day: 'numeric' 
                    })}
                  </CardTitle>
                  <CardDescription>
                    {selectedService?.name} • {selectedService?.duration}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-3 md:grid-cols-4 gap-2">
                    {generateTimeSlots().map((time) => (
                      <Button
                        key={time.value}
                        variant={selectedTime?.value === time.value ? "default" : "outline"}
                        size="sm"
                        onClick={() => handleTimeSelect(time)}
                        className="text-sm"
                      >
                        {time.label}
                      </Button>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            // Patient Information
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold">Your Information</h3>
                <Button variant="outline" onClick={() => setCurrentStep(3)}>
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back
                </Button>
              </div>
              
              <form onSubmit={handleSubmit} className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Appointment Summary</CardTitle>
                    <CardDescription className="text-sm text-blue-600">
                      <strong>Note:</strong> This is a consultation request. Our team will contact you to confirm the final appointment time and provide any additional instructions.
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="flex justify-between">
                      <span className="font-medium">Service:</span>
                      <span>{selectedService?.name}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">Date & Time:</span>
                      <span>
                        {selectedDate?.toLocaleDateString()} at {selectedTime?.label}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">Investment:</span>
                      <span className="font-semibold">{selectedService?.price}</span>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Personal Information</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-1">First Name *</label>
                        <Input
                          required
                          value={patientInfo.firstName}
                          onChange={(e) => handleInputChange('firstName', e.target.value)}
                          placeholder="John"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1">Last Name *</label>
                        <Input
                          required
                          value={patientInfo.lastName}
                          onChange={(e) => handleInputChange('lastName', e.target.value)}
                          placeholder="Smith"
                        />
                      </div>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium mb-1">Email *</label>
                      <Input
                        type="email"
                        required
                        value={patientInfo.email}
                        onChange={(e) => handleInputChange('email', e.target.value)}
                        placeholder="john.smith@email.com"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium mb-1">Phone Number *</label>
                      <Input
                        type="tel"
                        required
                        value={patientInfo.phone}
                        onChange={(e) => handleInputChange('phone', e.target.value)}
                        placeholder="(484) 555-0123"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium mb-1">Date of Birth</label>
                      <Input
                        type="date"
                        value={patientInfo.dateOfBirth}
                        onChange={(e) => handleInputChange('dateOfBirth', e.target.value)}
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium mb-1">Insurance Provider</label>
                      <Input
                        value={patientInfo.insurance}
                        onChange={(e) => handleInputChange('insurance', e.target.value)}
                        placeholder="Blue Cross Blue Shield, Aetna, etc."
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium mb-1">Reason for Visit</label>
                      <Textarea
                        value={patientInfo.reason}
                        onChange={(e) => handleInputChange('reason', e.target.value)}
                        placeholder="Please describe your health goals or concerns..."
                        rows={3}
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium mb-1">Preferred Contact Method</label>
                      <select
                        value={patientInfo.preferredContact}
                        onChange={(e) => handleInputChange('preferredContact', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="phone">Phone</option>
                        <option value="email">Email</option>
                        <option value="text">Text Message</option>
                      </select>
                    </div>
                  </CardContent>
                </Card>

                <div className="flex gap-4">
                  <Button
                    type="submit"
                    disabled={isSubmitting}
                    className="flex-1 bg-blue-600 hover:bg-blue-700"
                  >
                    {isSubmitting ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Submitting Request...
                      </>
                    ) : (
                      <>
                        <Calendar className="w-4 h-4 mr-2" />
                        Submit Consultation Request
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AppointmentScheduler;

