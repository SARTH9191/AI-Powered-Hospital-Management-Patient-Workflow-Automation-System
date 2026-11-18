'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
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
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Calendar,
  Clock,
  ChevronLeft,
  ChevronRight,
  Plus,
  Video,
  MapPin,
  User,
  Phone,
  Edit,
  Trash2,
} from 'lucide-react';
import { toast } from 'sonner';
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';

interface Appointment {
  id: string;
  patientName: string;
  patientId: string;
  date: string;
  time: string;
  duration: number;
  type: 'checkup' | 'consultation' | 'follow-up' | 'emergency' | 'virtual';
  status: 'confirmed' | 'pending' | 'completed' | 'cancelled';
  notes?: string;
  location?: string;
}

export default function AppointmentsPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [viewMode, setViewMode] = useState<'day' | 'week' | 'month'>('week');
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingAppointment, setEditingAppointment] = useState<Appointment | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [newAppointment, setNewAppointment] = useState({
    patientName: '',
    patientId: '',
    date: '',
    time: '',
    duration: 30,
    type: 'checkup' as const,
    notes: '',
    location: 'Clinic Room 1',
  });

  useEffect(() => {
    // Mock appointments data
    const mockAppointments: Appointment[] = [
      {
        id: '1',
        patientName: 'Emily Davis',
        patientId: 'P1234',
        date: '2024-10-18',
        time: '09:00',
        duration: 30,
        type: 'checkup',
        status: 'confirmed',
        notes: 'Annual checkup',
        location: 'Clinic Room 1',
      },
      {
        id: '2',
        patientName: 'James Wilson',
        patientId: 'P1235',
        date: '2024-10-18',
        time: '10:00',
        duration: 45,
        type: 'consultation',
        status: 'confirmed',
        notes: 'Discuss lab results',
        location: 'Clinic Room 2',
      },
      {
        id: '3',
        patientName: 'Sarah Miller',
        patientId: 'P1236',
        date: '2024-10-18',
        time: '11:30',
        duration: 30,
        type: 'follow-up',
        status: 'pending',
        notes: 'Post-surgery checkup',
        location: 'Clinic Room 1',
      },
      {
        id: '4',
        patientName: 'Michael Brown',
        patientId: 'P1237',
        date: '2024-10-18',
        time: '14:00',
        duration: 60,
        type: 'virtual',
        status: 'confirmed',
        notes: 'Telemedicine consultation',
        location: 'Virtual',
      },
      {
        id: '5',
        patientName: 'Linda Taylor',
        patientId: 'P1238',
        date: '2024-10-18',
        time: '15:30',
        duration: 30,
        type: 'follow-up',
        status: 'confirmed',
        notes: 'Medication review',
        location: 'Clinic Room 3',
      },
      {
        id: '6',
        patientName: 'Robert Johnson',
        patientId: 'P1239',
        date: '2024-10-19',
        time: '09:30',
        duration: 45,
        type: 'checkup',
        status: 'confirmed',
        notes: 'Routine physical',
        location: 'Clinic Room 1',
      },
      {
        id: '7',
        patientName: 'Mary Smith',
        patientId: 'P1240',
        date: '2024-10-19',
        time: '11:00',
        duration: 30,
        type: 'consultation',
        status: 'pending',
        notes: 'New patient consultation',
        location: 'Clinic Room 2',
      },
    ];

    setTimeout(() => {
      setAppointments(mockAppointments);
      setIsLoading(false);
    }, 500);
  }, []);

  const handleAddAppointment = () => {
    const appointment: Appointment = {
      id: Date.now().toString(),
      patientName: newAppointment.patientName,
      patientId: newAppointment.patientId,
      date: newAppointment.date,
      time: newAppointment.time,
      duration: newAppointment.duration,
      type: newAppointment.type,
      status: 'confirmed',
      notes: newAppointment.notes,
      location: newAppointment.location,
    };

    setAppointments([...appointments, appointment]);
    toast.success('Appointment scheduled', {
      description: `${newAppointment.patientName} on ${newAppointment.date} at ${newAppointment.time}`,
    });

    setIsAddDialogOpen(false);
    setNewAppointment({
      patientName: '',
      patientId: '',
      date: '',
      time: '',
      duration: 30,
      type: 'checkup',
      notes: '',
      location: 'Clinic Room 1',
    });
  };

  const handleEditAppointment = () => {
    if (!editingAppointment) return;

    setAppointments(appointments.map((apt) => (apt.id === editingAppointment.id ? editingAppointment : apt)));
    toast.success('Appointment updated successfully');
    setIsEditDialogOpen(false);
    setEditingAppointment(null);
  };

  const handleDeleteAppointment = (id: string) => {
    setAppointments(appointments.filter((apt) => apt.id !== id));
    toast.success('Appointment cancelled');
  };

  const getTypeColor = (type: string) => {
    const colors = {
      checkup: 'bg-blue-100 text-blue-800',
      consultation: 'bg-purple-100 text-purple-800',
      'follow-up': 'bg-green-100 text-green-800',
      emergency: 'bg-red-100 text-red-800',
      virtual: 'bg-orange-100 text-orange-800',
    };
    return colors[type as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const getStatusColor = (status: string) => {
    const colors = {
      confirmed: 'bg-green-100 text-green-800',
      pending: 'bg-yellow-100 text-yellow-800',
      completed: 'bg-gray-100 text-gray-800',
      cancelled: 'bg-red-100 text-red-800',
    };
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const getDayAppointments = (date: Date) => {
    const dateStr = date.toISOString().split('T')[0];
    return appointments.filter((apt) => apt.date === dateStr).sort((a, b) => a.time.localeCompare(b.time));
  };

  const getWeekDates = () => {
    const week: Date[] = [];
    const startOfWeek = new Date(selectedDate);
    const day = startOfWeek.getDay();
    const diff = startOfWeek.getDate() - day;
    startOfWeek.setDate(diff);

    for (let i = 0; i < 7; i++) {
      const date = new Date(startOfWeek);
      date.setDate(startOfWeek.getDate() + i);
      week.push(date);
    }
    return week;
  };

  const changeWeek = (direction: 'prev' | 'next') => {
    const newDate = new Date(selectedDate);
    newDate.setDate(selectedDate.getDate() + (direction === 'next' ? 7 : -7));
    setSelectedDate(newDate);
  };

  const timeSlots = Array.from({ length: 11 }, (_, i) => {
    const hour = i + 8;
    return `${hour.toString().padStart(2, '0')}:00`;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar role="doctor" />
        <main className="flex-1 ml-64 mt-16">
          <div className="p-8">
            {/* Header */}
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Appointments</h1>
                <p className="text-gray-500 mt-1">Manage your patient appointments</p>
              </div>
              <Button onClick={() => setIsAddDialogOpen(true)} className="bg-blue-600 hover:bg-blue-700">
                <Plus className="h-4 w-4 mr-2" />
                Schedule Appointment
              </Button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>Today's Appointments</CardDescription>
                  <CardTitle className="text-3xl">{getDayAppointments(new Date()).length}</CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>This Week</CardDescription>
                  <CardTitle className="text-3xl">{appointments.length}</CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>Pending</CardDescription>
                  <CardTitle className="text-3xl">
                    {appointments.filter((a) => a.status === 'pending').length}
                  </CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>Virtual Appointments</CardDescription>
                  <CardTitle className="text-3xl">
                    {appointments.filter((a) => a.type === 'virtual').length}
                  </CardTitle>
                </CardHeader>
              </Card>
            </div>

            {/* View Controls */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <Button variant="outline" size="icon" onClick={() => changeWeek('prev')}>
                      <ChevronLeft className="h-4 w-4" />
                    </Button>
                    <h2 className="text-xl font-semibold">
                      {selectedDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                    </h2>
                    <Button variant="outline" size="icon" onClick={() => changeWeek('next')}>
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="flex space-x-2">
                    <Button
                      variant={viewMode === 'day' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setViewMode('day')}
                    >
                      Day
                    </Button>
                    <Button
                      variant={viewMode === 'week' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setViewMode('week')}
                    >
                      Week
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {viewMode === 'week' ? (
                  <div className="space-y-4">
                    {/* Week Days */}
                    <div className="grid grid-cols-7 gap-2">
                      {getWeekDates().map((date, idx) => {
                        const dayAppointments = getDayAppointments(date);
                        const isToday = date.toDateString() === new Date().toDateString();

                        return (
                          <div
                            key={idx}
                            className={`p-4 rounded-lg border-2 ${
                              isToday ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                            }`}
                          >
                            <div className="text-center mb-3">
                              <div className="text-xs text-gray-500 uppercase">
                                {date.toLocaleDateString('en-US', { weekday: 'short' })}
                              </div>
                              <div
                                className={`text-2xl font-bold ${
                                  isToday ? 'text-blue-600' : 'text-gray-900'
                                }`}
                              >
                                {date.getDate()}
                              </div>
                            </div>
                            <div className="space-y-2">
                              {dayAppointments.map((apt) => (
                                <div
                                  key={apt.id}
                                  className={`p-2 rounded text-xs cursor-pointer hover:shadow-md transition-shadow ${getTypeColor(
                                    apt.type
                                  )}`}
                                  onClick={() => {
                                    setEditingAppointment(apt);
                                    setIsEditDialogOpen(true);
                                  }}
                                >
                                  <div className="font-semibold">{apt.time}</div>
                                  <div className="truncate">{apt.patientName}</div>
                                </div>
                              ))}
                              {dayAppointments.length === 0 && (
                                <div className="text-xs text-gray-400 text-center py-2">No appointments</div>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>

                    {/* Today's Schedule */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Today's Schedule</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          {getDayAppointments(new Date()).length === 0 ? (
                            <p className="text-gray-500 text-center py-4">No appointments today</p>
                          ) : (
                            getDayAppointments(new Date()).map((apt) => (
                              <div
                                key={apt.id}
                                className="flex items-center justify-between p-4 border rounded-lg hover:shadow-md transition-shadow"
                              >
                                <div className="flex items-center space-x-4">
                                  <Avatar>
                                    <AvatarFallback>
                                      {apt.patientName
                                        .split(' ')
                                        .map((n) => n[0])
                                        .join('')}
                                    </AvatarFallback>
                                  </Avatar>
                                  <div>
                                    <h3 className="font-semibold">{apt.patientName}</h3>
                                    <div className="flex items-center space-x-3 text-sm text-gray-500">
                                      <span className="flex items-center">
                                        <Clock className="h-3 w-3 mr-1" />
                                        {apt.time} ({apt.duration} min)
                                      </span>
                                      {apt.type === 'virtual' ? (
                                        <span className="flex items-center">
                                          <Video className="h-3 w-3 mr-1" />
                                          Virtual
                                        </span>
                                      ) : (
                                        <span className="flex items-center">
                                          <MapPin className="h-3 w-3 mr-1" />
                                          {apt.location}
                                        </span>
                                      )}
                                    </div>
                                  </div>
                                </div>
                                <div className="flex items-center space-x-2">
                                  <Badge className={getTypeColor(apt.type)}>{apt.type}</Badge>
                                  <Badge className={getStatusColor(apt.status)}>{apt.status}</Badge>
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => {
                                      setEditingAppointment(apt);
                                      setIsEditDialogOpen(true);
                                    }}
                                  >
                                    <Edit className="h-3 w-3" />
                                  </Button>
                                </div>
                              </div>
                            ))
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                ) : (
                  // Day View with time slots
                  <div className="space-y-1">
                    {timeSlots.map((time) => {
                      const apt = getDayAppointments(selectedDate).find((a) => a.time === time);

                      return (
                        <div key={time} className="flex items-start border-b py-3">
                          <div className="w-20 text-sm text-gray-500 font-medium">{time}</div>
                          <div className="flex-1">
                            {apt ? (
                              <div
                                className={`p-3 rounded-lg ${getTypeColor(apt.type)} cursor-pointer`}
                                onClick={() => {
                                  setEditingAppointment(apt);
                                  setIsEditDialogOpen(true);
                                }}
                              >
                                <div className="flex items-center justify-between">
                                  <div>
                                    <h3 className="font-semibold">{apt.patientName}</h3>
                                    <p className="text-sm opacity-75">{apt.notes}</p>
                                  </div>
                                  <Badge className={getStatusColor(apt.status)}>{apt.status}</Badge>
                                </div>
                              </div>
                            ) : (
                              <div className="text-sm text-gray-400">Available</div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Add Appointment Dialog */}
            <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
              <DialogContent className="max-w-md">
                <DialogHeader>
                  <DialogTitle>Schedule New Appointment</DialogTitle>
                  <DialogDescription>Book a new appointment for a patient</DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="patient-name">Patient Name</Label>
                      <Input
                        id="patient-name"
                        value={newAppointment.patientName}
                        onChange={(e) => setNewAppointment({ ...newAppointment, patientName: e.target.value })}
                        placeholder="John Doe"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="patient-id">Patient ID</Label>
                      <Input
                        id="patient-id"
                        value={newAppointment.patientId}
                        onChange={(e) => setNewAppointment({ ...newAppointment, patientId: e.target.value })}
                        placeholder="P1234"
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="date">Date</Label>
                      <Input
                        id="date"
                        type="date"
                        value={newAppointment.date}
                        onChange={(e) => setNewAppointment({ ...newAppointment, date: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="time">Time</Label>
                      <Input
                        id="time"
                        type="time"
                        value={newAppointment.time}
                        onChange={(e) => setNewAppointment({ ...newAppointment, time: e.target.value })}
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="type">Type</Label>
                      <Select
                        value={newAppointment.type}
                        onValueChange={(value: any) => setNewAppointment({ ...newAppointment, type: value })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="checkup">Checkup</SelectItem>
                          <SelectItem value="consultation">Consultation</SelectItem>
                          <SelectItem value="follow-up">Follow-up</SelectItem>
                          <SelectItem value="virtual">Virtual</SelectItem>
                          <SelectItem value="emergency">Emergency</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="duration">Duration (min)</Label>
                      <Select
                        value={newAppointment.duration.toString()}
                        onValueChange={(value) => setNewAppointment({ ...newAppointment, duration: Number(value) })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="15">15 minutes</SelectItem>
                          <SelectItem value="30">30 minutes</SelectItem>
                          <SelectItem value="45">45 minutes</SelectItem>
                          <SelectItem value="60">60 minutes</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="location">Location</Label>
                    <Select
                      value={newAppointment.location}
                      onValueChange={(value) => setNewAppointment({ ...newAppointment, location: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Clinic Room 1">Clinic Room 1</SelectItem>
                        <SelectItem value="Clinic Room 2">Clinic Room 2</SelectItem>
                        <SelectItem value="Clinic Room 3">Clinic Room 3</SelectItem>
                        <SelectItem value="Virtual">Virtual</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="notes">Notes</Label>
                    <Textarea
                      id="notes"
                      value={newAppointment.notes}
                      onChange={(e) => setNewAppointment({ ...newAppointment, notes: e.target.value })}
                      placeholder="Additional notes or instructions"
                      rows={3}
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleAddAppointment} className="bg-blue-600 hover:bg-blue-700">
                    Schedule Appointment
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>

            {/* Edit Appointment Dialog */}
            <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
              <DialogContent className="max-w-md">
                <DialogHeader>
                  <DialogTitle>Edit Appointment</DialogTitle>
                  <DialogDescription>Update appointment details</DialogDescription>
                </DialogHeader>
                {editingAppointment && (
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label>Patient</Label>
                      <Input value={editingAppointment.patientName} disabled />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="edit-date">Date</Label>
                        <Input
                          id="edit-date"
                          type="date"
                          value={editingAppointment.date}
                          onChange={(e) =>
                            setEditingAppointment({ ...editingAppointment, date: e.target.value })
                          }
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="edit-time">Time</Label>
                        <Input
                          id="edit-time"
                          type="time"
                          value={editingAppointment.time}
                          onChange={(e) =>
                            setEditingAppointment({ ...editingAppointment, time: e.target.value })
                          }
                        />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="edit-status">Status</Label>
                      <Select
                        value={editingAppointment.status}
                        onValueChange={(value: any) =>
                          setEditingAppointment({ ...editingAppointment, status: value })
                        }
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="confirmed">Confirmed</SelectItem>
                          <SelectItem value="pending">Pending</SelectItem>
                          <SelectItem value="completed">Completed</SelectItem>
                          <SelectItem value="cancelled">Cancelled</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="edit-notes">Notes</Label>
                      <Textarea
                        id="edit-notes"
                        value={editingAppointment.notes || ''}
                        onChange={(e) =>
                          setEditingAppointment({ ...editingAppointment, notes: e.target.value })
                        }
                        rows={3}
                      />
                    </div>
                  </div>
                )}
                <DialogFooter>
                  <Button
                    variant="outline"
                    className="text-red-600 hover:bg-red-50"
                    onClick={() => {
                      if (editingAppointment) {
                        handleDeleteAppointment(editingAppointment.id);
                        setIsEditDialogOpen(false);
                      }
                    }}
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Cancel Appointment
                  </Button>
                  <Button onClick={handleEditAppointment} className="bg-blue-600 hover:bg-blue-700">
                    Save Changes
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </main>
      </div>
    </div>
  );
}
