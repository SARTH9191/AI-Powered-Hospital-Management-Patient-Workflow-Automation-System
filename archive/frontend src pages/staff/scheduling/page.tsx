'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
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
  User,
  Stethoscope,
  MapPin,
  Plus,
  Search,
  Filter,
  CheckCircle,
  XCircle,
  Edit,
  Trash2,
} from 'lucide-react';
import { toast } from 'sonner';

interface Appointment {
  id: string;
  patientName: string;
  patientId: string;
  doctorName: string;
  date: string;
  time: string;
  type: string;
  status: 'scheduled' | 'confirmed' | 'cancelled' | 'completed';
  location: string;
  notes?: string;
}

export default function AppointmentScheduling() {
  const [appointments, setAppointments] = useState<Appointment[]>([
    {
      id: 'APT001',
      patientName: 'Emily Davis',
      patientId: 'P001',
      doctorName: 'Dr. Sarah Johnson',
      date: '2024-10-20',
      time: '09:00 AM',
      type: 'Checkup',
      status: 'confirmed',
      location: 'Room 101',
      notes: 'Annual physical examination',
    },
    {
      id: 'APT002',
      patientName: 'James Wilson',
      patientId: 'P002',
      doctorName: 'Dr. Michael Chen',
      date: '2024-10-20',
      time: '10:30 AM',
      type: 'Consultation',
      status: 'scheduled',
      location: 'Room 203',
      notes: 'Follow-up for lab results',
    },
    {
      id: 'APT003',
      patientName: 'Sarah Miller',
      patientId: 'P003',
      doctorName: 'Dr. Emily Rodriguez',
      date: '2024-10-20',
      time: '02:00 PM',
      type: 'Follow-up',
      status: 'confirmed',
      location: 'Room 105',
    },
    {
      id: 'APT004',
      patientName: 'Michael Brown',
      patientId: 'P004',
      doctorName: 'Dr. Sarah Johnson',
      date: '2024-10-21',
      time: '11:00 AM',
      type: 'Emergency',
      status: 'scheduled',
      location: 'Emergency Room',
      notes: 'Urgent care needed',
    },
    {
      id: 'APT005',
      patientName: 'Linda Taylor',
      patientId: 'P005',
      doctorName: 'Dr. David Kim',
      date: '2024-10-21',
      time: '03:30 PM',
      type: 'Virtual',
      status: 'confirmed',
      location: 'Online',
    },
  ]);

  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [showScheduleDialog, setShowScheduleDialog] = useState(false);
  const [formData, setFormData] = useState({
    patientId: '',
    patientName: '',
    doctorName: '',
    date: '',
    time: '',
    type: '',
    location: '',
    notes: '',
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSchedule = (e: React.FormEvent) => {
    e.preventDefault();
    const newAppointment: Appointment = {
      id: `APT${(appointments.length + 1).toString().padStart(3, '0')}`,
      patientName: formData.patientName,
      patientId: formData.patientId,
      doctorName: formData.doctorName,
      date: formData.date,
      time: formData.time,
      type: formData.type,
      status: 'scheduled',
      location: formData.location,
      notes: formData.notes,
    };
    setAppointments([...appointments, newAppointment]);
    toast.success('Appointment scheduled successfully!');
    setShowScheduleDialog(false);
    setFormData({
      patientId: '',
      patientName: '',
      doctorName: '',
      date: '',
      time: '',
      type: '',
      location: '',
      notes: '',
    });
  };

  const handleStatusChange = (id: string, status: Appointment['status']) => {
    setAppointments(appointments.map(apt => 
      apt.id === id ? { ...apt, status } : apt
    ));
    toast.success(`Appointment ${status}`);
  };

  const handleDelete = (id: string) => {
    setAppointments(appointments.filter(apt => apt.id !== id));
    toast.success('Appointment deleted');
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'default';
      case 'scheduled':
        return 'secondary';
      case 'cancelled':
        return 'destructive';
      case 'completed':
        return 'outline';
      default:
        return 'default';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'Checkup':
        return 'bg-blue-100 text-blue-800';
      case 'Consultation':
        return 'bg-purple-100 text-purple-800';
      case 'Follow-up':
        return 'bg-green-100 text-green-800';
      case 'Emergency':
        return 'bg-red-100 text-red-800';
      case 'Virtual':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredAppointments = appointments.filter((apt) => {
    const matchesSearch = `${apt.patientName} ${apt.doctorName} ${apt.id}`
      .toLowerCase()
      .includes(searchQuery.toLowerCase());
    const matchesStatus = filterStatus === 'all' || apt.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const todayAppointments = appointments.filter(apt => {
    const today = new Date().toISOString().split('T')[0];
    return apt.date === today;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar role="staff" />
        <main className="flex-1 ml-64 mt-16">
          <div className="p-8">
            {/* Header */}
            <div className="mb-8">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900 mb-2">Appointment Scheduling</h1>
                  <p className="text-gray-600">Schedule and manage patient appointments</p>
                </div>
                <Button
                  onClick={() => setShowScheduleDialog(true)}
                  className="flex items-center space-x-2"
                >
                  <Plus className="h-4 w-4" />
                  <span>Schedule Appointment</span>
                </Button>
              </div>
            </div>

            {/* Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Total Appointments
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">{appointments.length}</p>
                    <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <CalendarIcon className="h-6 w-6 text-blue-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Today's Appointments
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">{todayAppointments.length}</p>
                    <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center">
                      <Clock className="h-6 w-6 text-green-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Confirmed
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">
                      {appointments.filter(a => a.status === 'confirmed').length}
                    </p>
                    <div className="h-12 w-12 bg-purple-100 rounded-full flex items-center justify-center">
                      <CheckCircle className="h-6 w-6 text-purple-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Pending
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">
                      {appointments.filter(a => a.status === 'scheduled').length}
                    </p>
                    <div className="h-12 w-12 bg-orange-100 rounded-full flex items-center justify-center">
                      <Clock className="h-6 w-6 text-orange-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Filters */}
            <Card className="mb-6">
              <CardContent className="pt-6">
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="flex-1 relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      type="text"
                      placeholder="Search by patient, doctor, or appointment ID..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  <div className="flex items-center space-x-2">
                    <Filter className="h-4 w-4 text-gray-400" />
                    <select
                      value={filterStatus}
                      onChange={(e) => setFilterStatus(e.target.value)}
                      className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="all">All Status</option>
                      <option value="scheduled">Scheduled</option>
                      <option value="confirmed">Confirmed</option>
                      <option value="cancelled">Cancelled</option>
                      <option value="completed">Completed</option>
                    </select>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Appointments List */}
            <Card>
              <CardHeader>
                <CardTitle>All Appointments</CardTitle>
                <CardDescription>Manage and track all scheduled appointments</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {filteredAppointments.map((appointment) => (
                    <div
                      key={appointment.id}
                      className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <Badge variant="outline">{appointment.id}</Badge>
                            <Badge className={getTypeColor(appointment.type)}>
                              {appointment.type}
                            </Badge>
                            <Badge variant={getStatusColor(appointment.status)}>
                              {appointment.status}
                            </Badge>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <div className="flex items-center space-x-2 mb-2">
                                <User className="h-4 w-4 text-gray-400" />
                                <div>
                                  <p className="text-sm font-medium text-gray-900">
                                    {appointment.patientName}
                                  </p>
                                  <p className="text-xs text-gray-500">
                                    Patient ID: {appointment.patientId}
                                  </p>
                                </div>
                              </div>

                              <div className="flex items-center space-x-2">
                                <Stethoscope className="h-4 w-4 text-gray-400" />
                                <p className="text-sm text-gray-600">{appointment.doctorName}</p>
                              </div>
                            </div>

                            <div>
                              <div className="flex items-center space-x-2 mb-2">
                                <CalendarIcon className="h-4 w-4 text-gray-400" />
                                <p className="text-sm text-gray-600">
                                  {appointment.date} at {appointment.time}
                                </p>
                              </div>

                              <div className="flex items-center space-x-2">
                                <MapPin className="h-4 w-4 text-gray-400" />
                                <p className="text-sm text-gray-600">{appointment.location}</p>
                              </div>
                            </div>
                          </div>

                          {appointment.notes && (
                            <div className="mt-3 p-2 bg-gray-50 rounded">
                              <p className="text-xs text-gray-600">
                                <span className="font-medium">Notes:</span> {appointment.notes}
                              </p>
                            </div>
                          )}
                        </div>

                        <div className="flex flex-col space-y-2 ml-4">
                          {appointment.status === 'scheduled' && (
                            <Button
                              size="sm"
                              onClick={() => handleStatusChange(appointment.id, 'confirmed')}
                            >
                              <CheckCircle className="h-4 w-4 mr-1" />
                              Confirm
                            </Button>
                          )}
                          {appointment.status !== 'cancelled' && appointment.status !== 'completed' && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleStatusChange(appointment.id, 'cancelled')}
                            >
                              <XCircle className="h-4 w-4 mr-1" />
                              Cancel
                            </Button>
                          )}
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleDelete(appointment.id)}
                          >
                            <Trash2 className="h-4 w-4 text-red-600" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>

      {/* Schedule Dialog */}
      <Dialog open={showScheduleDialog} onOpenChange={setShowScheduleDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Schedule New Appointment</DialogTitle>
            <DialogDescription>Fill in the appointment details below</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSchedule}>
            <div className="grid grid-cols-2 gap-4 py-4">
              <div>
                <Label htmlFor="patientId">Patient ID *</Label>
                <Input
                  id="patientId"
                  name="patientId"
                  value={formData.patientId}
                  onChange={handleInputChange}
                  required
                  placeholder="P001"
                />
              </div>
              <div>
                <Label htmlFor="patientName">Patient Name *</Label>
                <Input
                  id="patientName"
                  name="patientName"
                  value={formData.patientName}
                  onChange={handleInputChange}
                  required
                  placeholder="John Doe"
                />
              </div>
              <div>
                <Label htmlFor="doctorName">Doctor *</Label>
                <select
                  id="doctorName"
                  name="doctorName"
                  value={formData.doctorName}
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
                <Label htmlFor="type">Appointment Type *</Label>
                <select
                  id="type"
                  name="type"
                  value={formData.type}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select type</option>
                  <option value="Checkup">Checkup</option>
                  <option value="Consultation">Consultation</option>
                  <option value="Follow-up">Follow-up</option>
                  <option value="Emergency">Emergency</option>
                  <option value="Virtual">Virtual</option>
                </select>
              </div>
              <div>
                <Label htmlFor="date">Date *</Label>
                <Input
                  id="date"
                  name="date"
                  type="date"
                  value={formData.date}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div>
                <Label htmlFor="time">Time *</Label>
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
                <Label htmlFor="location">Location *</Label>
                <Input
                  id="location"
                  name="location"
                  value={formData.location}
                  onChange={handleInputChange}
                  required
                  placeholder="Room 101"
                />
              </div>
              <div className="col-span-2">
                <Label htmlFor="notes">Notes</Label>
                <Textarea
                  id="notes"
                  name="notes"
                  value={formData.notes}
                  onChange={handleInputChange}
                  placeholder="Additional notes or instructions..."
                  rows={3}
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowScheduleDialog(false)}>
                Cancel
              </Button>
              <Button type="submit">Schedule Appointment</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
