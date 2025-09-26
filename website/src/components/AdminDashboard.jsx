 import React, { useState, useEffect } from 'react';
 import { Button } from '@/components/ui/button.jsx';
 import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx';
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

       const today = new Date().toISOString().split('T')[0];

       const [statsResult, requestsResult, appointmentsResult] = await Promise.all([
         fetchCrmJson('/dashboard/stats'),
         fetchCrmJson(`/consultation-requests?status=${currentStatus}`),
         fetchCrmJson(`/appointments?start_date=${today}&end_date=${today}`)
       ]);
 
       const statsData = statsResult?.data ?? statsResult;
      if (statsData?.success) {
         setStats(statsData.stats);
       }

       const requestsData = requestsResult?.data ?? requestsResult;
       if (requestsData?.success) {
         setConsultationRequests(requestsData.consultation_requests);
       }

       const appointmentsData = appointmentsResult?.data ?? appointmentsResult;
       if (appointmentsData?.success) {
         setAppointments(appointmentsData.appointments);
       }
  
     } catch (error) {
       console.error('Error fetching dashboard data:', error);
       if (error?.attempts) {
         console.error('CRM fetch attempts:', error.attempts);
       }
     } finally {
       setLoading(false);
     }
   };
 
   const handleConfirmRequest = async (requestId) => {
     try {
       const response = await fetchCrmJson(`/consultation-requests/${requestId}/confirm`, {
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

       const result = response?.data ?? response;
       if (result?.success) {
         fetchDashboardData(); // Refresh data
       }
     } catch (error) {
       console.error('Error confirming request:', error);
       if (error?.attempts) {
         console.error('CRM confirmation attempts:', error.attempts);
       }
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
