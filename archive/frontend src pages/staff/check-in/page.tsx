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
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';
import {
  UserCheck,
  Search,
  Clock,
  User,
  CheckCircle,
  AlertCircle,
  Phone,
  Mail,
  Calendar,
  ClipboardCheck,
  FileText,
} from 'lucide-react';
import axios from 'axios';

interface Appointment {
  appointment_id: string;
  patient_id: string;
  patient_name: string;
  patient_phone?: string;
  patient_email?: string;
  patient_dob?: string;
  doctor_id: string;
  doctor_name: string;
  appointment_date: string;
  appointment_time: string;
  type: string;
  status: string;
  reason?: string;
  checked_in: boolean;
  check_in_time?: string;
  check_in_notes?: string;
}

export default function StaffCheckIn() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const staffId = 'staff001'; // TODO: Get from authenticated user

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAppointment, setSelectedAppointment] = useState<Appointment | null>(null);
  const [checkInDialogOpen, setCheckInDialogOpen] = useState(false);
  const [checkInNotes, setCheckInNotes] = useState('');

  // Fetch today's appointments
  const { data: appointmentsData, isLoading } = useQuery({
    queryKey: ['check-in-appointments'],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `http://localhost:8000/api/appointments`,
        {
          params: {
            date: new Date().toISOString().split('T')[0],
          },
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data?.data?.appointments || [];
    },
  });

  // Check-in mutation
  const checkInMutation = useMutation({
    mutationFn: async ({ appointmentId, notes }: { appointmentId: string; notes: string }) => {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `http://localhost:8000/api/appointments/${appointmentId}/check-in`,
        {
          check_in_time: new Date().toISOString(),
          check_in_notes: notes,
          checked_in_by: staffId,
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
      queryClient.invalidateQueries({ queryKey: ['check-in-appointments'] });
      setCheckInDialogOpen(false);
      setCheckInNotes('');
      setSelectedAppointment(null);
    },
  });

  const appointments: Appointment[] = appointmentsData || [];

  // Filter appointments
  const filteredAppointments = appointments.filter((apt) => {
    if (
      searchQuery &&
      !apt.patient_name.toLowerCase().includes(searchQuery.toLowerCase()) &&
      !apt.patient_id.toLowerCase().includes(searchQuery.toLowerCase())
    ) {
      return false;
    }
    return true;
  });

  // Separate into pending and checked-in
  const pendingCheckIns = filteredAppointments.filter(
    (a) => !a.checked_in && a.status !== 'cancelled'
  );
  const checkedInAppointments = filteredAppointments.filter((a) => a.checked_in);

  const formatTime = (timeString: string) => {
    return new Date(`2000-01-01T${timeString}`).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  const handleCheckIn = (appointment: Appointment) => {
    setSelectedAppointment(appointment);
    setCheckInNotes('');
    setCheckInDialogOpen(true);
  };

  const submitCheckIn = () => {
    if (selectedAppointment) {
      checkInMutation.mutate({
        appointmentId: selectedAppointment.appointment_id,
        notes: checkInNotes,
      });
    }
  };

  const calculateAge = (dob: string) => {
    const birthDate = new Date(dob);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar role="staff" />
        <main className="flex-1 ml-64 mt-16">
          <div className="p-8">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Patient Check-in</h1>
              <p className="text-gray-600">Process patient arrivals and check-ins</p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Pending Check-ins
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-orange-600">{pendingCheckIns.length}</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Checked In Today
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-green-600">{checkedInAppointments.length}</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Total Appointments
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-gray-900">{appointments.length}</p>
                </CardContent>
              </Card>
            </div>

            {/* Search */}
            <Card className="mb-6">
              <CardContent className="pt-6">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <Input
                    placeholder="Search by patient name or ID..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-12 text-lg h-14"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Pending Check-ins */}
            <div className="mb-8">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-gray-900">
                  Pending Check-ins ({pendingCheckIns.length})
                </h2>
              </div>

              {isLoading ? (
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <Card key={i}>
                      <CardContent className="pt-6">
                        <Skeleton className="h-24 w-full" />
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : pendingCheckIns.length === 0 ? (
                <Card>
                  <CardContent className="pt-12 pb-12 text-center">
                    <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
                    <p className="text-gray-600 text-lg mb-2">All patients checked in!</p>
                    <p className="text-gray-500 text-sm">No pending check-ins at the moment</p>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {pendingCheckIns.map((appointment) => (
                    <Card
                      key={appointment.appointment_id}
                      className="border-orange-200 bg-orange-50 hover:shadow-lg transition-shadow"
                    >
                      <CardContent className="pt-6">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center space-x-4">
                            <div className="h-16 w-16 bg-orange-100 rounded-full flex items-center justify-center">
                              <span className="text-orange-600 font-bold text-xl">
                                {appointment.patient_name.charAt(0)}
                              </span>
                            </div>
                            <div>
                              <h3 className="text-xl font-bold text-gray-900">
                                {appointment.patient_name}
                              </h3>
                              <p className="text-sm text-gray-600">ID: {appointment.patient_id}</p>
                              {appointment.patient_dob && (
                                <p className="text-sm text-gray-600">
                                  Age: {calculateAge(appointment.patient_dob)} years
                                </p>
                              )}
                            </div>
                          </div>
                          <Badge variant="outline" className="bg-white">
                            <AlertCircle className="h-3 w-3 mr-1" />
                            Waiting
                          </Badge>
                        </div>

                        <div className="space-y-2 mb-4 p-3 bg-white rounded-lg">
                          <div className="flex items-center space-x-2 text-sm">
                            <Clock className="h-4 w-4 text-gray-400" />
                            <span className="font-medium">
                              {formatTime(appointment.appointment_time)}
                            </span>
                          </div>
                          <div className="flex items-center space-x-2 text-sm">
                            <User className="h-4 w-4 text-gray-400" />
                            <span>Dr. {appointment.doctor_name}</span>
                          </div>
                          <div className="flex items-center space-x-2 text-sm">
                            <ClipboardCheck className="h-4 w-4 text-gray-400" />
                            <span className="capitalize">{appointment.type}</span>
                          </div>
                          {appointment.reason && (
                            <div className="flex items-start space-x-2 text-sm">
                              <FileText className="h-4 w-4 text-gray-400 mt-0.5" />
                              <span className="text-gray-600">{appointment.reason}</span>
                            </div>
                          )}
                        </div>

                        {appointment.patient_phone && (
                          <div className="flex items-center space-x-4 mb-4 text-sm">
                            <div className="flex items-center space-x-2">
                              <Phone className="h-4 w-4 text-gray-400" />
                              <span>{appointment.patient_phone}</span>
                            </div>
                            {appointment.patient_email && (
                              <div className="flex items-center space-x-2">
                                <Mail className="h-4 w-4 text-gray-400" />
                                <span className="truncate">{appointment.patient_email}</span>
                              </div>
                            )}
                          </div>
                        )}

                        <Button
                          onClick={() => handleCheckIn(appointment)}
                          className="w-full"
                          size="lg"
                        >
                          <UserCheck className="h-5 w-5 mr-2" />
                          Check In Patient
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>

            {/* Checked-in Patients */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-gray-900">
                  Checked In Today ({checkedInAppointments.length})
                </h2>
              </div>

              {checkedInAppointments.length === 0 ? (
                <Card>
                  <CardContent className="pt-8 pb-8 text-center">
                    <p className="text-gray-600">No patients checked in yet</p>
                  </CardContent>
                </Card>
              ) : (
                <div className="space-y-3">
                  {checkedInAppointments.map((appointment) => (
                    <Card
                      key={appointment.appointment_id}
                      className="border-green-200 bg-green-50"
                    >
                      <CardContent className="pt-4 pb-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center">
                              <CheckCircle className="h-6 w-6 text-green-600" />
                            </div>
                            <div>
                              <h3 className="font-semibold text-gray-900">
                                {appointment.patient_name}
                              </h3>
                              <div className="flex items-center space-x-4 text-sm text-gray-600">
                                <span>Appointment: {formatTime(appointment.appointment_time)}</span>
                                <span>•</span>
                                <span>Dr. {appointment.doctor_name}</span>
                                {appointment.check_in_time && (
                                  <>
                                    <span>•</span>
                                    <span>Checked in: {formatTime(appointment.check_in_time)}</span>
                                  </>
                                )}
                              </div>
                              {appointment.check_in_notes && (
                                <p className="text-sm text-gray-600 mt-1">
                                  Notes: {appointment.check_in_notes}
                                </p>
                              )}
                            </div>
                          </div>
                          <Badge variant="default">
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Checked In
                          </Badge>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </div>
        </main>
      </div>

      {/* Check-in Dialog */}
      <Dialog open={checkInDialogOpen} onOpenChange={setCheckInDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Check In Patient</DialogTitle>
            <DialogDescription>
              Confirm patient arrival and complete check-in process
            </DialogDescription>
          </DialogHeader>

          {selectedAppointment && (
            <div className="space-y-6">
              {/* Patient Info */}
              <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                <div className="flex items-center space-x-4 mb-3">
                  <div className="h-16 w-16 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-blue-600 font-bold text-2xl">
                      {selectedAppointment.patient_name.charAt(0)}
                    </span>
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">
                      {selectedAppointment.patient_name}
                    </h3>
                    <p className="text-sm text-gray-600">
                      ID: {selectedAppointment.patient_id}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <Label className="text-gray-600">Appointment Time</Label>
                    <p className="font-medium">
                      {formatTime(selectedAppointment.appointment_time)}
                    </p>
                  </div>
                  <div>
                    <Label className="text-gray-600">Doctor</Label>
                    <p className="font-medium">Dr. {selectedAppointment.doctor_name}</p>
                  </div>
                  <div>
                    <Label className="text-gray-600">Type</Label>
                    <p className="font-medium capitalize">{selectedAppointment.type}</p>
                  </div>
                  <div>
                    <Label className="text-gray-600">Current Time</Label>
                    <p className="font-medium">
                      {new Date().toLocaleTimeString('en-US', {
                        hour: 'numeric',
                        minute: '2-digit',
                        hour12: true,
                      })}
                    </p>
                  </div>
                </div>

                {selectedAppointment.reason && (
                  <div className="mt-3">
                    <Label className="text-gray-600">Reason for Visit</Label>
                    <p className="font-medium">{selectedAppointment.reason}</p>
                  </div>
                )}
              </div>

              {/* Check-in Notes */}
              <div>
                <Label htmlFor="check_in_notes">
                  Check-in Notes (Optional)
                </Label>
                <Textarea
                  id="check_in_notes"
                  value={checkInNotes}
                  onChange={(e) => setCheckInNotes(e.target.value)}
                  placeholder="Any special notes or observations during check-in..."
                  rows={4}
                  className="mt-2"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Examples: Patient arrived early, brought insurance card, special accommodations needed, etc.
                </p>
              </div>

              {/* Confirmation */}
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                  <div>
                    <p className="font-medium text-green-900">Ready to check in</p>
                    <p className="text-sm text-green-700">
                      Patient will be marked as arrived and doctor will be notified
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setCheckInDialogOpen(false);
                setCheckInNotes('');
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={submitCheckIn}
              disabled={checkInMutation.isPending}
              size="lg"
            >
              <UserCheck className="h-5 w-5 mr-2" />
              Complete Check-in
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
