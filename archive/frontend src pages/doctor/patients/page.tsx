'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@/hooks/useAuth';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
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
} from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';
import {
  User,
  Search,
  Phone,
  Mail,
  Calendar,
  FileText,
  Stethoscope,
  Activity,
  Clock,
  MapPin,
  AlertCircle,
  TrendingUp,
  Pill,
  FlaskConical,
} from 'lucide-react';
import Link from 'next/link';
import axios from 'axios';

interface Patient {
  patient_id: string;
  name: string;
  email: string;
  phone: string;
  date_of_birth: string;
  gender: string;
  blood_type?: string;
  address?: string;
  emergency_contact?: string;
  last_visit?: string;
  next_appointment?: string;
  total_visits?: number;
  active_prescriptions?: number;
  pending_labs?: number;
}

interface MedicalHistory {
  consultation_id: string;
  date: string;
  diagnosis: string;
  treatment: string;
  doctor_notes: string;
}

export default function DoctorPatients() {
  const { user } = useAuth();
  const doctorId = 'doctor001'; // TODO: Get from authenticated user

  const [searchQuery, setSearchQuery] = useState('');
  const [genderFilter, setGenderFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('name');
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);

  // Fetch patients assigned to doctor
  const { data: patientsData, isLoading } = useQuery({
    queryKey: ['doctor-patients', doctorId],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `http://localhost:8000/api/doctors/${doctorId}/patients`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data?.data?.patients || [];
    },
    enabled: !!doctorId,
  });

  // Fetch patient medical history when selected
  const { data: historyData, isLoading: historyLoading } = useQuery({
    queryKey: ['patient-history', selectedPatient?.patient_id],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `http://localhost:8000/api/patients/${selectedPatient?.patient_id}/consultations`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data?.data?.consultations || [];
    },
    enabled: !!selectedPatient?.patient_id,
  });

  const patients: Patient[] = patientsData || [];

  // Filter and sort patients
  const filteredPatients = patients
    .filter((patient) => {
      if (genderFilter !== 'all' && patient.gender !== genderFilter) return false;
      if (
        searchQuery &&
        !patient.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
        !patient.patient_id.toLowerCase().includes(searchQuery.toLowerCase())
      ) {
        return false;
      }
      return true;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'recent':
          return (b.last_visit || '').localeCompare(a.last_visit || '');
        case 'upcoming':
          return (a.next_appointment || '').localeCompare(b.next_appointment || '');
        default:
          return 0;
      }
    });

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

  const handlePatientClick = (patient: Patient) => {
    setSelectedPatient(patient);
    setDetailsDialogOpen(true);
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
              <h1 className="text-3xl font-bold text-gray-900 mb-2">My Patients</h1>
              <p className="text-gray-600">Manage and view your assigned patients</p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Total Patients
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-gray-900">{patients.length}</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Active Cases
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-gray-900">
                    {patients.filter((p) => p.active_prescriptions && p.active_prescriptions > 0).length}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Pending Labs
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-gray-900">
                    {patients.reduce((sum, p) => sum + (p.pending_labs || 0), 0)}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    This Week's Visits
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-gray-900">
                    {patients.reduce((sum, p) => sum + (p.total_visits || 0), 0)}
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Filters */}
            <Card className="mb-6">
              <CardContent className="pt-6">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  {/* Search */}
                  <div className="relative md:col-span-2">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Search by name or patient ID..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>

                  {/* Gender Filter */}
                  <Select value={genderFilter} onValueChange={setGenderFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="Gender" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Genders</SelectItem>
                      <SelectItem value="male">Male</SelectItem>
                      <SelectItem value="female">Female</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>

                  {/* Sort */}
                  <Select value={sortBy} onValueChange={setSortBy}>
                    <SelectTrigger>
                      <SelectValue placeholder="Sort by" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="name">Name (A-Z)</SelectItem>
                      <SelectItem value="recent">Recent Visit</SelectItem>
                      <SelectItem value="upcoming">Next Appointment</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Patients Grid */}
            {isLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[1, 2, 3, 4, 5, 6].map((i) => (
                  <Card key={i}>
                    <CardContent className="pt-6">
                      <Skeleton className="h-32 w-full" />
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : filteredPatients.length === 0 ? (
              <Card>
                <CardContent className="pt-12 pb-12 text-center">
                  <User className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 text-lg mb-2">No patients found</p>
                  <p className="text-gray-500 text-sm">
                    Try adjusting your search or filters
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredPatients.map((patient) => (
                  <Card
                    key={patient.patient_id}
                    className="hover:shadow-lg transition-shadow cursor-pointer"
                    onClick={() => handlePatientClick(patient)}
                  >
                    <CardContent className="pt-6">
                      {/* Patient Header */}
                      <div className="flex items-start space-x-4 mb-4">
                        <Avatar className="h-12 w-12">
                          <AvatarFallback className="bg-blue-100 text-blue-600 font-semibold">
                            {patient.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                          </AvatarFallback>
                        </Avatar>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold text-gray-900 truncate">
                            {patient.name}
                          </h3>
                          <p className="text-sm text-gray-600">{patient.patient_id}</p>
                          <div className="flex items-center space-x-2 mt-1">
                            <Badge variant="outline" className="text-xs">
                              {patient.gender}
                            </Badge>
                            <span className="text-xs text-gray-600">
                              {calculateAge(patient.date_of_birth)} years
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Contact Info */}
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <Phone className="h-4 w-4" />
                          <span className="truncate">{patient.phone}</span>
                        </div>
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <Mail className="h-4 w-4" />
                          <span className="truncate">{patient.email}</span>
                        </div>
                      </div>

                      {/* Quick Stats */}
                      <div className="grid grid-cols-3 gap-2 pt-4 border-t">
                        <div className="text-center">
                          <div className="flex items-center justify-center mb-1">
                            <Pill className="h-4 w-4 text-blue-600" />
                          </div>
                          <p className="text-xs text-gray-600">Prescriptions</p>
                          <p className="text-sm font-semibold text-gray-900">
                            {patient.active_prescriptions || 0}
                          </p>
                        </div>
                        <div className="text-center">
                          <div className="flex items-center justify-center mb-1">
                            <FlaskConical className="h-4 w-4 text-purple-600" />
                          </div>
                          <p className="text-xs text-gray-600">Pending Labs</p>
                          <p className="text-sm font-semibold text-gray-900">
                            {patient.pending_labs || 0}
                          </p>
                        </div>
                        <div className="text-center">
                          <div className="flex items-center justify-center mb-1">
                            <Activity className="h-4 w-4 text-green-600" />
                          </div>
                          <p className="text-xs text-gray-600">Visits</p>
                          <p className="text-sm font-semibold text-gray-900">
                            {patient.total_visits || 0}
                          </p>
                        </div>
                      </div>

                      {/* Last/Next Visit */}
                      {(patient.last_visit || patient.next_appointment) && (
                        <div className="mt-4 pt-4 border-t space-y-2">
                          {patient.last_visit && (
                            <div className="flex items-center justify-between text-sm">
                              <span className="text-gray-600">Last visit:</span>
                              <span className="font-medium text-gray-900">
                                {new Date(patient.last_visit).toLocaleDateString()}
                              </span>
                            </div>
                          )}
                          {patient.next_appointment && (
                            <div className="flex items-center justify-between text-sm">
                              <span className="text-gray-600">Next appointment:</span>
                              <span className="font-medium text-blue-600">
                                {new Date(patient.next_appointment).toLocaleDateString()}
                              </span>
                            </div>
                          )}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </main>
      </div>

      {/* Patient Details Dialog */}
      <Dialog open={detailsDialogOpen} onOpenChange={setDetailsDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Patient Details</DialogTitle>
            <DialogDescription>
              Complete medical information and history
            </DialogDescription>
          </DialogHeader>

          {selectedPatient && (
            <div className="space-y-6">
              {/* Patient Header */}
              <div className="flex items-start space-x-4 pb-4 border-b">
                <Avatar className="h-16 w-16">
                  <AvatarFallback className="bg-blue-100 text-blue-600 font-semibold text-xl">
                    {selectedPatient.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1">
                  <h2 className="text-2xl font-bold text-gray-900">{selectedPatient.name}</h2>
                  <p className="text-gray-600">{selectedPatient.patient_id}</p>
                  <div className="flex items-center space-x-3 mt-2">
                    <Badge>{selectedPatient.gender}</Badge>
                    <span className="text-sm text-gray-600">
                      {calculateAge(selectedPatient.date_of_birth)} years old
                    </span>
                    {selectedPatient.blood_type && (
                      <Badge variant="outline">Blood Type: {selectedPatient.blood_type}</Badge>
                    )}
                  </div>
                </div>
              </div>

              {/* Tabs */}
              <Tabs defaultValue="info" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="info">Personal Info</TabsTrigger>
                  <TabsTrigger value="history">Medical History</TabsTrigger>
                  <TabsTrigger value="actions">Quick Actions</TabsTrigger>
                </TabsList>

                {/* Personal Info Tab */}
                <TabsContent value="info" className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Contact Information</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="text-sm text-gray-600">Phone</label>
                          <p className="font-medium text-gray-900">{selectedPatient.phone}</p>
                        </div>
                        <div>
                          <label className="text-sm text-gray-600">Email</label>
                          <p className="font-medium text-gray-900">{selectedPatient.email}</p>
                        </div>
                        <div className="col-span-2">
                          <label className="text-sm text-gray-600">Address</label>
                          <p className="font-medium text-gray-900">
                            {selectedPatient.address || 'Not provided'}
                          </p>
                        </div>
                        <div className="col-span-2">
                          <label className="text-sm text-gray-600">Emergency Contact</label>
                          <p className="font-medium text-gray-900">
                            {selectedPatient.emergency_contact || 'Not provided'}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Medical Summary</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-3 gap-4">
                        <div className="text-center p-4 bg-blue-50 rounded-lg">
                          <Pill className="h-6 w-6 text-blue-600 mx-auto mb-2" />
                          <p className="text-2xl font-bold text-blue-600">
                            {selectedPatient.active_prescriptions || 0}
                          </p>
                          <p className="text-sm text-gray-600">Active Prescriptions</p>
                        </div>
                        <div className="text-center p-4 bg-purple-50 rounded-lg">
                          <FlaskConical className="h-6 w-6 text-purple-600 mx-auto mb-2" />
                          <p className="text-2xl font-bold text-purple-600">
                            {selectedPatient.pending_labs || 0}
                          </p>
                          <p className="text-sm text-gray-600">Pending Lab Tests</p>
                        </div>
                        <div className="text-center p-4 bg-green-50 rounded-lg">
                          <Activity className="h-6 w-6 text-green-600 mx-auto mb-2" />
                          <p className="text-2xl font-bold text-green-600">
                            {selectedPatient.total_visits || 0}
                          </p>
                          <p className="text-sm text-gray-600">Total Visits</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>

                {/* Medical History Tab */}
                <TabsContent value="history">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Consultation History</CardTitle>
                    </CardHeader>
                    <CardContent>
                      {historyLoading ? (
                        <div className="space-y-3">
                          {[1, 2, 3].map((i) => (
                            <Skeleton key={i} className="h-24 w-full" />
                          ))}
                        </div>
                      ) : historyData && historyData.length > 0 ? (
                        <div className="space-y-4">
                          {historyData.map((consultation: MedicalHistory) => (
                            <div
                              key={consultation.consultation_id}
                              className="p-4 bg-gray-50 rounded-lg"
                            >
                              <div className="flex items-center justify-between mb-2">
                                <span className="font-medium text-gray-900">
                                  {new Date(consultation.date).toLocaleDateString()}
                                </span>
                                <Badge variant="outline">{consultation.consultation_id}</Badge>
                              </div>
                              <div className="space-y-2 text-sm">
                                <div>
                                  <span className="text-gray-600">Diagnosis:</span>
                                  <p className="text-gray-900">{consultation.diagnosis}</p>
                                </div>
                                <div>
                                  <span className="text-gray-600">Treatment:</span>
                                  <p className="text-gray-900">{consultation.treatment}</p>
                                </div>
                                {consultation.doctor_notes && (
                                  <div>
                                    <span className="text-gray-600">Notes:</span>
                                    <p className="text-gray-900">{consultation.doctor_notes}</p>
                                  </div>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-center text-gray-600 py-8">
                          No consultation history available
                        </p>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>

                {/* Quick Actions Tab */}
                <TabsContent value="actions">
                  <div className="grid grid-cols-2 gap-4">
                    <Link href={`/doctor/consultations?patient=${selectedPatient.patient_id}`}>
                      <Button variant="outline" className="w-full h-24 flex-col">
                        <Stethoscope className="h-8 w-8 mb-2" />
                        New Consultation
                      </Button>
                    </Link>
                    <Link href={`/doctor/prescriptions?patient=${selectedPatient.patient_id}`}>
                      <Button variant="outline" className="w-full h-24 flex-col">
                        <Pill className="h-8 w-8 mb-2" />
                        Write Prescription
                      </Button>
                    </Link>
                    <Link href={`/doctor/lab-results?patient=${selectedPatient.patient_id}`}>
                      <Button variant="outline" className="w-full h-24 flex-col">
                        <FlaskConical className="h-8 w-8 mb-2" />
                        Order Lab Test
                      </Button>
                    </Link>
                    <Link href={`/doctor/schedule?patient=${selectedPatient.patient_id}`}>
                      <Button variant="outline" className="w-full h-24 flex-col">
                        <Calendar className="h-8 w-8 mb-2" />
                        Schedule Appointment
                      </Button>
                    </Link>
                  </div>
                </TabsContent>
              </Tabs>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
