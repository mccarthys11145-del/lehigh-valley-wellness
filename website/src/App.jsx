import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button.jsx';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import { Input } from '@/components/ui/input.jsx';
import { Textarea } from '@/components/ui/textarea.jsx';
import AppointmentScheduler from './components/AppointmentScheduler.jsx';
import AdminDashboard from './components/AdminDashboard.jsx';
import AdminLogin from './components/AdminLogin.jsx';
import ChatWidget from './components/ChatWidget.jsx';
import { 
  Phone, 
  Mail, 
  MapPin, 
  Clock, 
  Star, 
  Heart, 
  Brain, 
  Zap, 
  Shield, 
  Users, 
  Calendar,
  CheckCircle,
  ArrowRight,
  Stethoscope,
  Activity,
  Award,
  Menu,
  X,
  Settings
} from 'lucide-react';
import './App.css';

function App() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [activeSection, setActiveSection] = useState('home');
  const [isSchedulerOpen, setIsSchedulerOpen] = useState(false);
  const [isAdminOpen, setIsAdminOpen] = useState(false);
  const [isAdminAuthenticated, setIsAdminAuthenticated] = useState(false);
  const [showAdminLogin, setShowAdminLogin] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const sections = ['home', 'about', 'services', 'why-choose', 'testimonials', 'contact'];
      const scrollPosition = window.scrollY + 100;

      for (const section of sections) {
        const element = document.getElementById(section);
        if (element && scrollPosition >= element.offsetTop && scrollPosition < element.offsetTop + element.offsetHeight) {
          setActiveSection(section);
          break;
        }
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
    setIsMenuOpen(false);
  };

  const services = [
    {
      icon: <Brain className="w-8 h-8 text-blue-600" />,
      title: "Psychiatry & Mental Health",
      description: "Comprehensive mental health care including therapy, counseling, and psychiatric evaluations without controlled substances.",
      features: ["Individual Therapy", "Cognitive Behavioral Therapy", "Anxiety & Depression Treatment", "Telehealth Available"]
    },
    {
      icon: <Zap className="w-8 h-8 text-green-600" />,
      title: "Hormone Optimization",
      description: "Advanced hormone replacement therapy and optimization for both men and women using safe, effective protocols.",
      features: ["Testosterone Therapy", "Bio-Identical Hormones", "Comprehensive Testing", "Ongoing Monitoring"]
    },
    {
      icon: <Heart className="w-8 h-8 text-red-600" />,
      title: "Medical Weight Loss",
      description: "Physician-supervised weight loss programs with personalized nutrition and lifestyle coaching.",
      features: ["Semaglutide Programs", "Nutritional Counseling", "Metabolic Testing", "Lifestyle Coaching"]
    },
    {
      icon: <Activity className="w-8 h-8 text-purple-600" />,
      title: "Peptide Therapy",
      description: "FDA-approved peptide treatments for anti-aging, recovery, and wellness optimization.",
      features: ["Anti-Aging Peptides", "Recovery Enhancement", "Immune Support", "Performance Optimization"]
    },
    {
      icon: <Stethoscope className="w-8 h-8 text-teal-600" />,
      title: "IV Therapy",
      description: "Intravenous nutrient therapy for energy, immunity, and overall wellness enhancement.",
      features: ["Energy Boost", "Immune Support", "Athletic Recovery", "Hangover Relief"]
    },
    {
      icon: <Shield className="w-8 h-8 text-orange-600" />,
      title: "Wellness Consultations",
      description: "Comprehensive wellness assessments and personalized optimization plans for peak health.",
      features: ["Health Assessments", "Preventive Care", "Lifestyle Optimization", "Supplement Guidance"]
    }
  ];

  const testimonials = [
    {
      name: "Sarah M.",
      rating: 5,
      text: "The hormone optimization program completely changed my life. I have energy I haven't felt in years!"
    },
    {
      name: "Michael R.",
      rating: 5,
      text: "Professional, caring staff and cutting-edge treatments. The weight loss program exceeded my expectations."
    },
    {
      name: "Jennifer L.",
      rating: 5,
      text: "Finally found a practice that focuses on wellness, not just treating illness. Highly recommend!"
    }
  ];

  const whyChooseUs = [
    {
      icon: <Award className="w-6 h-6 text-blue-600" />,
      title: "Expert Medical Team",
      description: "Board-certified physicians with specialized training in wellness and optimization medicine."
    },
    {
      icon: <Shield className="w-6 h-6 text-green-600" />,
      title: "Safe & Effective",
      description: "All treatments are FDA-approved and follow the highest safety standards and protocols."
    },
    {
      icon: <Users className="w-6 h-6 text-purple-600" />,
      title: "Personalized Care",
      description: "Individualized treatment plans tailored to your unique health goals and needs."
    },
    {
      icon: <Zap className="w-6 h-6 text-orange-600" />,
      title: "Advanced Technology",
      description: "State-of-the-art equipment and cutting-edge treatment protocols for optimal results."
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/95 backdrop-blur-sm border-b border-gray-200 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-blue-600">Lehigh Valley Wellness</h1>
              </div>
            </div>
            
            {/* Desktop Navigation */}
            <div className="hidden md:block">
              <div className="hidden md:flex items-center space-x-8">
                {['home', 'about', 'services', 'why-choose', 'testimonials', 'contact'].map((section) => (
                  <button
                    key={section}
                    onClick={() => scrollToSection(section)}
                    className={`text-sm font-medium transition-colors ${
                      activeSection === section ? 'text-blue-600' : 'text-gray-700 hover:text-blue-600'
                    }`}
                  >
                    {section.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                  </button>
                ))}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    if (isAdminAuthenticated) {
                      setIsAdminOpen(true);
                    } else {
                      setShowAdminLogin(true);
                    }
                  }}
                  className="text-gray-600 hover:text-blue-600"
                >
                  <Settings className="w-4 h-4 mr-1" />
                  Admin
                </Button>
              </div>
            </div>

            {/* Mobile menu button */}
            <div className="md:hidden">
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="inline-flex items-center justify-center p-2 rounded-md text-gray-700 hover:text-blue-600 hover:bg-gray-100"
              >
                {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-white border-t border-gray-200">
              {['Home', 'About', 'Services', 'Why Choose Us', 'Testimonials', 'Contact'].map((item) => (
                <button
                  key={item}
                  onClick={() => scrollToSection(item.toLowerCase().replace(' ', '-'))}
                  className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50 w-full text-left"
                >
                  {item}
                </button>
              ))}
              <button
                onClick={() => {
                  if (isAdminAuthenticated) {
                    setIsAdminOpen(true);
                  } else {
                    setShowAdminLogin(true);
                  }
                  setIsMenuOpen(false);
                }}
                className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50 w-full text-left"
              >
                <Settings className="w-4 h-4 mr-2 inline" />
                Admin
              </button>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section id="home" className="pt-16 bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              Optimize Your Health,
              <span className="text-blue-600"> Transform Your Life</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Lehigh Valley's premier wellness center offering cutting-edge hormone optimization, 
              medical weight loss, mental health services, and advanced wellness treatments.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button 
                size="lg" 
                onClick={() => setIsSchedulerOpen(true)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 text-lg"
              >
                Request Consultation
                <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
              <Button 
                variant="outline" 
                size="lg"
                onClick={() => scrollToSection('services')}
                className="border-blue-600 text-blue-600 hover:bg-blue-50 px-8 py-3 text-lg"
              >
                Explore Services
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              About Lehigh Valley Wellness
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              We're dedicated to helping you achieve optimal health through personalized, 
              evidence-based wellness treatments and cutting-edge medical care.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-6">Our Mission</h3>
              <p className="text-gray-600 mb-6">
                At Lehigh Valley Wellness, we believe in treating the whole person, not just symptoms. 
                Our comprehensive approach combines traditional medicine with innovative wellness therapies 
                to help you achieve peak health and vitality.
              </p>
              <div className="space-y-4">
                <div className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-600 mr-3" />
                  <span className="text-gray-700">Board-certified medical professionals</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-600 mr-3" />
                  <span className="text-gray-700">Personalized treatment plans</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-600 mr-3" />
                  <span className="text-gray-700">State-of-the-art facilities</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-600 mr-3" />
                  <span className="text-gray-700">Comprehensive wellness approach</span>
                </div>
              </div>
            </div>
            <div className="bg-gradient-to-br from-blue-50 to-indigo-100 p-8 rounded-2xl">
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 text-white rounded-full mb-4">
                  <Heart className="w-8 h-8" />
                </div>
                <h4 className="text-xl font-bold text-gray-900 mb-2">Patient-Centered Care</h4>
                <p className="text-gray-600">
                  Every treatment plan is customized to your unique health goals, 
                  lifestyle, and medical history for optimal results.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section id="services" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Our Services
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Comprehensive wellness solutions designed to optimize your health and enhance your quality of life.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {services.map((service, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow duration-300">
                <CardHeader>
                  <div className="flex items-center mb-4">
                    {service.icon}
                    <CardTitle className="ml-3 text-xl">{service.title}</CardTitle>
                  </div>
                  <CardDescription className="text-gray-600">
                    {service.description}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {service.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-center text-sm text-gray-600">
                        <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Why Choose Us Section */}
      <section id="why-choose" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Why Choose Lehigh Valley Wellness?
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Experience the difference of personalized, cutting-edge wellness care.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {whyChooseUs.map((item, index) => (
              <div key={index} className="text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 bg-gray-100 rounded-full mb-4">
                  {item.icon}
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{item.title}</h3>
                <p className="text-gray-600">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              What Our Patients Say
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Real stories from real patients who have transformed their health with us.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="text-center">
                <CardContent className="pt-6">
                  <div className="flex justify-center mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                    ))}
                  </div>
                  <p className="text-gray-600 mb-4 italic">"{testimonial.text}"</p>
                  <p className="font-semibold text-gray-900">- {testimonial.name}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-20 bg-blue-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Ready to Transform Your Health?
            </h2>
            <p className="text-xl text-blue-100 max-w-3xl mx-auto">
              Request your consultation today and take the first step toward optimal wellness.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-12">
            {/* Contact Info */}
            <div>
              <h3 className="text-2xl font-bold mb-6">Get in Touch</h3>
              <div className="space-y-4">
                <div className="flex items-center">
                  <Phone className="w-6 h-6 text-blue-300 mr-4" />
                  <div>
                    <p className="font-semibold">Phone</p>
                    <p className="text-blue-100">(484) 357-1916</p>
                  </div>
                </div>
                <div className="flex items-center">
                  <Mail className="w-6 h-6 text-blue-300 mr-4" />
                  <div>
                    <p className="font-semibold">Email</p>
                    <p className="text-blue-100">info@lehighvalleywellness.org</p>
                  </div>
                </div>
                <div className="flex items-center">
                  <MapPin className="w-6 h-6 text-blue-300 mr-4" />
                  <div>
                    <p className="font-semibold">Location</p>
                    <p className="text-blue-100">Lehigh Valley, PA</p>
                  </div>
                </div>
                <div className="flex items-center">
                  <Clock className="w-6 h-6 text-blue-300 mr-4" />
                  <div>
                    <p className="font-semibold">Hours</p>
                    <p className="text-blue-100">Mon-Fri: 8AM-6PM</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Contact Form */}
            <div>
              <Card className="bg-white text-gray-900">
                <CardHeader>
                  <CardTitle>Request Your Consultation</CardTitle>
                  <CardDescription>
                    Fill out the form below and we'll contact you within 24 hours to confirm your appointment.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <Input placeholder="First Name" />
                      <Input placeholder="Last Name" />
                    </div>
                    <Input placeholder="Email" type="email" />
                    <Input placeholder="Phone" type="tel" />
                    <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                      <option value="">Select Service Interest</option>
                      <option value="hormone">Hormone Optimization</option>
                      <option value="weight-loss">Medical Weight Loss</option>
                      <option value="psychiatry">Psychiatry & Mental Health</option>
                      <option value="peptide">Peptide Therapy</option>
                      <option value="iv">IV Therapy</option>
                      <option value="wellness">Wellness Consultation</option>
                    </select>
                    <Textarea placeholder="Tell us about your health goals..." rows={4} />
                    <Button className="w-full bg-blue-600 hover:bg-blue-700" onClick={() => setIsSchedulerOpen(true)}>
                      Request Consultation
                      <Calendar className="ml-2 w-4 h-4" />
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-xl font-bold mb-4">Lehigh Valley Wellness</h3>
              <p className="text-gray-400 mb-4">
                Your premier destination for comprehensive wellness and optimization medicine.
              </p>
              <div className="flex space-x-4">
                <Badge variant="secondary">Board Certified</Badge>
                <Badge variant="secondary">HIPAA Compliant</Badge>
              </div>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Services</h4>
              <ul className="space-y-2 text-gray-400">
                <li>Hormone Optimization</li>
                <li>Medical Weight Loss</li>
                <li>Psychiatry & Mental Health</li>
                <li>Peptide Therapy</li>
                <li>IV Therapy</li>
                <li>Wellness Consultations</li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Quick Links</h4>
              <ul className="space-y-2 text-gray-400">
                <li><button onClick={() => scrollToSection('about')} className="hover:text-white">About Us</button></li>
                <li><button onClick={() => scrollToSection('services')} className="hover:text-white">Services</button></li>
                <li><button onClick={() => scrollToSection('testimonials')} className="hover:text-white">Testimonials</button></li>
                <li><button onClick={() => scrollToSection('contact')} className="hover:text-white">Contact</button></li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Contact Info</h4>
              <ul className="space-y-2 text-gray-400">
                <li>(484) 357-1916</li>
                <li>info@lehighvalleywellness.org</li>
                <li>Lehigh Valley, PA</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Lehigh Valley Wellness. All rights reserved.</p>
          </div>
        </div>
      </footer>

      {/* Appointment Scheduler Modal */}
      <AppointmentScheduler 
        isOpen={isSchedulerOpen} 
        onClose={() => setIsSchedulerOpen(false)} 
      />

      {/* Admin Login Modal */}
      <AdminLogin 
        isOpen={showAdminLogin} 
        onClose={() => setShowAdminLogin(false)}
        onLogin={() => setIsAdminAuthenticated(true)}
      />

      {/* Admin Dashboard Modal */}
      <AdminDashboard 
        isOpen={isAdminOpen} 
        onClose={() => {
          setIsAdminOpen(false);
          // Optional: logout when closing dashboard
          // setIsAdminAuthenticated(false);
        }} 
      />

      {/* Chat Widget */}
      <ChatWidget 
        isOpen={isChatOpen} 
        onClose={() => setIsChatOpen(false)} 
      />

      {/* Floating Chat Button */}
      {!isChatOpen && (
        <button
          onClick={() => setIsChatOpen(true)}
          className="fixed bottom-4 right-4 bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700 transition-all duration-300 hover:scale-110 z-40"
          aria-label="Open chat"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </button>
      )}
    </div>
  );
}

export default App;

