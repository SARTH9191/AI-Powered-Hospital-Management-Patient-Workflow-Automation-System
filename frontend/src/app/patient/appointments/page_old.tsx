'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/hooks/useAuth';
import { appointmentsAPI } from '@/lib/api/appointments';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';
import {
  Calendar as CalendarIcon,
  Clock,
  Plus,
  MapPin,
  User,
  FileText,
  CheckCircle,
  XCircle,
  Video,
} from 'lucide-react';
import { toast } from 'sonner';

interface Appointment {
  appointment_id: string;
  patient_id: string;
  patient_name: string;
  doctor_id: string;
  doctor_name: string;
  specialty: string;
  appointment_date: string;
  appointment_time: string;
  type: string;
  status: string;
  reason?: string;
  notes?: string;
  location?: string;
}

export default function PatientAppointments() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const patientId = 'patient001'; // TODO: Get from authenticated user

  // Fetch all appointments
  const { data: appointmentsData, isLoading } = useQuery({
    queryKey: ['appointments', patientId],
    queryFn: () => appointmentsAPI.getAllAppointments({ patient_id: patientId }),
    enabled: !!patientId,
  });

  const appointments = appointmentsData?.appointments || [];

  const [showBookDialog, setShowBookDialog] = useState(false);
  const [showCancelDialog, setShowCancelDialog] = useState(false);
  const [selectedAppointment, setSelectedAppointment] = useState<Appointment | null>(null);
  const [formData, setFormData] = useState({
    specialty: '',
    doctor: '',
    date: '',
    time: '',
    type: 'In-Person',
    reason: '',
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleBookAppointment = (e: React.FormEvent) => {
    e.preventDefault();
    const newAppointment: Appointment = {
      id: `APT${(appointments.length + 1).toString().padStart(3, '0')}`,
      doctor: formData.doctor,
      specialty: formData.specialty,
      date: formData.date,
      time: formData.time,
      type: formData.type as 'In-Person' | 'Virtual',
      status: 'upcoming',
      location: formData.type === 'Virtual' ? 'Online Video Call' : 'TBD',
      reason: formData.reason,
    };
    setAppointments([...appointments, newAppointment]);
    toast.success('Appointment booked successfully!');
    setShowBookDialog(false);
    setFormData({
      specialty: '',
      doctor: '',
      date: '',
      time: '',
      type: 'In-Person',
      reason: '',
    });
  };

  const handleCancelAppointment = (id: string) => {
    setAppointments(appointments.map(apt =>
      apt.id === id ? { ...apt, status: 'cancelled' as const } : apt
    ));
    toast.success('Appointment cancelled');
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'upcoming':
        return 'default';
      case 'completed':
        return 'secondary';
      case 'cancelled':
        return 'destructive';
      default:
        return 'outline';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'upcoming':
        return <Clock className="h-4 w-4 text-blue-600" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'cancelled':
        return <XCircle className="h-4 w-4 text-red-600" />;
      default:
        return null;
    }
  };

  const upcomingAppointments = appointments.filter(a => a.status === 'upcoming');
  const pastAppointments = appointments.filter(a => a.status === 'completed');
  const cancelledAppointments = appointments.filter(a => a.status === 'cancelled');

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar role="patient" />
        <main className="flex-1 ml-64 mt-16">
          <div className="p-8">
            {/* Header */}
            <div className="mb-8">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900 mb-2">My Appointments</h1>
                  <p className="text-gray-600">View and manage your appointments</p>
                </div>
                <Button
                  onClick={() => setShowBookDialog(true)}
                  className="flex items-center space-x-2"
                >
                  <Plus className="h-4 w-4" />
                  <span>Book Appointment</span>
                </Button>
              </div>
            </div>

            {/* Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Upcoming
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">{upcomingAppointments.length}</p>
                    <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <CalendarIcon className="h-6 w-6 text-blue-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Completed
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">{pastAppointments.length}</p>
                    <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center">
                      <CheckCircle className="h-6 w-6 text-green-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Total Visits
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">
                      {upcomingAppointments.length + pastAppointments.length}
                    </p>
                    <div className="h-12 w-12 bg-purple-100 rounded-full flex items-center justify-center">
                      <User className="h-6 w-6 text-purple-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Appointments Tabs */}
            <Tabs defaultValue="upcoming" className="space-y-6">
              <TabsList>
                <TabsTrigger value="upcoming">
                  Upcoming ({upcomingAppointments.length})
                </TabsTrigger>
                <TabsTrigger value="past">
                  Past ({pastAppointments.length})
                </TabsTrigger>
                <TabsTrigger value="cancelled">
                  Cancelled ({cancelledAppointments.length})
                </TabsTrigger>
              </TabsList>

              {/* Upcoming Appointments */}
              <TabsContent value="upcoming">
                <Card>
                  <CardHeader>
                    <CardTitle>Upcoming Appointments</CardTitle>
                    <CardDescription>Your scheduled appointments</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {upcomingAppointments.map((appointment) => (
                        <div
                          key={appointment.id}
                          className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors"
                        >
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex items-start space-x-3">
                              <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
                                <User className="h-6 w-6 text-blue-600" />
                              </div>
                              <div>
                                <p className="font-semibold text-gray-900">{appointment.doctor}</p>
                                <p className="text-sm text-gray-500">{appointment.specialty}</p>
                              </div>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Badge variant={getStatusColor(appointment.status)}>
                                {appointment.status}
                              </Badge>
                              {appointment.type === 'Virtual' && (
                                <Badge variant="outline" className="bg-purple-50">
                                  <Video className="h-3 w-3 mr-1" />
                                  Virtual
                                </Badge>
                              )}
                            </div>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                            <div className="flex items-center space-x-2 text-sm text-gray-600">
                              <CalendarIcon className="h-4 w-4" />
                              <span>{appointment.date}</span>
                            </div>
                            <div className="flex items-center space-x-2 text-sm text-gray-600">
                              <Clock className="h-4 w-4" />
                              <span>{appointment.time}</span>
                            </div>
                            <div className="flex items-center space-x-2 text-sm text-gray-600">
                              <MapPin className="h-4 w-4" />
                              <span>{appointment.location}</span>
                            </div>
                            {appointment.reason && (
                              <div className="flex items-center space-x-2 text-sm text-gray-600">
                                <FileText className="h-4 w-4" />
                                <span>{appointment.reason}</span>
                              </div>
                            )}
                          </div>

                          <div className="flex items-center space-x-2 pt-3 border-t">
                            {appointment.type === 'Virtual' && (
                              <Button size="sm">
                                <Video className="h-4 w-4 mr-1" />
                                Join Call
                              </Button>
                            )}
                            <Button size="sm" variant="outline">
                              Reschedule
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleCancelAppointment(appointment.id)}
                            >
                              Cancel
                            </Button>
                          </div>
                        </div>
                      ))}
                      {upcomingAppointments.length === 0 && (
                        <div className="text-center py-12 text-gray-500">
                          <CalendarIcon className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                          <p className="text-lg font-medium">No upcoming appointments</p>
                          <p className="text-sm">Book an appointment to get started</p>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Past Appointments */}
              <TabsContent value="past">
                <Card>
                  <CardHeader>
                    <CardTitle>Past Appointments</CardTitle>
                    <CardDescription>Your appointment history</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {pastAppointments.map((appointment) => (
                        <div
                          key={appointment.id}
                          className="p-4 border border-gray-200 rounded-lg"
                        >
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex items-start space-x-3">
                              <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center">
                                <CheckCircle className="h-6 w-6 text-green-600" />
                              </div>
                              <div>
                                <p className="font-semibold text-gray-900">{appointment.doctor}</p>
                                <p className="text-sm text-gray-500">{appointment.specialty}</p>
                              </div>
                            </div>
                            <Badge variant={getStatusColor(appointment.status)}>
                              {appointment.status}
                            </Badge>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            <div className="flex items-center space-x-2 text-sm text-gray-600">
                              <CalendarIcon className="h-4 w-4" />
                              <span>{appointment.date}</span>
                            </div>
                            <div className="flex items-center space-x-2 text-sm text-gray-600">
                              <Clock className="h-4 w-4" />
                              <span>{appointment.time}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Cancelled Appointments */}
              <TabsContent value="cancelled">
                <Card>
                  <CardHeader>
                    <CardTitle>Cancelled Appointments</CardTitle>
                    <CardDescription>Previously cancelled appointments</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {cancelledAppointments.length === 0 ? (
                        <div className="text-center py-12 text-gray-500">
                          <p>No cancelled appointments</p>
                        </div>
                      ) : (
                        cancelledAppointments.map((appointment) => (
                          <div
                            key={appointment.id}
                            className="p-4 border border-gray-200 rounded-lg opacity-75"
                          >
                            <div className="flex items-start justify-between">
                              <div>
                                <p className="font-semibold text-gray-900">{appointment.doctor}</p>
                                <p className="text-sm text-gray-500">{appointment.specialty}</p>
                              </div>
                              <Badge variant={getStatusColor(appointment.status)}>
                                {appointment.status}
                              </Badge>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </main>
      </div>

      {/* Book Appointment Dialog */}
      <Dialog open={showBookDialog} onOpenChange={setShowBookDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Book New Appointment</DialogTitle>
            <DialogDescription>Schedule an appointment with a doctor</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleBookAppointment}>
            <div className="grid grid-cols-2 gap-4 py-4">
              <div>
                <Label htmlFor="specialty">Specialty *</Label>
                <select
                  id="specialty"
                  name="specialty"
                  value={formData.specialty}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select specialty</option>
                  <option value="General Physician">General Physician</option>
                  <option value="Cardiologist">Cardiologist</option>
                  <option value="Dermatologist">Dermatologist</option>
                  <option value="Orthopedic">Orthopedic</option>
                  <option value="Pediatrician">Pediatrician</option>
                  <option value="Dentist">Dentist</option>
                </select>
              </div>
              <div>
                <Label htmlFor="doctor">Doctor *</Label>
                <select
                  id="doctor"
                  name="doctor"
                  value={formData.doctor}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select doctor</option>
                  <option value="Dr. Sarah Johnson">Dr. Sarah Johnson</option>
                  <option value="Dr. Michael Chen">Dr. Michael Chen</option>
                  <option value="Dr. Emily Rodriguez">Dr. Emily Rodriguez</option>
                  <option value="Dr. David Kim">Dr. David Kim</option>
                </select>
              </div>
              <div>
                <Label htmlFor="date">Preferred Date *</Label>
                <Input
                  id="date"
                  name="date"
                  type="date"
                  value={formData.date}
                  onChange={handleInputChange}
                  required
                  min={new Date().toISOString().split('T')[0]}
                />
              </div>
              <div>
                <Label htmlFor="time">Preferred Time *</Label>
                <Input
                  id="time"
                  name="time"
                  type="time"
                  value={formData.time}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="col-span-2">
                <Label htmlFor="type">Appointment Type *</Label>
                <select
                  id="type"
                  name="type"
                  value={formData.type}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="In-Person">In-Person Visit</option>
                  <option value="Virtual">Virtual Consultation</option>
                </select>
              </div>
              <div className="col-span-2">
                <Label htmlFor="reason">Reason for Visit *</Label>
                <Textarea
                  id="reason"
                  name="reason"
                  value={formData.reason}
                  onChange={handleInputChange}
                  required
                  placeholder="Brief description of your symptoms or reason for visit..."
                  rows={3}
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowBookDialog(false)}>
                Cancel
              </Button>
              <Button type="submit">Book Appointment</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
