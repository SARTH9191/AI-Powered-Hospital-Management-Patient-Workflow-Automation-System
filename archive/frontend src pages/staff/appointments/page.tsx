'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/hooks/useAuth';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';
import {
  Calendar,
  Clock,
  User,
  Search,
  Filter,
  ChevronLeft,
  ChevronRight,
  Plus,
  Edit,
  CheckCircle,
  XCircle,
  UserCheck,
  Phone,
  Mail,
} from 'lucide-react';
import axios from 'axios';

interface Appointment {
  appointment_id: string;
  patient_id: string;
  patient_name: string;
  patient_phone?: string;
  patient_email?: string;
  doctor_id: string;
  doctor_name: string;
  appointment_date: string;
  appointment_time: string;
  type: string;
  status: string;
  reason?: string;
  checked_in: boolean;
  check_in_time?: string;
}

export default function StaffAppointments() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const staffId = 'staff001'; // TODO: Get from authenticated user

  const [selectedDate, setSelectedDate] = useState(new Date());
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [doctorFilter, setDoctorFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAppointment, setSelectedAppointment] = useState<Appointment | null>(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [scheduleDialogOpen, setScheduleDialogOpen] = useState(false);

  // Form state for scheduling
  const [formData, setFormData] = useState({
    patient_id: '',
    patient_name: '',
    doctor_id: '',
    appointment_date: new Date().toISOString().split('T')[0],
    appointment_time: '09:00:00',
    type: 'consultation',
    reason: '',
  });

  // Fetch appointments for selected date
  const { data: appointmentsData, isLoading } = useQuery({
    queryKey: ['staff-appointments', selectedDate.toISOString().split('T')[0]],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `http://localhost:8000/api/appointments`,
        {
          params: {
            date: selectedDate.toISOString().split('T')[0],
          },
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data?.data?.appointments || [];
    },
  });

  // Fetch doctors for scheduling
  const { data: doctorsData } = useQuery({
    queryKey: ['doctors-list'],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        'http://localhost:8000/api/doctors',
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data?.data?.doctors || [];
    },
  });

  // Schedule appointment mutation
  const scheduleMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        'http://localhost:8000/api/appointments',
        {
          ...data,
          status: 'scheduled',
          checked_in: false,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['staff-appointments'] });
      setScheduleDialogOpen(false);
      resetForm();
    },
  });

  // Update appointment status mutation
  const updateStatusMutation = useMutation({
    mutationFn: async ({ appointmentId, status }: { appointmentId: string; status: string }) => {
      const token = localStorage.getItem('token');
      const response = await axios.put(
        `http://localhost:8000/api/appointments/${appointmentId}/status`,
        { status },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['staff-appointments'] });
      setDetailsDialogOpen(false);
    },
  });

  const appointments: Appointment[] = appointmentsData || [];
  const doctors = doctorsData || [];

  // Filter appointments
  const filteredAppointments = appointments.filter((apt) => {
    if (statusFilter !== 'all' && apt.status !== statusFilter) return false;
    if (doctorFilter !== 'all' && apt.doctor_id !== doctorFilter) return false;
    if (
      searchQuery &&
      !apt.patient_name.toLowerCase().includes(searchQuery.toLowerCase()) &&
      !apt.patient_id.toLowerCase().includes(searchQuery.toLowerCase())
    ) {
      return false;
    }
    return true;
  });

  const formatTime = (timeString: string) => {
    return new Date(`2000-01-01T${timeString}`).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const goToPreviousDay = () => {
    const newDate = new Date(selectedDate);
    newDate.setDate(newDate.getDate() - 1);
    setSelectedDate(newDate);
  };

  const goToNextDay = () => {
    const newDate = new Date(selectedDate);
    newDate.setDate(newDate.getDate() + 1);
    setSelectedDate(newDate);
  };

  const goToToday = () => {
    setSelectedDate(new Date());
  };

  const resetForm = () => {
    setFormData({
      patient_id: '',
      patient_name: '',
      doctor_id: '',
      appointment_date: new Date().toISOString().split('T')[0],
      appointment_time: '09:00:00',
      type: 'consultation',
      reason: '',
    });
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'default';
      case 'confirmed':
      case 'scheduled':
        return 'secondary';
      case 'in_progress':
        return 'outline';
      case 'cancelled':
        return 'destructive';
      default:
        return 'outline';
    }
  };

  const handleViewDetails = (appointment: Appointment) => {
    setSelectedAppointment(appointment);
    setDetailsDialogOpen(true);
  };

  const handleUpdateStatus = (status: string) => {
    if (selectedAppointment) {
      updateStatusMutation.mutate({
        appointmentId: selectedAppointment.appointment_id,
        status,
      });
    }
  };

  const handleSchedule = () => {
    scheduleMutation.mutate(formData);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar role="staff" />
        <main className="flex-1 ml-64 mt-16">
          <div className="p-8">
            {/* Header */}
            <div className="mb-8 flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">Appointments</h1>
                <p className="text-gray-600">Manage daily appointments and scheduling</p>
              </div>
              <Button onClick={() => setScheduleDialogOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Schedule Appointment
              </Button>
            </div>

            {/* Controls */}
            <div className="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
              {/* Date Navigation */}
              <div className="flex items-center space-x-4">
                <Button variant="outline" size="sm" onClick={goToPreviousDay}>
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <div className="flex items-center space-x-2">
                  <Calendar className="h-5 w-5 text-gray-600" />
                  <span className="font-medium text-gray-900">{formatDate(selectedDate)}</span>
                </div>
                <Button variant="outline" size="sm" onClick={goToNextDay}>
                  <ChevronRight className="h-4 w-4" />
                </Button>
                <Button variant="outline" size="sm" onClick={goToToday}>
                  Today
                </Button>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Total</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-gray-900">{filteredAppointments.length}</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Checked In</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-green-600">
                    {filteredAppointments.filter((a) => a.checked_in).length}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Pending</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-orange-600">
                    {filteredAppointments.filter((a) => !a.checked_in && a.status !== 'cancelled').length}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Completed</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-blue-600">
                    {filteredAppointments.filter((a) => a.status === 'completed').length}
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Filters */}
            <Card className="mb-6">
              <CardContent className="pt-6">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  {/* Search */}
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Search patient..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>

                  {/* Status Filter */}
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="Status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Status</SelectItem>
                      <SelectItem value="scheduled">Scheduled</SelectItem>
                      <SelectItem value="confirmed">Confirmed</SelectItem>
                      <SelectItem value="in_progress">In Progress</SelectItem>
                      <SelectItem value="completed">Completed</SelectItem>
                      <SelectItem value="cancelled">Cancelled</SelectItem>
                    </SelectContent>
                  </Select>

                  {/* Doctor Filter */}
                  <Select value={doctorFilter} onValueChange={setDoctorFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="Doctor" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Doctors</SelectItem>
                      {doctors.map((doctor: any) => (
                        <SelectItem key={doctor.doctor_id} value={doctor.doctor_id}>
                          Dr. {doctor.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  {/* Count */}
                  <div className="flex items-center justify-center bg-blue-50 rounded-lg px-4 py-2">
                    <span className="text-2xl font-bold text-blue-600">
                      {filteredAppointments.length}
                    </span>
                    <span className="text-sm text-gray-600 ml-2">appointments</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Tabs */}
            <Tabs defaultValue="all" className="space-y-6">
              <TabsList>
                <TabsTrigger value="all">
                  All ({filteredAppointments.length})
                </TabsTrigger>
                <TabsTrigger value="pending">
                  Pending Check-in ({filteredAppointments.filter((a) => !a.checked_in && a.status !== 'cancelled').length})
                </TabsTrigger>
                <TabsTrigger value="checked-in">
                  Checked In ({filteredAppointments.filter((a) => a.checked_in).length})
                </TabsTrigger>
              </TabsList>

              {/* All Tab */}
              <TabsContent value="all">
                {isLoading ? (
                  <div className="space-y-3">
                    {[1, 2, 3, 4].map((i) => (
                      <Card key={i}>
                        <CardContent className="pt-6">
                          <Skeleton className="h-20 w-full" />
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                ) : filteredAppointments.length === 0 ? (
                  <Card>
                    <CardContent className="pt-12 pb-12 text-center">
                      <Calendar className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600 text-lg">No appointments found</p>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="space-y-3">
                    {filteredAppointments.map((appointment) => (
                      <Card
                        key={appointment.appointment_id}
                        className="hover:shadow-lg transition-shadow cursor-pointer"
                        onClick={() => handleViewDetails(appointment)}
                      >
                        <CardContent className="pt-6">
                          <div className="flex items-start justify-between">
                            <div className="flex items-center space-x-4 flex-1">
                              <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
                                <span className="text-blue-600 font-semibold">
                                  {appointment.patient_name.charAt(0)}
                                </span>
                              </div>
                              <div className="flex-1">
                                <div className="flex items-center space-x-3 mb-1">
                                  <h3 className="font-semibold text-gray-900">
                                    {appointment.patient_name}
                                  </h3>
                                  {appointment.checked_in && (
                                    <Badge variant="default">
                                      <CheckCircle className="h-3 w-3 mr-1" />
                                      Checked In
                                    </Badge>
                                  )}
                                  <Badge variant={getStatusColor(appointment.status)}>
                                    {appointment.status}
                                  </Badge>
                                </div>
                                <div className="flex items-center space-x-4 text-sm text-gray-600">
                                  <div className="flex items-center space-x-1">
                                    <Clock className="h-3 w-3" />
                                    <span>{formatTime(appointment.appointment_time)}</span>
                                  </div>
                                  <div className="flex items-center space-x-1">
                                    <User className="h-3 w-3" />
                                    <span>Dr. {appointment.doctor_name}</span>
                                  </div>
                                  <span className="capitalize">{appointment.type}</span>
                                </div>
                                {appointment.reason && (
                                  <p className="text-sm text-gray-600 mt-1">
                                    Reason: {appointment.reason}
                                  </p>
                                )}
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </TabsContent>

              {/* Pending Check-in Tab */}
              <TabsContent value="pending">
                <div className="space-y-3">
                  {filteredAppointments
                    .filter((a) => !a.checked_in && a.status !== 'cancelled')
                    .map((appointment) => (
                      <Card
                        key={appointment.appointment_id}
                        className="border-orange-200 hover:shadow-lg transition-shadow"
                      >
                        <CardContent className="pt-6">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-4 flex-1">
                              <div className="h-12 w-12 bg-orange-100 rounded-full flex items-center justify-center">
                                <UserCheck className="h-6 w-6 text-orange-600" />
                              </div>
                              <div>
                                <h3 className="font-semibold text-gray-900">
                                  {appointment.patient_name}
                                </h3>
                                <div className="flex items-center space-x-3 text-sm text-gray-600">
                                  <Clock className="h-3 w-3" />
                                  <span>{formatTime(appointment.appointment_time)}</span>
                                  <span>•</span>
                                  <span>Dr. {appointment.doctor_name}</span>
                                </div>
                              </div>
                            </div>
                            <Button onClick={() => handleViewDetails(appointment)}>
                              <UserCheck className="h-4 w-4 mr-2" />
                              Check In
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  {filteredAppointments.filter((a) => !a.checked_in && a.status !== 'cancelled').length === 0 && (
                    <Card>
                      <CardContent className="pt-12 pb-12 text-center">
                        <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
                        <p className="text-gray-600 text-lg">All patients checked in!</p>
                      </CardContent>
                    </Card>
                  )}
                </div>
              </TabsContent>

              {/* Checked In Tab */}
              <TabsContent value="checked-in">
                <div className="space-y-3">
                  {filteredAppointments
                    .filter((a) => a.checked_in)
                    .map((appointment) => (
                      <Card key={appointment.appointment_id} className="border-green-200">
                        <CardContent className="pt-6">
                          <div className="flex items-center space-x-4">
                            <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center">
                              <CheckCircle className="h-6 w-6 text-green-600" />
                            </div>
                            <div className="flex-1">
                              <h3 className="font-semibold text-gray-900">
                                {appointment.patient_name}
                              </h3>
                              <div className="flex items-center space-x-4 text-sm text-gray-600">
                                <span>{formatTime(appointment.appointment_time)}</span>
                                <span>•</span>
                                <span>Dr. {appointment.doctor_name}</span>
                                {appointment.check_in_time && (
                                  <>
                                    <span>•</span>
                                    <span>Checked in at {formatTime(appointment.check_in_time)}</span>
                                  </>
                                )}
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </main>
      </div>

      {/* Appointment Details Dialog */}
      <Dialog open={detailsDialogOpen} onOpenChange={setDetailsDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Appointment Details</DialogTitle>
          </DialogHeader>

          {selectedAppointment && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Patient Name</Label>
                  <p className="font-medium">{selectedAppointment.patient_name}</p>
                </div>
                <div>
                  <Label>Patient ID</Label>
                  <p className="font-medium">{selectedAppointment.patient_id}</p>
                </div>
                <div>
                  <Label>Doctor</Label>
                  <p className="font-medium">Dr. {selectedAppointment.doctor_name}</p>
                </div>
                <div>
                  <Label>Date & Time</Label>
                  <p className="font-medium">
                    {new Date(selectedAppointment.appointment_date).toLocaleDateString()} at{' '}
                    {formatTime(selectedAppointment.appointment_time)}
                  </p>
                </div>
                <div>
                  <Label>Type</Label>
                  <p className="font-medium capitalize">{selectedAppointment.type}</p>
                </div>
                <div>
                  <Label>Status</Label>
                  <Badge variant={getStatusColor(selectedAppointment.status)}>
                    {selectedAppointment.status}
                  </Badge>
                </div>
              </div>

              {selectedAppointment.patient_phone && (
                <div>
                  <Label>Contact</Label>
                  <div className="flex items-center space-x-4 mt-1">
                    <div className="flex items-center space-x-2">
                      <Phone className="h-4 w-4 text-gray-400" />
                      <span>{selectedAppointment.patient_phone}</span>
                    </div>
                    {selectedAppointment.patient_email && (
                      <div className="flex items-center space-x-2">
                        <Mail className="h-4 w-4 text-gray-400" />
                        <span>{selectedAppointment.patient_email}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {selectedAppointment.reason && (
                <div>
                  <Label>Reason for Visit</Label>
                  <p className="mt-1">{selectedAppointment.reason}</p>
                </div>
              )}

              <div>
                <Label>Check-in Status</Label>
                <div className="mt-2">
                  {selectedAppointment.checked_in ? (
                    <Badge variant="default">
                      <CheckCircle className="h-4 w-4 mr-2" />
                      Checked In
                      {selectedAppointment.check_in_time && (
                        <span className="ml-2">at {formatTime(selectedAppointment.check_in_time)}</span>
                      )}
                    </Badge>
                  ) : (
                    <Badge variant="outline">Not Checked In</Badge>
                  )}
                </div>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setDetailsDialogOpen(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Schedule Appointment Dialog */}
      <Dialog open={scheduleDialogOpen} onOpenChange={setScheduleDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Schedule New Appointment</DialogTitle>
            <DialogDescription>Create a new appointment for a patient</DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="patient_id">Patient ID *</Label>
                <Input
                  id="patient_id"
                  value={formData.patient_id}
                  onChange={(e) => setFormData({ ...formData, patient_id: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="patient_name">Patient Name *</Label>
                <Input
                  id="patient_name"
                  value={formData.patient_name}
                  onChange={(e) => setFormData({ ...formData, patient_name: e.target.value })}
                />
              </div>
            </div>

            <div>
              <Label htmlFor="doctor">Doctor *</Label>
              <Select
                value={formData.doctor_id}
                onValueChange={(value) => setFormData({ ...formData, doctor_id: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select doctor" />
                </SelectTrigger>
                <SelectContent>
                  {doctors.map((doctor: any) => (
                    <SelectItem key={doctor.doctor_id} value={doctor.doctor_id}>
                      Dr. {doctor.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="date">Date *</Label>
                <Input
                  id="date"
                  type="date"
                  value={formData.appointment_date}
                  onChange={(e) => setFormData({ ...formData, appointment_date: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="time">Time *</Label>
                <Input
                  id="time"
                  type="time"
                  value={formData.appointment_time.substring(0, 5)}
                  onChange={(e) => setFormData({ ...formData, appointment_time: e.target.value + ':00' })}
                />
              </div>
            </div>

            <div>
              <Label htmlFor="type">Type *</Label>
              <Select
                value={formData.type}
                onValueChange={(value) => setFormData({ ...formData, type: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="consultation">Consultation</SelectItem>
                  <SelectItem value="follow-up">Follow-up</SelectItem>
                  <SelectItem value="telemedicine">Telemedicine</SelectItem>
                  <SelectItem value="emergency">Emergency</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="reason">Reason for Visit</Label>
              <Input
                id="reason"
                value={formData.reason}
                onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
                placeholder="Brief description"
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setScheduleDialogOpen(false);
                resetForm();
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSchedule}
              disabled={scheduleMutation.isPending}
            >
              <Calendar className="h-4 w-4 mr-2" />
              Schedule Appointment
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
