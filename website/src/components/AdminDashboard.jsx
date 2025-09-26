import React, { useState, useEffect, useMemo } from 'react';
import { Button } from '@/components/ui/button.jsx';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import { Input } from '@/components/ui/input.jsx';
import { fetchCrmJson } from '@/lib/api.js';
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
  const [error, setError] = useState(null);
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
      setError(null);

      const today = new Date().toISOString().split('T')[0];

      const [statsResult, requestsResult, appointmentsResult, patientsResult] = await Promise.all([
        fetchCrmJson('/dashboard/stats').catch((err) => ({ error: err })),
        fetchCrmJson(`/consultation-requests?status=${currentStatus}`).catch((err) => ({ error: err })),
        fetchCrmJson(`/appointments?start_date=${today}&end_date=${today}`).catch((err) => ({ error: err })),
        fetchCrmJson('/patients').catch((err) => ({ error: err }))
      ]);

      if (statsResult?.error) {
        throw statsResult.error;
      }

      const statsData = statsResult?.data ?? statsResult;
      if (statsData?.success) {
        setStats(statsData.stats || {});
      } else {
        setStats(statsData || {});
      }

      if (!requestsResult?.error) {
        const requestsData = requestsResult?.data ?? requestsResult;
        setConsultationRequests(requestsData?.consultation_requests ?? requestsData ?? []);
      }

      if (!appointmentsResult?.error) {
        const appointmentsData = appointmentsResult?.data ?? appointmentsResult;
        setAppointments(appointmentsData?.appointments ?? appointmentsData ?? []);
      }

      if (!patientsResult?.error) {
        const patientsData = patientsResult?.data ?? patientsResult;
        setPatients(patientsData?.patients ?? patientsData ?? []);
      }
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Unable to load dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmRequest = async (requestId) => {
    try {
      const response = await fetchCrmJson(`/consultation-requests/${requestId}/confirm`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          confirmedDate: '2025-09-10',
          confirmedTime: '10:00',
          duration: 60,
          provider: 'Dr. Smith'
        })
      });

      const result = response?.data ?? response;
      if (result?.success) {
        fetchDashboardData();
      }
    } catch (err) {
      console.error('Error confirming request:', err);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'TBD';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatTime = (timeString) => {
    if (!timeString) return 'TBD';
    return new Date(`2000-01-01T${timeString}`).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const getServiceBadgeColor = (serviceType) => {
    const colors = {
      psychiatry: 'bg-blue-100 text-blue-800',
      hormone: 'bg-green-100 text-green-800',
      'weight-loss': 'bg-red-100 text-red-800',
      peptide: 'bg-purple-100 text-purple-800',
      wellness: 'bg-orange-100 text-orange-800',
      default: 'bg-gray-100 text-gray-800'
    };

    return colors[serviceType] || colors.default;
  };

  const getStatusBadgeColor = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      confirmed: 'bg-green-100 text-green-800',
      completed: 'bg-blue-100 text-blue-800',
      cancelled: 'bg-red-100 text-red-800'
    };

    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const filteredRequests = useMemo(() => {
    const normalizedSearch = searchTerm.trim().toLowerCase();

    return consultationRequests.filter((request) => {
      if (!normalizedSearch) return true;

      const haystack = [
        request?.patient_name,
        request?.email,
        request?.phone,
        request?.service_type,
        request?.status
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();

      return haystack.includes(normalizedSearch);
    });
  }, [consultationRequests, searchTerm]);

  const filteredAppointments = useMemo(() => {
    const normalizedSearch = searchTerm.trim().toLowerCase();

    return appointments.filter((appointment) => {
      if (!normalizedSearch) return true;

      const haystack = [
        appointment?.patient_name,
        appointment?.provider,
        appointment?.service_type,
        appointment?.status
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();

      return haystack.includes(normalizedSearch);
    });
  }, [appointments, searchTerm]);

  const filteredPatients = useMemo(() => {
    const normalizedSearch = searchTerm.trim().toLowerCase();

    return patients.filter((patient) => {
      if (!normalizedSearch) return true;

      const haystack = [patient?.first_name, patient?.last_name, patient?.email, patient?.phone]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();

      return haystack.includes(normalizedSearch);
    });
  }, [patients, searchTerm]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="relative bg-white rounded-lg shadow-2xl w-full max-w-5xl">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-semibold text-gray-900 flex items-center gap-3">
              <TrendingUp className="w-6 h-6 text-blue-600" />
              Admin Dashboard
            </h2>
            <p className="text-sm text-gray-500">Monitor requests, appointments, and patient activity</p>
          </div>
          <Button variant="ghost" onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X className="w-5 h-5" />
          </Button>
        </div>

        <div className="px-6 pt-4 flex flex-wrap gap-2 border-b border-gray-100">
          {[
            { id: 'dashboard', label: 'Overview' },
            { id: 'requests', label: 'Consultation Requests' },
            { id: 'appointments', label: 'Appointments' },
            { id: 'patients', label: 'Patients' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === tab.id ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="p-6 space-y-6">
          {(loading || error) && (
            <Card>
              <CardContent className="p-6">
                {loading ? (
                  <div className="flex items-center gap-3 text-blue-600">
                    <Clock className="w-5 h-5 animate-spin" />
                    <span>Loading dashboard data...</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-3 text-red-600">
                    <AlertCircle className="w-5 h-5" />
                    <span>{error}</span>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {!loading && !error && (
            <>
              {activeTab === 'dashboard' && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                      <CardTitle className="text-sm font-medium text-gray-500">Pending Requests</CardTitle>
                      <MessageSquare className="w-4 h-4 text-blue-500" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-semibold">{stats?.pending_requests ?? 0}</div>
                      <p className="text-xs text-gray-500">Awaiting confirmation</p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                      <CardTitle className="text-sm font-medium text-gray-500">Confirmed Appointments</CardTitle>
                      <CalendarDays className="w-4 h-4 text-green-500" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-semibold">{stats?.confirmed_appointments ?? 0}</div>
                      <p className="text-xs text-gray-500">Scheduled for today</p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                      <CardTitle className="text-sm font-medium text-gray-500">Active Patients</CardTitle>
                      <Users className="w-4 h-4 text-purple-500" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-semibold">{stats?.active_patients ?? patients.length}</div>
                      <p className="text-xs text-gray-500">Records in CRM</p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                      <CardTitle className="text-sm font-medium text-gray-500">Average Response</CardTitle>
                      <Clock className="w-4 h-4 text-orange-500" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-semibold">{stats?.avg_response_time ?? '—'}</div>
                      <p className="text-xs text-gray-500">Response time for new leads</p>
                    </CardContent>
                  </Card>
                </div>
              )}

              {activeTab === 'requests' && (
                <div className="space-y-6">
                  <div className="flex flex-col md:flex-row gap-4 md:items-center">
                    <div className="relative flex-1 max-w-md">
                      <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                      <Input
                        placeholder="Search requests..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-9"
                      />
                    </div>
                    <select
                      value={statusFilter}
                      onChange={(e) => {
                        const newStatus = e.target.value;
                        setStatusFilter(newStatus);
                        fetchDashboardData(newStatus);
                      }}
                      className="px-3 py-2 border border-gray-300 rounded-md text-sm"
                    >
                      <option value="pending">Pending</option>
                      <option value="confirmed">Confirmed</option>
                      <option value="all">All</option>
                    </select>
                  </div>

                  <div className="space-y-4">
                    {filteredRequests.length === 0 && (
                      <Card>
                        <CardContent className="p-6 text-center text-gray-500">
                          No consultation requests found.
                        </CardContent>
                      </Card>
                    )}

                    {filteredRequests.map((request) => (
                      <Card key={request?.id ?? request?.uuid ?? Math.random()}>
                        <CardContent className="p-6 space-y-4">
                          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                            <div className="space-y-2">
                              <div className="flex items-center gap-3">
                                <h3 className="text-lg font-semibold text-gray-900">
                                  {request?.patient_name || 'Unknown Patient'}
                                </h3>
                                {request?.service_type && (
                                  <Badge className={getServiceBadgeColor(request.service_type)}>
                                    {request.service_type}
                                  </Badge>
                                )}
                                {request?.status && (
                                  <Badge className={getStatusBadgeColor(request.status)}>
                                    {request.status}
                                  </Badge>
                                )}
                              </div>
                              <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                                {request?.preferred_date && (
                                  <span className="flex items-center gap-2">
                                    <Calendar className="w-4 h-4" />
                                    {formatDate(request.preferred_date)}
                                  </span>
                                )}
                                {request?.preferred_time && (
                                  <span className="flex items-center gap-2">
                                    <Clock className="w-4 h-4" />
                                    {formatTime(request.preferred_time)}
                                  </span>
                                )}
                                {request?.email && (
                                  <span className="flex items-center gap-2">
                                    <Mail className="w-4 h-4" />
                                    {request.email}
                                  </span>
                                )}
                                {request?.phone && (
                                  <span className="flex items-center gap-2">
                                    <Phone className="w-4 h-4" />
                                    {request.phone}
                                  </span>
                                )}
                              </div>
                            </div>
                            <div className="flex gap-2">
                              <Button
                                variant="outline"
                                className="flex items-center gap-2"
                                onClick={() => console.log('View request', request)}
                              >
                                <Eye className="w-4 h-4" /> View
                              </Button>
                              <Button
                                className="bg-green-600 hover:bg-green-700 flex items-center gap-2"
                                onClick={() => handleConfirmRequest(request?.id)}
                              >
                                <Check className="w-4 h-4" /> Confirm
                              </Button>
                            </div>
                          </div>

                          {request?.notes && (
                            <div className="bg-gray-50 rounded-md p-4 text-sm text-gray-600">
                              <p className="font-medium text-gray-700 mb-1">Notes</p>
                              <p>{request.notes}</p>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'appointments' && (
                <div className="space-y-4">
                  <div className="relative max-w-md">
                    <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    <Input
                      placeholder="Search appointments..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-9"
                    />
                  </div>

                  <div className="space-y-4">
                    {filteredAppointments.length === 0 && (
                      <Card>
                        <CardContent className="p-6 text-center text-gray-500">
                          No appointments found for today.
                        </CardContent>
                      </Card>
                    )}

                    {filteredAppointments.map((appointment) => (
                      <Card key={appointment?.id ?? appointment?.uuid ?? Math.random()}>
                        <CardContent className="p-6 space-y-4">
                          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                            <div className="space-y-2">
                              <div className="flex items-center gap-3">
                                <h3 className="text-lg font-semibold text-gray-900">
                                  {appointment?.patient_name || 'Unknown Patient'}
                                </h3>
                                {appointment?.status && (
                                  <Badge className={getStatusBadgeColor(appointment.status)}>
                                    {appointment.status}
                                  </Badge>
                                )}
                              </div>
                              <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                                {appointment?.date && (
                                  <span className="flex items-center gap-2">
                                    <Calendar className="w-4 h-4" />
                                    {formatDate(appointment.date)}
                                  </span>
                                )}
                                {appointment?.time && (
                                  <span className="flex items-center gap-2">
                                    <Clock className="w-4 h-4" />
                                    {formatTime(appointment.time)}
                                  </span>
                                )}
                                {appointment?.provider && (
                                  <span className="flex items-center gap-2">
                                    <User className="w-4 h-4" />
                                    {appointment.provider}
                                  </span>
                                )}
                                {appointment?.service_type && (
                                  <Badge className={getServiceBadgeColor(appointment.service_type)}>
                                    {appointment.service_type}
                                  </Badge>
                                )}
                              </div>
                            </div>
                            <div className="flex gap-2">
                              <Button variant="outline" className="flex items-center gap-2">
                                <CheckCircle className="w-4 h-4 text-green-600" /> Complete
                              </Button>
                              <Button variant="outline" className="flex items-center gap-2 text-red-600">
                                <X className="w-4 h-4" /> Cancel
                              </Button>
                            </div>
                          </div>

                          {appointment?.notes && (
                            <div className="bg-gray-50 rounded-md p-4 text-sm text-gray-600">
                              <p className="font-medium text-gray-700 mb-1">Notes</p>
                              <p>{appointment.notes}</p>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'patients' && (
                <div className="space-y-4">
                  <div className="relative max-w-md">
                    <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    <Input
                      placeholder="Search patients..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-9"
                    />
                  </div>

                  <div className="space-y-4">
                    {filteredPatients.length === 0 && (
                      <Card>
                        <CardContent className="p-6 text-center text-gray-500">
                          No patients found.
                        </CardContent>
                      </Card>
                    )}

                    {filteredPatients.map((patient) => (
                      <Card key={patient?.id ?? patient?.uuid ?? Math.random()}>
                        <CardContent className="p-6 space-y-4">
                          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                            <div className="space-y-2">
                              <h3 className="text-lg font-semibold text-gray-900">
                                {[patient?.first_name, patient?.last_name].filter(Boolean).join(' ') || 'Unnamed Patient'}
                              </h3>
                              <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                                {patient?.email && (
                                  <span className="flex items-center gap-2">
                                    <Mail className="w-4 h-4" />
                                    {patient.email}
                                  </span>
                                )}
                                {patient?.phone && (
                                  <span className="flex items-center gap-2">
                                    <Phone className="w-4 h-4" />
                                    {patient.phone}
                                  </span>
                                )}
                                {patient?.last_visit_date && (
                                  <span className="flex items-center gap-2">
                                    <Calendar className="w-4 h-4" />
                                    {formatDate(patient.last_visit_date)}
                                  </span>
                                )}
                              </div>
                            </div>
                            <div className="flex gap-2">
                              <Button variant="outline" className="flex items-center gap-2">
                                <Eye className="w-4 h-4" /> View Profile
                              </Button>
                              <Button variant="outline" className="flex items-center gap-2">
                                <MessageSquare className="w-4 h-4" /> Contact
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
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
