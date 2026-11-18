'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@/hooks/useAuth';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';
import {
  Users,
  Search,
  User,
  Phone,
  Mail,
  Calendar,
  MapPin,
  Heart,
  FileText,
  Clock,
  DollarSign,
  Activity,
  AlertCircle,
  CheckCircle,
} from 'lucide-react';
import axios from 'axios';

interface Patient {
  patient_id: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string;
  phone: string;
  email: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  insurance_provider?: string;
  insurance_id?: string;
  blood_type?: string;
  allergies?: string[];
  chronic_conditions?: string[];
  primary_doctor_id?: string;
  primary_doctor_name?: string;
  status?: string;
  created_at?: string;
  last_visit?: string;
}

interface Appointment {
  appointment_id: string;
  appointment_date: string;
  appointment_time: string;
  doctor_name: string;
  type: string;
  status: string;
  reason?: string;
}

interface Invoice {
  invoice_id: string;
  invoice_date: string;
  amount: number;
  amount_paid: number;
  status: string;
  description?: string;
}

export default function StaffPatients() {
  const { user } = useAuth();

  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);

  // Fetch all patients
  const { data: patientsData, isLoading } = useQuery({
    queryKey: ['staff-patients'],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:8000/api/patients', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      return response.data?.data?.patients || [];
    },
  });

  // Fetch patient appointments
  const { data: appointmentsData } = useQuery({
    queryKey: ['patient-appointments', selectedPatient?.patient_id],
    queryFn: async () => {
      if (!selectedPatient) return [];
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `http://localhost:8000/api/patients/${selectedPatient.patient_id}/appointments`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data?.data?.appointments || [];
    },
    enabled: !!selectedPatient,
  });

  // Fetch patient billing
  const { data: invoicesData } = useQuery({
    queryKey: ['patient-invoices', selectedPatient?.patient_id],
    queryFn: async () => {
      if (!selectedPatient) return [];
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `http://localhost:8000/api/patients/${selectedPatient.patient_id}/invoices`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data?.data?.invoices || [];
    },
    enabled: !!selectedPatient,
  });

  const patients: Patient[] = patientsData || [];
  const appointments: Appointment[] = appointmentsData || [];
  const invoices: Invoice[] = invoicesData || [];

  // Filter patients
  const filteredPatients = patients.filter((patient) => {
    const fullName = `${patient.first_name} ${patient.last_name}`.toLowerCase();
    const matchesSearch =
      !searchQuery ||
      fullName.includes(searchQuery.toLowerCase()) ||
      patient.patient_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      patient.email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      patient.phone?.includes(searchQuery);

    const matchesStatus = statusFilter === 'all' || patient.status === statusFilter;

    return matchesSearch && matchesStatus;
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

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const formatTime = (timeString: string) => {
    return new Date(`2000-01-01T${timeString}`).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  const viewPatientDetails = (patient: Patient) => {
    setSelectedPatient(patient);
    setDetailsDialogOpen(true);
  };

  // Calculate stats
  const totalPatients = patients.length;
  const activePatients = patients.filter((p) => p.status === 'active').length;
  const newThisMonth = patients.filter((p) => {
    if (!p.created_at) return false;
    const created = new Date(p.created_at);
    const now = new Date();
    return (
      created.getMonth() === now.getMonth() && created.getFullYear() === now.getFullYear()
    );
  }).length;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar role="staff" />
        <main className="flex-1 ml-64 mt-16">
          <div className="p-8">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Patient Records</h1>
              <p className="text-gray-600">Search and manage patient information</p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Total Patients
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-gray-900">{totalPatients}</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Active Patients
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-green-600">{activePatients}</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    New This Month
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-blue-600">{newThisMonth}</p>
                </CardContent>
              </Card>
            </div>

            {/* Search and Filters */}
            <Card className="mb-6">
              <CardContent className="pt-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="md:col-span-2">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                      <Input
                        placeholder="Search by name, ID, email, or phone..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-12"
                      />
                    </div>
                  </div>
                  <div>
                    <Select value={statusFilter} onValueChange={setStatusFilter}>
                      <SelectTrigger>
                        <SelectValue placeholder="Filter by status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Patients</SelectItem>
                        <SelectItem value="active">Active</SelectItem>
                        <SelectItem value="inactive">Inactive</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="mt-4 flex items-center justify-between">
                  <p className="text-sm text-gray-600">
                    Showing {filteredPatients.length} of {totalPatients} patients
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Patients List */}
            {isLoading ? (
              <div className="space-y-4">
                {[1, 2, 3, 4, 5].map((i) => (
                  <Card key={i}>
                    <CardContent className="pt-6">
                      <Skeleton className="h-20 w-full" />
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : filteredPatients.length === 0 ? (
              <Card>
                <CardContent className="pt-12 pb-12 text-center">
                  <Users className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 text-lg mb-2">No patients found</p>
                  <p className="text-gray-500 text-sm">
                    Try adjusting your search or filters
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-3">
                {filteredPatients.map((patient) => (
                  <Card key={patient.patient_id} className="hover:shadow-lg transition-shadow">
                    <CardContent className="pt-6">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-4 flex-1">
                          <div className="h-16 w-16 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                            <span className="text-blue-600 font-bold text-xl">
                              {patient.first_name.charAt(0)}
                              {patient.last_name.charAt(0)}
                            </span>
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center space-x-3 mb-2">
                              <h3 className="text-lg font-bold text-gray-900">
                                {patient.first_name} {patient.last_name}
                              </h3>
                              <Badge
                                variant={patient.status === 'active' ? 'default' : 'secondary'}
                              >
                                {patient.status || 'Active'}
                              </Badge>
                            </div>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                              <div className="flex items-center space-x-2">
                                <User className="h-4 w-4 text-gray-400" />
                                <span className="text-gray-600">
                                  {calculateAge(patient.date_of_birth)} years, {patient.gender}
                                </span>
                              </div>
                              <div className="flex items-center space-x-2">
                                <Phone className="h-4 w-4 text-gray-400" />
                                <span className="text-gray-600">{patient.phone}</span>
                              </div>
                              <div className="flex items-center space-x-2">
                                <Mail className="h-4 w-4 text-gray-400" />
                                <span className="text-gray-600 truncate">{patient.email}</span>
                              </div>
                              {patient.primary_doctor_name && (
                                <div className="flex items-center space-x-2">
                                  <Activity className="h-4 w-4 text-gray-400" />
                                  <span className="text-gray-600">
                                    Dr. {patient.primary_doctor_name}
                                  </span>
                                </div>
                              )}
                            </div>
                            {patient.last_visit && (
                              <p className="text-xs text-gray-500 mt-2">
                                Last visit: {formatDate(patient.last_visit)}
                              </p>
                            )}
                          </div>
                        </div>
                        <Button onClick={() => viewPatientDetails(patient)}>
                          View Details
                        </Button>
                      </div>
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
              Complete patient information and records
            </DialogDescription>
          </DialogHeader>

          {selectedPatient && (
            <Tabs defaultValue="demographics" className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="demographics">Demographics</TabsTrigger>
                <TabsTrigger value="medical">Medical Info</TabsTrigger>
                <TabsTrigger value="appointments">Appointments</TabsTrigger>
                <TabsTrigger value="billing">Billing</TabsTrigger>
              </TabsList>

              {/* Demographics Tab */}
              <TabsContent value="demographics" className="space-y-6">
                <div className="flex items-center space-x-4 p-4 bg-blue-50 rounded-lg">
                  <div className="h-20 w-20 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-blue-600 font-bold text-3xl">
                      {selectedPatient.first_name.charAt(0)}
                      {selectedPatient.last_name.charAt(0)}
                    </span>
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">
                      {selectedPatient.first_name} {selectedPatient.last_name}
                    </h2>
                    <p className="text-gray-600">ID: {selectedPatient.patient_id}</p>
                    <Badge
                      variant={selectedPatient.status === 'active' ? 'default' : 'secondary'}
                      className="mt-1"
                    >
                      {selectedPatient.status || 'Active'}
                    </Badge>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <Label className="text-gray-600">Date of Birth</Label>
                    <p className="font-medium">
                      {formatDate(selectedPatient.date_of_birth)} (
                      {calculateAge(selectedPatient.date_of_birth)} years)
                    </p>
                  </div>
                  <div>
                    <Label className="text-gray-600">Gender</Label>
                    <p className="font-medium capitalize">{selectedPatient.gender}</p>
                  </div>
                  <div>
                    <Label className="text-gray-600">Phone</Label>
                    <p className="font-medium">{selectedPatient.phone}</p>
                  </div>
                  <div>
                    <Label className="text-gray-600">Email</Label>
                    <p className="font-medium">{selectedPatient.email}</p>
                  </div>
                </div>

                {selectedPatient.address && (
                  <div>
                    <Label className="text-gray-600">Address</Label>
                    <div className="flex items-start space-x-2 mt-1">
                      <MapPin className="h-5 w-5 text-gray-400 mt-0.5" />
                      <p className="font-medium">
                        {selectedPatient.address}
                        {selectedPatient.city && `, ${selectedPatient.city}`}
                        {selectedPatient.state && `, ${selectedPatient.state}`}
                        {selectedPatient.zip_code && ` ${selectedPatient.zip_code}`}
                      </p>
                    </div>
                  </div>
                )}

                <div className="border-t pt-6">
                  <h3 className="font-semibold mb-4">Emergency Contact</h3>
                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <Label className="text-gray-600">Name</Label>
                      <p className="font-medium">
                        {selectedPatient.emergency_contact_name || 'Not provided'}
                      </p>
                    </div>
                    <div>
                      <Label className="text-gray-600">Phone</Label>
                      <p className="font-medium">
                        {selectedPatient.emergency_contact_phone || 'Not provided'}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="border-t pt-6">
                  <h3 className="font-semibold mb-4">Insurance</h3>
                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <Label className="text-gray-600">Provider</Label>
                      <p className="font-medium">
                        {selectedPatient.insurance_provider || 'Not provided'}
                      </p>
                    </div>
                    <div>
                      <Label className="text-gray-600">Insurance ID</Label>
                      <p className="font-medium">
                        {selectedPatient.insurance_id || 'Not provided'}
                      </p>
                    </div>
                  </div>
                </div>
              </TabsContent>

              {/* Medical Info Tab */}
              <TabsContent value="medical" className="space-y-6">
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <Label className="text-gray-600">Primary Doctor</Label>
                    <p className="font-medium">
                      {selectedPatient.primary_doctor_name
                        ? `Dr. ${selectedPatient.primary_doctor_name}`
                        : 'Not assigned'}
                    </p>
                  </div>
                  <div>
                    <Label className="text-gray-600">Blood Type</Label>
                    <div className="flex items-center space-x-2">
                      <Heart className="h-5 w-5 text-red-500" />
                      <p className="font-medium">{selectedPatient.blood_type || 'Unknown'}</p>
                    </div>
                  </div>
                </div>

                <div>
                  <Label className="text-gray-600 flex items-center space-x-2">
                    <AlertCircle className="h-4 w-4" />
                    <span>Allergies</span>
                  </Label>
                  <div className="mt-2">
                    {selectedPatient.allergies && selectedPatient.allergies.length > 0 ? (
                      <div className="flex flex-wrap gap-2">
                        {selectedPatient.allergies.map((allergy, idx) => (
                          <Badge key={idx} variant="destructive">
                            {allergy}
                          </Badge>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500">No known allergies</p>
                    )}
                  </div>
                </div>

                <div>
                  <Label className="text-gray-600">Chronic Conditions</Label>
                  <div className="mt-2">
                    {selectedPatient.chronic_conditions &&
                    selectedPatient.chronic_conditions.length > 0 ? (
                      <div className="flex flex-wrap gap-2">
                        {selectedPatient.chronic_conditions.map((condition, idx) => (
                          <Badge key={idx} variant="secondary">
                            {condition}
                          </Badge>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500">No chronic conditions recorded</p>
                    )}
                  </div>
                </div>
              </TabsContent>

              {/* Appointments Tab */}
              <TabsContent value="appointments" className="space-y-4">
                {appointments.length === 0 ? (
                  <div className="text-center py-12">
                    <Calendar className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">No appointments found</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {appointments.map((apt) => (
                      <Card key={apt.appointment_id}>
                        <CardContent className="pt-4 pb-4">
                          <div className="flex items-center justify-between">
                            <div>
                              <div className="flex items-center space-x-3 mb-1">
                                <Calendar className="h-4 w-4 text-gray-400" />
                                <span className="font-medium">{formatDate(apt.appointment_date)}</span>
                                <Clock className="h-4 w-4 text-gray-400 ml-2" />
                                <span>{formatTime(apt.appointment_time)}</span>
                              </div>
                              <div className="text-sm text-gray-600 ml-7">
                                Dr. {apt.doctor_name} • {apt.type}
                              </div>
                              {apt.reason && (
                                <p className="text-sm text-gray-600 ml-7 mt-1">
                                  Reason: {apt.reason}
                                </p>
                              )}
                            </div>
                            <Badge>{apt.status}</Badge>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </TabsContent>

              {/* Billing Tab */}
              <TabsContent value="billing" className="space-y-4">
                {invoices.length === 0 ? (
                  <div className="text-center py-12">
                    <DollarSign className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">No billing records found</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {invoices.map((invoice) => {
                      const balance = invoice.amount - invoice.amount_paid;
                      return (
                        <Card key={invoice.invoice_id}>
                          <CardContent className="pt-4 pb-4">
                            <div className="flex items-center justify-between">
                              <div>
                                <div className="flex items-center space-x-3 mb-1">
                                  <FileText className="h-4 w-4 text-gray-400" />
                                  <span className="font-medium">
                                    {formatDate(invoice.invoice_date)}
                                  </span>
                                  <Badge
                                    variant={
                                      invoice.status === 'paid'
                                        ? 'default'
                                        : invoice.status === 'pending'
                                        ? 'secondary'
                                        : 'destructive'
                                    }
                                  >
                                    {invoice.status}
                                  </Badge>
                                </div>
                                {invoice.description && (
                                  <p className="text-sm text-gray-600 ml-7">
                                    {invoice.description}
                                  </p>
                                )}
                              </div>
                              <div className="text-right">
                                <p className="text-lg font-bold text-gray-900">
                                  ${invoice.amount.toFixed(2)}
                                </p>
                                {balance > 0 && (
                                  <p className="text-sm text-orange-600">
                                    Balance: ${balance.toFixed(2)}
                                  </p>
                                )}
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      );
                    })}
                  </div>
                )}
              </TabsContent>
            </Tabs>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
