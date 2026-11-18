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
  Stethoscope,
  FileText,
  Calendar,
  User,
  Search,
  Plus,
  Edit,
  Eye,
  Save,
  X,
  Clock,
  Activity,
  Pill,
  FlaskConical,
} from 'lucide-react';
import axios from 'axios';

interface Consultation {
  consultation_id: string;
  patient_id: string;
  patient_name: string;
  doctor_id: string;
  appointment_id?: string;
  date: string;
  diagnosis: string;
  symptoms: string;
  treatment: string;
  prescription?: string;
  lab_tests_ordered?: string;
  follow_up_date?: string;
  doctor_notes: string;
  status: string;
}

export default function DoctorConsultations() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const doctorId = 'doctor001'; // TODO: Get from authenticated user

  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [selectedConsultation, setSelectedConsultation] = useState<Consultation | null>(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);

  // Form state for new/edit consultation
  const [formData, setFormData] = useState({
    patient_id: '',
    patient_name: '',
    date: new Date().toISOString().split('T')[0],
    symptoms: '',
    diagnosis: '',
    treatment: '',
    prescription: '',
    lab_tests_ordered: '',
    follow_up_date: '',
    doctor_notes: '',
    status: 'completed',
  });

  // Fetch consultations
  const { data: consultationsData, isLoading } = useQuery({
    queryKey: ['doctor-consultations', doctorId],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `http://localhost:8000/api/doctors/${doctorId}/consultations`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data?.data?.consultations || [];
    },
    enabled: !!doctorId,
  });

  // Create consultation mutation
  const createMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        'http://localhost:8000/api/consultations',
        {
          ...data,
          doctor_id: doctorId,
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
      queryClient.invalidateQueries({ queryKey: ['doctor-consultations'] });
      setCreateDialogOpen(false);
      resetForm();
    },
  });

  // Update consultation mutation
  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<typeof formData> }) => {
      const token = localStorage.getItem('token');
      const response = await axios.put(
        `http://localhost:8000/api/consultations/${id}`,
        data,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['doctor-consultations'] });
      setEditDialogOpen(false);
      resetForm();
    },
  });

  const consultations: Consultation[] = consultationsData || [];

  // Filter consultations
  const filteredConsultations = consultations.filter((consult) => {
    if (statusFilter !== 'all' && consult.status !== statusFilter) return false;
    if (
      searchQuery &&
      !consult.patient_name.toLowerCase().includes(searchQuery.toLowerCase()) &&
      !consult.diagnosis.toLowerCase().includes(searchQuery.toLowerCase())
    ) {
      return false;
    }
    return true;
  });

  const resetForm = () => {
    setFormData({
      patient_id: '',
      patient_name: '',
      date: new Date().toISOString().split('T')[0],
      symptoms: '',
      diagnosis: '',
      treatment: '',
      prescription: '',
      lab_tests_ordered: '',
      follow_up_date: '',
      doctor_notes: '',
      status: 'completed',
    });
  };

  const handleView = (consultation: Consultation) => {
    setSelectedConsultation(consultation);
    setViewDialogOpen(true);
  };

  const handleEdit = (consultation: Consultation) => {
    setSelectedConsultation(consultation);
    setFormData({
      patient_id: consultation.patient_id,
      patient_name: consultation.patient_name,
      date: consultation.date,
      symptoms: consultation.symptoms,
      diagnosis: consultation.diagnosis,
      treatment: consultation.treatment,
      prescription: consultation.prescription || '',
      lab_tests_ordered: consultation.lab_tests_ordered || '',
      follow_up_date: consultation.follow_up_date || '',
      doctor_notes: consultation.doctor_notes,
      status: consultation.status,
    });
    setEditDialogOpen(true);
  };

  const handleCreate = () => {
    createMutation.mutate(formData);
  };

  const handleUpdate = () => {
    if (selectedConsultation) {
      updateMutation.mutate({
        id: selectedConsultation.consultation_id,
        data: formData,
      });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'default';
      case 'in_progress':
        return 'secondary';
      case 'pending':
        return 'outline';
      default:
        return 'outline';
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
            <div className="mb-8 flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">Consultations</h1>
                <p className="text-gray-600">Manage patient consultations and medical records</p>
              </div>
              <Button onClick={() => setCreateDialogOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                New Consultation
              </Button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Total Consultations
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-gray-900">{consultations.length}</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    This Month
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-gray-900">
                    {consultations.filter((c) => {
                      const consultDate = new Date(c.date);
                      const now = new Date();
                      return consultDate.getMonth() === now.getMonth() &&
                        consultDate.getFullYear() === now.getFullYear();
                    }).length}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    In Progress
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-gray-900">
                    {consultations.filter((c) => c.status === 'in_progress').length}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Follow-ups Scheduled
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-gray-900">
                    {consultations.filter((c) => c.follow_up_date).length}
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Filters */}
            <Card className="mb-6">
              <CardContent className="pt-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* Search */}
                  <div className="relative md:col-span-2">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Search by patient name or diagnosis..."
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
                      <SelectItem value="completed">Completed</SelectItem>
                      <SelectItem value="in_progress">In Progress</SelectItem>
                      <SelectItem value="pending">Pending</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Consultations List */}
            {isLoading ? (
              <div className="space-y-4">
                {[1, 2, 3, 4].map((i) => (
                  <Card key={i}>
                    <CardContent className="pt-6">
                      <Skeleton className="h-24 w-full" />
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : filteredConsultations.length === 0 ? (
              <Card>
                <CardContent className="pt-12 pb-12 text-center">
                  <Stethoscope className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 text-lg mb-2">No consultations found</p>
                  <p className="text-gray-500 text-sm mb-4">
                    Start by creating a new consultation record
                  </p>
                  <Button onClick={() => setCreateDialogOpen(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    New Consultation
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                {filteredConsultations.map((consultation) => (
                  <Card
                    key={consultation.consultation_id}
                    className="hover:shadow-lg transition-shadow"
                  >
                    <CardContent className="pt-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          {/* Header */}
                          <div className="flex items-center space-x-3 mb-3">
                            <div className="h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
                              <Stethoscope className="h-5 w-5 text-blue-600" />
                            </div>
                            <div>
                              <h3 className="font-semibold text-gray-900">
                                {consultation.patient_name}
                              </h3>
                              <div className="flex items-center space-x-2 text-sm text-gray-600">
                                <Calendar className="h-3 w-3" />
                                <span>{new Date(consultation.date).toLocaleDateString()}</span>
                                <span>•</span>
                                <span>{consultation.consultation_id}</span>
                              </div>
                            </div>
                            <Badge variant={getStatusColor(consultation.status)}>
                              {consultation.status}
                            </Badge>
                          </div>

                          {/* Details Grid */}
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 p-4 bg-gray-50 rounded-lg">
                            <div>
                              <label className="text-xs text-gray-600 uppercase">Diagnosis</label>
                              <p className="font-medium text-gray-900">{consultation.diagnosis}</p>
                            </div>
                            <div>
                              <label className="text-xs text-gray-600 uppercase">Symptoms</label>
                              <p className="text-gray-900">{consultation.symptoms}</p>
                            </div>
                            <div>
                              <label className="text-xs text-gray-600 uppercase">Treatment</label>
                              <p className="text-gray-900">{consultation.treatment}</p>
                            </div>
                            {consultation.follow_up_date && (
                              <div>
                                <label className="text-xs text-gray-600 uppercase">Follow-up</label>
                                <p className="text-gray-900">
                                  {new Date(consultation.follow_up_date).toLocaleDateString()}
                                </p>
                              </div>
                            )}
                          </div>

                          {/* Badges */}
                          <div className="flex items-center space-x-2 mt-4">
                            {consultation.prescription && (
                              <Badge variant="outline" className="text-xs">
                                <Pill className="h-3 w-3 mr-1" />
                                Prescription
                              </Badge>
                            )}
                            {consultation.lab_tests_ordered && (
                              <Badge variant="outline" className="text-xs">
                                <FlaskConical className="h-3 w-3 mr-1" />
                                Lab Tests
                              </Badge>
                            )}
                          </div>
                        </div>

                        {/* Actions */}
                        <div className="flex flex-col space-y-2 ml-4">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleView(consultation)}
                          >
                            <Eye className="h-4 w-4 mr-2" />
                            View
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEdit(consultation)}
                          >
                            <Edit className="h-4 w-4 mr-2" />
                            Edit
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </main>
      </div>

      {/* View Consultation Dialog */}
      <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Consultation Details</DialogTitle>
            <DialogDescription>Complete consultation record</DialogDescription>
          </DialogHeader>

          {selectedConsultation && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-gray-600">Patient Name</Label>
                  <p className="font-medium text-gray-900">{selectedConsultation.patient_name}</p>
                </div>
                <div>
                  <Label className="text-gray-600">Date</Label>
                  <p className="font-medium text-gray-900">
                    {new Date(selectedConsultation.date).toLocaleDateString()}
                  </p>
                </div>
                <div>
                  <Label className="text-gray-600">Patient ID</Label>
                  <p className="font-medium text-gray-900">{selectedConsultation.patient_id}</p>
                </div>
                <div>
                  <Label className="text-gray-600">Status</Label>
                  <Badge variant={getStatusColor(selectedConsultation.status)}>
                    {selectedConsultation.status}
                  </Badge>
                </div>
              </div>

              <div>
                <Label className="text-gray-600">Symptoms</Label>
                <p className="mt-1 text-gray-900">{selectedConsultation.symptoms}</p>
              </div>

              <div>
                <Label className="text-gray-600">Diagnosis</Label>
                <p className="mt-1 text-gray-900">{selectedConsultation.diagnosis}</p>
              </div>

              <div>
                <Label className="text-gray-600">Treatment Plan</Label>
                <p className="mt-1 text-gray-900">{selectedConsultation.treatment}</p>
              </div>

              {selectedConsultation.prescription && (
                <div>
                  <Label className="text-gray-600">Prescription</Label>
                  <p className="mt-1 text-gray-900">{selectedConsultation.prescription}</p>
                </div>
              )}

              {selectedConsultation.lab_tests_ordered && (
                <div>
                  <Label className="text-gray-600">Lab Tests Ordered</Label>
                  <p className="mt-1 text-gray-900">{selectedConsultation.lab_tests_ordered}</p>
                </div>
              )}

              {selectedConsultation.follow_up_date && (
                <div>
                  <Label className="text-gray-600">Follow-up Date</Label>
                  <p className="mt-1 text-gray-900">
                    {new Date(selectedConsultation.follow_up_date).toLocaleDateString()}
                  </p>
                </div>
              )}

              <div>
                <Label className="text-gray-600">Doctor's Notes</Label>
                <p className="mt-1 text-gray-900 whitespace-pre-wrap">
                  {selectedConsultation.doctor_notes}
                </p>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setViewDialogOpen(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Create/Edit Consultation Dialog */}
      <Dialog
        open={createDialogOpen || editDialogOpen}
        onOpenChange={(open) => {
          setCreateDialogOpen(false);
          setEditDialogOpen(false);
          if (!open) resetForm();
        }}
      >
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {createDialogOpen ? 'New Consultation' : 'Edit Consultation'}
            </DialogTitle>
            <DialogDescription>
              {createDialogOpen
                ? 'Create a new consultation record'
                : 'Update consultation information'}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="patient_id">Patient ID *</Label>
                <Input
                  id="patient_id"
                  value={formData.patient_id}
                  onChange={(e) => setFormData({ ...formData, patient_id: e.target.value })}
                  placeholder="Enter patient ID"
                />
              </div>
              <div>
                <Label htmlFor="patient_name">Patient Name *</Label>
                <Input
                  id="patient_name"
                  value={formData.patient_name}
                  onChange={(e) => setFormData({ ...formData, patient_name: e.target.value })}
                  placeholder="Enter patient name"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="date">Date *</Label>
                <Input
                  id="date"
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="status">Status *</Label>
                <Select
                  value={formData.status}
                  onValueChange={(value) => setFormData({ ...formData, status: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="completed">Completed</SelectItem>
                    <SelectItem value="in_progress">In Progress</SelectItem>
                    <SelectItem value="pending">Pending</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <Label htmlFor="symptoms">Symptoms *</Label>
              <Textarea
                id="symptoms"
                value={formData.symptoms}
                onChange={(e) => setFormData({ ...formData, symptoms: e.target.value })}
                placeholder="Describe patient's symptoms"
                rows={3}
              />
            </div>

            <div>
              <Label htmlFor="diagnosis">Diagnosis *</Label>
              <Textarea
                id="diagnosis"
                value={formData.diagnosis}
                onChange={(e) => setFormData({ ...formData, diagnosis: e.target.value })}
                placeholder="Enter diagnosis"
                rows={3}
              />
            </div>

            <div>
              <Label htmlFor="treatment">Treatment Plan *</Label>
              <Textarea
                id="treatment"
                value={formData.treatment}
                onChange={(e) => setFormData({ ...formData, treatment: e.target.value })}
                placeholder="Describe treatment plan"
                rows={3}
              />
            </div>

            <div>
              <Label htmlFor="prescription">Prescription (Optional)</Label>
              <Textarea
                id="prescription"
                value={formData.prescription}
                onChange={(e) => setFormData({ ...formData, prescription: e.target.value })}
                placeholder="List medications and dosages"
                rows={2}
              />
            </div>

            <div>
              <Label htmlFor="lab_tests">Lab Tests Ordered (Optional)</Label>
              <Input
                id="lab_tests"
                value={formData.lab_tests_ordered}
                onChange={(e) => setFormData({ ...formData, lab_tests_ordered: e.target.value })}
                placeholder="e.g., CBC, Blood Sugar"
              />
            </div>

            <div>
              <Label htmlFor="follow_up">Follow-up Date (Optional)</Label>
              <Input
                id="follow_up"
                type="date"
                value={formData.follow_up_date}
                onChange={(e) => setFormData({ ...formData, follow_up_date: e.target.value })}
              />
            </div>

            <div>
              <Label htmlFor="notes">Doctor's Notes *</Label>
              <Textarea
                id="notes"
                value={formData.doctor_notes}
                onChange={(e) => setFormData({ ...formData, doctor_notes: e.target.value })}
                placeholder="Additional notes and observations"
                rows={4}
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setCreateDialogOpen(false);
                setEditDialogOpen(false);
                resetForm();
              }}
            >
              <X className="h-4 w-4 mr-2" />
              Cancel
            </Button>
            <Button
              onClick={createDialogOpen ? handleCreate : handleUpdate}
              disabled={createMutation.isPending || updateMutation.isPending}
            >
              <Save className="h-4 w-4 mr-2" />
              {createDialogOpen ? 'Create' : 'Update'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
