import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button.jsx';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import { Input } from '@/components/ui/input.jsx';
import { buildCrmApiUrl } from '@/lib/api.js';
import { 
  Calendar, 
  Clock, 
  User, 
  Phone, 
  Mail, 
  CheckCircle, 
  AlertCircle,
  Users,
  CalendarDays,
  MessageSquare,
  TrendingUp,
  Search,
  Eye,
  Check,
  X
} from 'lucide-react';

const AdminDashboard = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState({});
  const [consultationRequests, setConsultationRequests] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('pending');

  useEffect(() => {
    if (isOpen) {
      fetchDashboardData();
    }
  }, [isOpen]);

  const fetchDashboardData = async (currentStatus = statusFilter) => {
    try {
      setLoading(true);

      // Fetch dashboard stats
      const statsResponse = await fetch(buildCrmApiUrl('/dashboard/stats'));
      const statsData = await statsResponse.json();
      if (statsData.success) {
        setStats(statsData.stats);
      }

      // Fetch consultation requests
      const requestsResponse = await fetch(buildCrmApiUrl(`/consultation-requests?status=${currentStatus}`));
      const requestsData = await requestsResponse.json();
      if (requestsData.success) {
        setConsultationRequests(requestsData.consultation_requests);
      }

      // Fetch today's appointments
      const today = new Date().toISOString().split('T')[0];
      const appointmentsResponse = await fetch(buildCrmApiUrl(`/appointments?start_date=${today}&end_date=${today}`));
      const appointmentsData = await appointmentsResponse.json();
      if (appointmentsData.success) {
        setAppointments(appointmentsData.appointments);
      }
      
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmRequest = async (requestId) => {
    try {
      const response = await fetch(buildCrmApiUrl(`/consultation-requests/${requestId}/confirm`), {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          confirmedDate: '2025-09-10', // This would come from a date picker
          confirmedTime: '10:00',
          duration: 60,
          provider: 'Dr. Smith'
        })
      });
      
      const result = await response.json();
      if (result.success) {
        fetchDashboardData(); // Refresh data
      }
    } catch (error) {
      console.error('Error confirming request:', error);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatTime = (timeString) => {
    return new Date(`2000-01-01T${timeString}`).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const getServiceBadgeColor = (serviceType) => {
    const colors = {
      'psychiatry': 'bg-blue-100 text-blue-800',
      'hormone': 'bg-green-100 text-green-800',
      'weight-loss': 'bg-red-100 text-red-800',
      'peptide': 'bg-purple-100 text-purple-800',
      'iv-therapy': 'bg-teal-100 text-teal-800',
      'wellness': 'bg-orange-100 text-orange-800'
    };
    return colors[serviceType] || 'bg-gray-100 text-gray-800';
  };

  const getStatusBadgeColor = (status) => {
    const colors = {
      'pending': 'bg-yellow-100 text-yellow-800',
      'confirmed': 'bg-green-100 text-green-800',
      'scheduled': 'bg-blue-100 text-blue-800',
      'completed': 'bg-gray-100 text-gray-800',
      'cancelled': 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-7xl w-full max-h-[95vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">CRM Dashboard</h2>
            <p className="text-gray-600">Lehigh Valley Wellness Practice Management</p>
          </div>
          <Button variant="outline" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>

        {/* Navigation Tabs */}
        <div className="flex border-b">
          {[
            { id: 'dashboard', label: 'Dashboard', icon: TrendingUp },
            { id: 'requests', label: 'Consultation Requests', icon: MessageSquare },
            { id: 'appointments', label: 'Appointments', icon: CalendarDays },
            { id: 'patients', label: 'Patients', icon: Users }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <tab.icon className="w-4 h-4 mr-2" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <>
              {activeTab === 'dashboard' && (
                <div className="space-y-6">
                  {/* Stats Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Today's Appointments</CardTitle>
                        <CalendarDays className="h-4 w-4 text-muted-foreground" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{stats.todays_appointments || 0}</div>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Pending Requests</CardTitle>
                        <AlertCircle className="h-4 w-4 text-muted-foreground" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{stats.pending_requests || 0}</div>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Patients</CardTitle>
                        <Users className="h-4 w-4 text-muted-foreground" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{stats.total_patients || 0}</div>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">This Week</CardTitle>
                        <TrendingUp className="h-4 w-4 text-muted-foreground" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{stats.weekly_appointments || 0}</div>
                      </CardContent>
                    </Card>
                  </div>

                  {/* Recent Activity */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <Card>
                      <CardHeader>
                        <CardTitle>Today's Appointments</CardTitle>
                      </CardHeader>
                      <CardContent>
                        {appointments.length === 0 ? (
                          <p className="text-gray-500 text-center py-4">No appointments today</p>
                        ) : (
                          <div className="space-y-3">
                            {appointments.slice(0, 5).map((appointment) => (
                              <div key={appointment.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                <div>
                                  <p className="font-medium">{appointment.patient_name}</p>
                                  <p className="text-sm text-gray-600">{appointment.service_type}</p>
                                </div>
                                <div className="text-right">
                                  <p className="text-sm font-medium">{formatTime(appointment.appointment_time)}</p>
                                  <Badge className={getStatusBadgeColor(appointment.status)}>
                                    {appointment.status}
                                  </Badge>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader>
                        <CardTitle>Recent Consultation Requests</CardTitle>
                      </CardHeader>
                      <CardContent>
                        {consultationRequests.length === 0 ? (
                          <p className="text-gray-500 text-center py-4">No pending requests</p>
                        ) : (
                          <div className="space-y-3">
                            {consultationRequests.slice(0, 5).map((request) => (
                              <div key={request.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                <div>
                                  <p className="font-medium">{request.patient_name}</p>
                                  <p className="text-sm text-gray-600">{request.service_type}</p>
                                </div>
                                <div className="text-right">
                                  <p className="text-sm text-gray-600">{formatDate(request.created_at)}</p>
                                  <Badge className={getStatusBadgeColor(request.status)}>
                                    {request.status}
                                  </Badge>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </div>
                </div>
              )}

              {activeTab === 'requests' && (
                <div className="space-y-6">
                  {/* Filters */}
                  <div className="flex gap-4">
                    <div className="flex-1">
                      <Input
                        placeholder="Search requests..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="max-w-sm"
                      />
                    </div>
                    <select
                      value={statusFilter}
                      onChange={(e) => {
                        const newStatus = e.target.value;
                        setStatusFilter(newStatus);
                        fetchDashboardData(newStatus);
                      }}
                      className="px-3 py-2 border border-gray-300 rounded-md"
                    >
                      <option value="pending">Pending</option>
                      <option value="confirmed">Confirmed</option>
                      <option value="all">All</option>
                    </select>
                  </div>

                  {/* Requests List */}
                  <div className="space-y-4">
                    {consultationRequests.map((request) => (
                      <Card key={request.id}>
                        <CardContent className="p-6">
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-4 mb-2">
                                <h3 className="text-lg font-semibold">{request.patient_name}</h3>
                                <Badge className={getServiceBadgeColor(request.service_type)}>
                                  {request.service_type}
                                </Badge>
                                <Badge className={getStatusBadgeColor(request.status)}>
                                  {request.status}
                                </Badge>
                              </div>
                              
                              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
                                <div>
                                  <span className="font-medium">Preferred Date:</span>
                                  <p>{request.preferred_date ? formatDate(request.preferred_date) : 'Not specified'}</p>
                                </div>
                                <div>
                                  <span className="font-medium">Preferred Time:</span>
                                  <p>{request.preferred_time ? formatTime(request.preferred_time) : 'Not specified'}</p>
                                </div>
                                <div>
                                  <span className="font-medium">Requested:</span>
                                  <p>{formatDate(request.created_at)}</p>
                                </div>
                                <div>
                                  <span className="font-medium">Priority:</span>
                                  <p className="capitalize">{request.priority}</p>
                                </div>
                              </div>
                              
                              {request.reason_for_visit && (
                                <div className="mt-3">
                                  <span className="font-medium text-sm">Reason for Visit:</span>
                                  <p className="text-sm text-gray-600 mt-1">{request.reason_for_visit}</p>
                                </div>
                              )}
                            </div>
                            
                            <div className="flex gap-2 ml-4">
                              {request.status === 'pending' && (
                                <Button
                                  size="sm"
                                  onClick={() => handleConfirmRequest(request.id)}
                                  className="bg-green-600 hover:bg-green-700"
                                >
                                  <Check className="w-4 h-4 mr-1" />
                                  Confirm
                                </Button>
                              )}
                              <Button variant="outline" size="sm">
                                <Eye className="w-4 h-4 mr-1" />
                                View
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'appointments' && (
                <div className="space-y-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Upcoming Appointments</CardTitle>
                      <CardDescription>Manage scheduled appointments</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-500 text-center py-8">Appointment management interface coming soon...</p>
                    </CardContent>
                  </Card>
                </div>
              )}

              {activeTab === 'patients' && (
                <div className="space-y-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Patient Management</CardTitle>
                      <CardDescription>View and manage patient records</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-500 text-center py-8">Patient management interface coming soon...</p>
                    </CardContent>
                  </Card>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;

