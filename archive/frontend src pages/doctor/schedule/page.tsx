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
  CheckCircle,
  XCircle,
  AlertCircle,
  Video,
  MapPin,
  Phone,
} from 'lucide-react';
import axios from 'axios';

interface Appointment {
  appointment_id: string;
  patient_id: string;
  patient_name: string;
  doctor_id: string;
  appointment_date: string;
  appointment_time: string;
  type: string;
  status: string;
  reason?: string;
  notes?: string;
}

interface TimeSlot {
  time: string;
  available: boolean;
  appointment?: Appointment;
}

export default function DoctorSchedule() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const doctorId = 'doctor001'; // TODO: Get from authenticated user

  const [selectedDate, setSelectedDate] = useState(new Date());
  const [view, setView] = useState<'day' | 'week'>('day');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAppointment, setSelectedAppointment] = useState<Appointment | null>(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [rescheduleDialogOpen, setRescheduleDialogOpen] = useState(false);

  // Fetch appointments for selected date
  const { data: appointmentsData, isLoading } = useQuery({
    queryKey: ['doctor-appointments', doctorId, selectedDate.toISOString().split('T')[0]],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `http://localhost:8000/api/appointments/doctor/${doctorId}`,
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
    enabled: !!doctorId,
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
      queryClient.invalidateQueries({ queryKey: ['doctor-appointments'] });
      setDetailsDialogOpen(false);
    },
  });

  const appointments: Appointment[] = appointmentsData || [];

  // Filter appointments
  const filteredAppointments = appointments.filter((apt) => {
    if (statusFilter !== 'all' && apt.status !== statusFilter) return false;
    if (typeFilter !== 'all' && apt.type !== typeFilter) return false;
    if (searchQuery && !apt.patient_name.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    return true;
  });

  // Generate time slots for the day (8 AM - 6 PM)
  const generateTimeSlots = (): TimeSlot[] => {
    const slots: TimeSlot[] = [];
    for (let hour = 8; hour < 18; hour++) {
      for (let minute = 0; minute < 60; minute += 30) {
        const time = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}:00`;
        const appointment = filteredAppointments.find((apt) => apt.appointment_time === time);
        slots.push({
          time,
          available: !appointment,
          appointment,
        });
      }
    }
    return slots;
  };

  const timeSlots = generateTimeSlots();

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

  const getTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'video':
      case 'telemedicine':
        return <Video className="h-4 w-4" />;
      case 'phone':
        return <Phone className="h-4 w-4" />;
      case 'in-person':
      case 'consultation':
        return <MapPin className="h-4 w-4" />;
      default:
        return <User className="h-4 w-4" />;
    }
  };

  const handleAppointmentClick = (appointment: Appointment) => {
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

  const getStatusActions = (status: string) => {
    switch (status.toLowerCase()) {
      case 'scheduled':
      case 'confirmed':
        return [
          { label: 'Start Consultation', value: 'in_progress', icon: CheckCircle },
          { label: 'Cancel', value: 'cancelled', icon: XCircle },
        ];
      case 'in_progress':
        return [
          { label: 'Complete', value: 'completed', icon: CheckCircle },
          { label: 'Cancel', value: 'cancelled', icon: XCircle },
        ];
      default:
        return [];
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar role="doctor" />
        <main className="flex-1 ml-64 mt-16">
          <div className="p-8">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Schedule</h1>
              <p className="text-gray-600">Manage your appointments and availability</p>
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

              {/* View Toggle */}
              <Tabs value={view} onValueChange={(v) => setView(v as 'day' | 'week')}>
                <TabsList>
                  <TabsTrigger value="day">Day</TabsTrigger>
                  <TabsTrigger value="week">Week</TabsTrigger>
                </TabsList>
              </Tabs>
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

                  {/* Type Filter */}
                  <Select value={typeFilter} onValueChange={setTypeFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="Type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Types</SelectItem>
                      <SelectItem value="consultation">In-Person</SelectItem>
                      <SelectItem value="telemedicine">Telemedicine</SelectItem>
                      <SelectItem value="follow-up">Follow-up</SelectItem>
                      <SelectItem value="emergency">Emergency</SelectItem>
                    </SelectContent>
                  </Select>

                  {/* Stats */}
                  <div className="flex items-center justify-center bg-blue-50 rounded-lg px-4 py-2">
                    <span className="text-2xl font-bold text-blue-600">
                      {filteredAppointments.length}
                    </span>
                    <span className="text-sm text-gray-600 ml-2">appointments</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Schedule Grid */}
            {isLoading ? (
              <Card>
                <CardContent className="pt-6">
                  <div className="space-y-3">
                    {[1, 2, 3, 4, 5, 6].map((i) => (
                      <Skeleton key={i} className="h-20 w-full" />
                    ))}
                  </div>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Timeline View */}
                <div className="lg:col-span-2">
                  <Card>
                    <CardHeader>
                      <CardTitle>Timeline</CardTitle>
                      <CardDescription>
                        Your schedule for {formatDate(selectedDate)}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-1 max-h-[600px] overflow-y-auto">
                        {timeSlots.map((slot) => (
                          <div
                            key={slot.time}
                            className={`flex items-stretch border-l-4 ${
                              slot.appointment
                                ? 'border-blue-500 bg-blue-50'
                                : 'border-gray-200 bg-white'
                            } rounded-r-lg overflow-hidden hover:shadow-sm transition-shadow`}
                          >
                            {/* Time */}
                            <div className="w-24 flex-shrink-0 p-3 bg-gray-50 border-r">
                              <div className="flex items-center space-x-1">
                                <Clock className="h-3 w-3 text-gray-400" />
                                <span className="text-sm font-medium text-gray-700">
                                  {formatTime(slot.time)}
                                </span>
                              </div>
                            </div>

                            {/* Content */}
                            <div className="flex-1 p-3">
                              {slot.appointment ? (
                                <button
                                  onClick={() => handleAppointmentClick(slot.appointment!)}
                                  className="w-full text-left"
                                >
                                  <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                      <div className="flex items-center space-x-2 mb-1">
                                        {getTypeIcon(slot.appointment.type)}
                                        <span className="font-medium text-gray-900">
                                          {slot.appointment.patient_name}
                                        </span>
                                        <Badge
                                          variant={getStatusColor(slot.appointment.status)}
                                          className="text-xs"
                                        >
                                          {slot.appointment.status}
                                        </Badge>
                                      </div>
                                      <p className="text-sm text-gray-600 capitalize">
                                        {slot.appointment.type}
                                        {slot.appointment.reason && ` • ${slot.appointment.reason}`}
                                      </p>
                                    </div>
                                  </div>
                                </button>
                              ) : (
                                <div className="text-sm text-gray-400 italic">Available</div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Summary Sidebar */}
                <div className="space-y-6">
                  {/* Stats Card */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Today's Overview</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                        <div className="flex items-center space-x-2">
                          <CheckCircle className="h-5 w-5 text-green-600" />
                          <span className="text-sm text-gray-600">Completed</span>
                        </div>
                        <span className="text-lg font-bold text-green-600">
                          {appointments.filter((a) => a.status === 'completed').length}
                        </span>
                      </div>

                      <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                        <div className="flex items-center space-x-2">
                          <Clock className="h-5 w-5 text-blue-600" />
                          <span className="text-sm text-gray-600">Scheduled</span>
                        </div>
                        <span className="text-lg font-bold text-blue-600">
                          {
                            appointments.filter(
                              (a) => a.status === 'scheduled' || a.status === 'confirmed'
                            ).length
                          }
                        </span>
                      </div>

                      <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                        <div className="flex items-center space-x-2">
                          <AlertCircle className="h-5 w-5 text-yellow-600" />
                          <span className="text-sm text-gray-600">In Progress</span>
                        </div>
                        <span className="text-lg font-bold text-yellow-600">
                          {appointments.filter((a) => a.status === 'in_progress').length}
                        </span>
                      </div>

                      <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                        <div className="flex items-center space-x-2">
                          <XCircle className="h-5 w-5 text-red-600" />
                          <span className="text-sm text-gray-600">Cancelled</span>
                        </div>
                        <span className="text-lg font-bold text-red-600">
                          {appointments.filter((a) => a.status === 'cancelled').length}
                        </span>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Next Appointment */}
                  {filteredAppointments.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Next Appointment</CardTitle>
                      </CardHeader>
                      <CardContent>
                        {(() => {
                          const nextApt = filteredAppointments
                            .filter((a) => a.status !== 'completed' && a.status !== 'cancelled')
                            .sort((a, b) => a.appointment_time.localeCompare(b.appointment_time))[0];

                          if (!nextApt) {
                            return (
                              <p className="text-sm text-gray-600">No upcoming appointments</p>
                            );
                          }

                          return (
                            <div className="space-y-3">
                              <div className="flex items-center space-x-2">
                                <Clock className="h-4 w-4 text-gray-400" />
                                <span className="text-sm font-medium">
                                  {formatTime(nextApt.appointment_time)}
                                </span>
                              </div>
                              <div className="flex items-center space-x-2">
                                <User className="h-4 w-4 text-gray-400" />
                                <span className="text-sm font-medium">{nextApt.patient_name}</span>
                              </div>
                              <div className="flex items-center space-x-2">
                                {getTypeIcon(nextApt.type)}
                                <span className="text-sm text-gray-600 capitalize">
                                  {nextApt.type}
                                </span>
                              </div>
                              <Button
                                onClick={() => handleAppointmentClick(nextApt)}
                                className="w-full mt-3"
                                size="sm"
                              >
                                View Details
                              </Button>
                            </div>
                          );
                        })()}
                      </CardContent>
                    </Card>
                  )}
                </div>
              </div>
            )}
          </div>
        </main>
      </div>

      {/* Appointment Details Dialog */}
      <Dialog open={detailsDialogOpen} onOpenChange={setDetailsDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Appointment Details</DialogTitle>
            <DialogDescription>
              View and manage appointment information
            </DialogDescription>
          </DialogHeader>

          {selectedAppointment && (
            <div className="space-y-6">
              {/* Patient Info */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-3">Patient Information</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Name:</span>
                    <p className="font-medium text-gray-900">{selectedAppointment.patient_name}</p>
                  </div>
                  <div>
                    <span className="text-gray-600">Patient ID:</span>
                    <p className="font-medium text-gray-900">{selectedAppointment.patient_id}</p>
                  </div>
                </div>
              </div>

              {/* Appointment Info */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-3">Appointment Details</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Date:</span>
                    <p className="font-medium text-gray-900">
                      {new Date(selectedAppointment.appointment_date).toLocaleDateString()}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-600">Time:</span>
                    <p className="font-medium text-gray-900">
                      {formatTime(selectedAppointment.appointment_time)}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-600">Type:</span>
                    <p className="font-medium text-gray-900 capitalize">
                      {selectedAppointment.type}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-600">Status:</span>
                    <Badge variant={getStatusColor(selectedAppointment.status)}>
                      {selectedAppointment.status}
                    </Badge>
                  </div>
                </div>
              </div>

              {/* Reason & Notes */}
              {(selectedAppointment.reason || selectedAppointment.notes) && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 mb-3">Additional Information</h3>
                  {selectedAppointment.reason && (
                    <div className="mb-3">
                      <span className="text-sm text-gray-600">Reason:</span>
                      <p className="text-sm text-gray-900">{selectedAppointment.reason}</p>
                    </div>
                  )}
                  {selectedAppointment.notes && (
                    <div>
                      <span className="text-sm text-gray-600">Notes:</span>
                      <p className="text-sm text-gray-900">{selectedAppointment.notes}</p>
                    </div>
                  )}
                </div>
              )}

              {/* Status Actions */}
              <div className="flex flex-wrap gap-2">
                {getStatusActions(selectedAppointment.status).map((action) => {
                  const Icon = action.icon;
                  return (
                    <Button
                      key={action.value}
                      onClick={() => handleUpdateStatus(action.value)}
                      variant={action.value === 'cancelled' ? 'destructive' : 'default'}
                      disabled={updateStatusMutation.isPending}
                    >
                      <Icon className="h-4 w-4 mr-2" />
                      {action.label}
                    </Button>
                  );
                })}
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
    </div>
  );
}
