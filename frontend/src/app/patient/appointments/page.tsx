'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/hooks/useAuth';
import { appointmentsAPI, type Appointment } from '@/lib/api/appointments';
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
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
  Loader2,
} from 'lucide-react';
import { toast } from 'sonner';

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

  // State
  const [showBookDialog, setShowBookDialog] = useState(false);
  const [showCancelDialog, setShowCancelDialog] = useState(false);
  const [selectedAppointment, setSelectedAppointment] = useState<Appointment | null>(null);
  const [formData, setFormData] = useState({
    specialty: '',
    doctor_name: '',
    appointment_date: '',
    appointment_time: '',
    type: 'In-Person',
    reason: '',
  });

  // Book appointment mutation
  const bookMutation = useMutation({
    mutationFn: (data: any) => appointmentsAPI.createAppointment(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      toast.success('Appointment booked successfully!');
      setShowBookDialog(false);
      setFormData({
        specialty: '',
        doctor_name: '',
        appointment_date: '',
        appointment_time: '',
        type: 'In-Person',
        reason: '',
      });
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to book appointment');
    },
  });

  // Cancel appointment mutation
  const cancelMutation = useMutation({
    mutationFn: (appointmentId: string) => appointmentsAPI.cancelAppointment(appointmentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      toast.success('Appointment cancelled successfully!');
      setShowCancelDialog(false);
      setSelectedAppointment(null);
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to cancel appointment');
    },
  });

  // Handlers
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleBookAppointment = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form
    if (!formData.specialty || !formData.doctor_name || !formData.appointment_date || !formData.appointment_time) {
      toast.error('Please fill in all required fields');
      return;
    }

    // Create appointment data
    const appointmentData = {
      patient_id: patientId,
      doctor_id: 'doctor001', // TODO: Get from doctor selection
      doctor_name: formData.doctor_name,
      specialty: formData.specialty,
      appointment_date: formData.appointment_date,
      appointment_time: formData.appointment_time,
      type: formData.type,
      reason: formData.reason,
      status: 'scheduled',
    };

    bookMutation.mutate(appointmentData);
  };

  const handleCancelClick = (appointment: Appointment) => {
    setSelectedAppointment(appointment);
    setShowCancelDialog(true);
  };

  const handleConfirmCancel = () => {
    if (selectedAppointment) {
      cancelMutation.mutate(selectedAppointment.appointment_id);
    }
  };

  // Helper functions
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'scheduled':
      case 'confirmed':
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
    switch (status.toLowerCase()) {
      case 'scheduled':
      case 'confirmed':
        return <Clock className="h-4 w-4 text-blue-600" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'cancelled':
        return <XCircle className="h-4 w-4 text-red-600" />;
      default:
        return null;
    }
  };

  // Filter appointments
  const upcomingAppointments = appointments.filter((a: Appointment) => 
    a.status === 'scheduled' || a.status === 'confirmed'
  );
  const pastAppointments = appointments.filter((a: Appointment) => a.status === 'completed');
  const cancelledAppointments = appointments.filter((a: Appointment) => a.status === 'cancelled');

  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

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
            {isLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                {[1, 2, 3].map((i) => (
                  <Card key={i}>
                    <CardHeader className="pb-2">
                      <Skeleton className="h-4 w-20" />
                    </CardHeader>
                    <CardContent>
                      <Skeleton className="h-8 w-12" />
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
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
                      Cancelled
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <p className="text-3xl font-bold text-gray-900">{cancelledAppointments.length}</p>
                      <div className="h-12 w-12 bg-red-100 rounded-full flex items-center justify-center">
                        <XCircle className="h-6 w-6 text-red-600" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Appointments Tabs */}
            <Tabs defaultValue="upcoming" className="space-y-6">
              <TabsList>
                <TabsTrigger value="upcoming">Upcoming ({upcomingAppointments.length})</TabsTrigger>
                <TabsTrigger value="past">Past ({pastAppointments.length})</TabsTrigger>
                <TabsTrigger value="cancelled">Cancelled ({cancelledAppointments.length})</TabsTrigger>
              </TabsList>

              {/* Upcoming Appointments */}
              <TabsContent value="upcoming">
                {isLoading ? (
                  <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                      <Card key={i}>
                        <CardContent className="p-6">
                          <Skeleton className="h-6 w-full mb-4" />
                          <Skeleton className="h-4 w-3/4" />
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                ) : upcomingAppointments.length === 0 ? (
                  <Card>
                    <CardContent className="p-12 text-center">
                      <CalendarIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">No upcoming appointments</p>
                      <Button
                        onClick={() => setShowBookDialog(true)}
                        className="mt-4"
                      >
                        Book an Appointment
                      </Button>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="space-y-4">
                    {upcomingAppointments.map((appointment: Appointment) => (
                      <Card key={appointment.appointment_id}>
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3 mb-3">
                                <Badge variant={getStatusColor(appointment.status)}>
                                  <div className="flex items-center space-x-1">
                                    {getStatusIcon(appointment.status)}
                                    <span className="capitalize">{appointment.status}</span>
                                  </div>
                                </Badge>
                                <Badge variant="outline">{appointment.type}</Badge>
                              </div>

                              <div className="grid grid-cols-2 gap-4">
                                <div>
                                  <div className="flex items-center text-gray-600 mb-2">
                                    <User className="h-4 w-4 mr-2" />
                                    <span className="font-medium">{appointment.doctor_name}</span>
                                  </div>
                                  <div className="flex items-center text-gray-600 mb-2">
                                    <FileText className="h-4 w-4 mr-2" />
                                    <span className="text-sm">{appointment.specialty}</span>
                                  </div>
                                </div>

                                <div>
                                  <div className="flex items-center text-gray-600 mb-2">
                                    <CalendarIcon className="h-4 w-4 mr-2" />
                                    <span className="text-sm">{formatDate(appointment.appointment_date)}</span>
                                  </div>
                                  <div className="flex items-center text-gray-600 mb-2">
                                    <Clock className="h-4 w-4 mr-2" />
                                    <span className="text-sm">{appointment.appointment_time}</span>
                                  </div>
                                  {appointment.location && (
                                    <div className="flex items-center text-gray-600">
                                      <MapPin className="h-4 w-4 mr-2" />
                                      <span className="text-sm">{appointment.location}</span>
                                    </div>
                                  )}
                                </div>
                              </div>

                              {appointment.reason && (
                                <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                                  <p className="text-sm text-gray-700">
                                    <span className="font-medium">Reason: </span>
                                    {appointment.reason}
                                  </p>
                                </div>
                              )}
                            </div>

                            <div className="flex flex-col space-y-2 ml-4">
                              {appointment.type === 'Virtual' && (
                                <Button size="sm" className="whitespace-nowrap">
                                  <Video className="h-4 w-4 mr-2" />
                                  Join Call
                                </Button>
                              )}
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleCancelClick(appointment)}
                                disabled={cancelMutation.isPending}
                              >
                                Cancel
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </TabsContent>

              {/* Past Appointments */}
              <TabsContent value="past">
                {pastAppointments.length === 0 ? (
                  <Card>
                    <CardContent className="p-12 text-center">
                      <CheckCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">No past appointments</p>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="space-y-4">
                    {pastAppointments.map((appointment: Appointment) => (
                      <Card key={appointment.appointment_id}>
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3 mb-3">
                                <Badge variant={getStatusColor(appointment.status)}>
                                  <div className="flex items-center space-x-1">
                                    {getStatusIcon(appointment.status)}
                                    <span className="capitalize">{appointment.status}</span>
                                  </div>
                                </Badge>
                              </div>

                              <div className="grid grid-cols-2 gap-4">
                                <div>
                                  <div className="flex items-center text-gray-600 mb-2">
                                    <User className="h-4 w-4 mr-2" />
                                    <span className="font-medium">{appointment.doctor_name}</span>
                                  </div>
                                  <div className="flex items-center text-gray-600">
                                    <FileText className="h-4 w-4 mr-2" />
                                    <span className="text-sm">{appointment.specialty}</span>
                                  </div>
                                </div>

                                <div>
                                  <div className="flex items-center text-gray-600 mb-2">
                                    <CalendarIcon className="h-4 w-4 mr-2" />
                                    <span className="text-sm">{formatDate(appointment.appointment_date)}</span>
                                  </div>
                                  <div className="flex items-center text-gray-600">
                                    <Clock className="h-4 w-4 mr-2" />
                                    <span className="text-sm">{appointment.appointment_time}</span>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </TabsContent>

              {/* Cancelled Appointments */}
              <TabsContent value="cancelled">
                {cancelledAppointments.length === 0 ? (
                  <Card>
                    <CardContent className="p-12 text-center">
                      <XCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">No cancelled appointments</p>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="space-y-4">
                    {cancelledAppointments.map((appointment: Appointment) => (
                      <Card key={appointment.appointment_id}>
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3 mb-3">
                                <Badge variant={getStatusColor(appointment.status)}>
                                  <div className="flex items-center space-x-1">
                                    {getStatusIcon(appointment.status)}
                                    <span className="capitalize">{appointment.status}</span>
                                  </div>
                                </Badge>
                              </div>

                              <div className="grid grid-cols-2 gap-4">
                                <div>
                                  <div className="flex items-center text-gray-600 mb-2">
                                    <User className="h-4 w-4 mr-2" />
                                    <span className="font-medium">{appointment.doctor_name}</span>
                                  </div>
                                  <div className="flex items-center text-gray-600">
                                    <FileText className="h-4 w-4 mr-2" />
                                    <span className="text-sm">{appointment.specialty}</span>
                                  </div>
                                </div>

                                <div>
                                  <div className="flex items-center text-gray-600 mb-2">
                                    <CalendarIcon className="h-4 w-4 mr-2" />
                                    <span className="text-sm">{formatDate(appointment.appointment_date)}</span>
                                  </div>
                                  <div className="flex items-center text-gray-600">
                                    <Clock className="h-4 w-4 mr-2" />
                                    <span className="text-sm">{appointment.appointment_time}</span>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </div>
        </main>
      </div>

      {/* Book Appointment Dialog */}
      <Dialog open={showBookDialog} onOpenChange={setShowBookDialog}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>Book New Appointment</DialogTitle>
            <DialogDescription>
              Fill in the details to schedule your appointment
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleBookAppointment}>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="specialty">Specialty *</Label>
                <Select
                  value={formData.specialty}
                  onValueChange={(value) => setFormData({ ...formData, specialty: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select specialty" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Cardiology">Cardiology</SelectItem>
                    <SelectItem value="Dermatology">Dermatology</SelectItem>
                    <SelectItem value="General Medicine">General Medicine</SelectItem>
                    <SelectItem value="Orthopedics">Orthopedics</SelectItem>
                    <SelectItem value="Pediatrics">Pediatrics</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="doctor_name">Doctor Name *</Label>
                <Input
                  id="doctor_name"
                  name="doctor_name"
                  value={formData.doctor_name}
                  onChange={handleInputChange}
                  placeholder="e.g., Dr. Smith"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="appointment_date">Date *</Label>
                  <Input
                    id="appointment_date"
                    name="appointment_date"
                    type="date"
                    value={formData.appointment_date}
                    onChange={handleInputChange}
                    min={new Date().toISOString().split('T')[0]}
                    required
                  />
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="appointment_time">Time *</Label>
                  <Input
                    id="appointment_time"
                    name="appointment_time"
                    type="time"
                    value={formData.appointment_time}
                    onChange={handleInputChange}
                    required
                  />
                </div>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="type">Appointment Type</Label>
                <Select
                  value={formData.type}
                  onValueChange={(value) => setFormData({ ...formData, type: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="In-Person">In-Person</SelectItem>
                    <SelectItem value="Virtual">Virtual</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="reason">Reason for Visit</Label>
                <Textarea
                  id="reason"
                  name="reason"
                  value={formData.reason}
                  onChange={handleInputChange}
                  placeholder="Describe your symptoms or reason for visit..."
                  rows={3}
                />
              </div>
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setShowBookDialog(false)}
                disabled={bookMutation.isPending}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={bookMutation.isPending}>
                {bookMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Booking...
                  </>
                ) : (
                  'Book Appointment'
                )}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Cancel Appointment Dialog */}
      <Dialog open={showCancelDialog} onOpenChange={setShowCancelDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Cancel Appointment</DialogTitle>
            <DialogDescription>
              Are you sure you want to cancel this appointment?
            </DialogDescription>
          </DialogHeader>
          {selectedAppointment && (
            <div className="py-4">
              <div className="space-y-2 text-sm">
                <p><strong>Doctor:</strong> {selectedAppointment.doctor_name}</p>
                <p><strong>Date:</strong> {formatDate(selectedAppointment.appointment_date)}</p>
                <p><strong>Time:</strong> {selectedAppointment.appointment_time}</p>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowCancelDialog(false)}
              disabled={cancelMutation.isPending}
            >
              Keep Appointment
            </Button>
            <Button
              variant="destructive"
              onClick={handleConfirmCancel}
              disabled={cancelMutation.isPending}
            >
              {cancelMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Cancelling...
                </>
              ) : (
                'Yes, Cancel'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
