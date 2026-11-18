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
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';
import {
  Pill,
  Search,
  Plus,
  FileText,
  Calendar,
  User,
  Clock,
  AlertCircle,
  CheckCircle,
  Eye,
  Download,
} from 'lucide-react';
import axios from 'axios';

interface Prescription {
  prescription_id: string;
  patient_id: string;
  patient_name: string;
  doctor_id: string;
  medication_name: string;
  dosage: string;
  frequency: string;
  duration: string;
  quantity: number;
  refills: number;
  instructions: string;
  prescribed_date: string;
  start_date: string;
  end_date: string;
  status: string;
  notes?: string;
}

export default function DoctorPrescriptions() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const doctorId = 'doctor001'; // TODO: Get from authenticated user

  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [selectedPrescription, setSelectedPrescription] = useState<Prescription | null>(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    patient_id: '',
    patient_name: '',
    medication_name: '',
    dosage: '',
    frequency: '',
    duration: '',
    quantity: 30,
    refills: 0,
    instructions: '',
    start_date: new Date().toISOString().split('T')[0],
    notes: '',
  });

  // Fetch prescriptions
  const { data: prescriptionsData, isLoading } = useQuery({
    queryKey: ['doctor-prescriptions', doctorId],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `http://localhost:8000/api/doctors/${doctorId}/prescriptions`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data?.data?.prescriptions || [];
    },
    enabled: !!doctorId,
  });

  // Create prescription mutation
  const createMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        'http://localhost:8000/api/prescriptions',
        {
          ...data,
          doctor_id: doctorId,
          prescribed_date: new Date().toISOString().split('T')[0],
          status: 'active',
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
      queryClient.invalidateQueries({ queryKey: ['doctor-prescriptions'] });
      setCreateDialogOpen(false);
      resetForm();
    },
  });

  const prescriptions: Prescription[] = prescriptionsData || [];

  // Filter prescriptions
  const filteredPrescriptions = prescriptions.filter((rx) => {
    if (statusFilter !== 'all' && rx.status !== statusFilter) return false;
    if (
      searchQuery &&
      !rx.patient_name.toLowerCase().includes(searchQuery.toLowerCase()) &&
      !rx.medication_name.toLowerCase().includes(searchQuery.toLowerCase())
    ) {
      return false;
    }
    return true;
  });

  const resetForm = () => {
    setFormData({
      patient_id: '',
      patient_name: '',
      medication_name: '',
      dosage: '',
      frequency: '',
      duration: '',
      quantity: 30,
      refills: 0,
      instructions: '',
      start_date: new Date().toISOString().split('T')[0],
      notes: '',
    });
  };

  const handleView = (prescription: Prescription) => {
    setSelectedPrescription(prescription);
    setViewDialogOpen(true);
  };

  const handleCreate = () => {
    createMutation.mutate(formData);
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'default';
      case 'completed':
        return 'secondary';
      case 'expired':
        return 'outline';
      case 'cancelled':
        return 'destructive';
      default:
        return 'outline';
    }
  };

  const isExpiringSoon = (endDate: string) => {
    const end = new Date(endDate);
    const now = new Date();
    const daysUntilExpiry = Math.ceil((end.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    return daysUntilExpiry <= 7 && daysUntilExpiry > 0;
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
                <h1 className="text-3xl font-bold text-gray-900 mb-2">Prescriptions</h1>
                <p className="text-gray-600">Manage patient prescriptions and medications</p>
              </div>
              <Button onClick={() => setCreateDialogOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                New Prescription
              </Button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Total Prescriptions
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-gray-900">{prescriptions.length}</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Active
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-green-600">
                    {prescriptions.filter((p) => p.status === 'active').length}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Expiring Soon
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-orange-600">
                    {prescriptions.filter((p) => isExpiringSoon(p.end_date)).length}
                  </p>
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
                    {prescriptions.filter((p) => {
                      const prescribedDate = new Date(p.prescribed_date);
                      const now = new Date();
                      return prescribedDate.getMonth() === now.getMonth() &&
                        prescribedDate.getFullYear() === now.getFullYear();
                    }).length}
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
                      placeholder="Search by patient or medication..."
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
                      <SelectItem value="active">Active</SelectItem>
                      <SelectItem value="completed">Completed</SelectItem>
                      <SelectItem value="expired">Expired</SelectItem>
                      <SelectItem value="cancelled">Cancelled</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Prescriptions List */}
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
            ) : filteredPrescriptions.length === 0 ? (
              <Card>
                <CardContent className="pt-12 pb-12 text-center">
                  <Pill className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 text-lg mb-2">No prescriptions found</p>
                  <p className="text-gray-500 text-sm mb-4">
                    Start by creating a new prescription
                  </p>
                  <Button onClick={() => setCreateDialogOpen(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    New Prescription
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {filteredPrescriptions.map((prescription) => (
                  <Card
                    key={prescription.prescription_id}
                    className="hover:shadow-lg transition-shadow"
                  >
                    <CardContent className="pt-6">
                      {/* Header */}
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
                            <Pill className="h-6 w-6 text-blue-600" />
                          </div>
                          <div>
                            <h3 className="font-semibold text-gray-900">
                              {prescription.medication_name}
                            </h3>
                            <p className="text-sm text-gray-600">{prescription.dosage}</p>
                          </div>
                        </div>
                        <div className="flex flex-col items-end space-y-2">
                          <Badge variant={getStatusColor(prescription.status)}>
                            {prescription.status}
                          </Badge>
                          {isExpiringSoon(prescription.end_date) && (
                            <Badge variant="outline" className="text-xs text-orange-600">
                              <AlertCircle className="h-3 w-3 mr-1" />
                              Expiring Soon
                            </Badge>
                          )}
                        </div>
                      </div>

                      {/* Patient Info */}
                      <div className="bg-gray-50 rounded-lg p-3 mb-4">
                        <div className="flex items-center space-x-2 text-sm">
                          <User className="h-4 w-4 text-gray-400" />
                          <span className="font-medium text-gray-900">
                            {prescription.patient_name}
                          </span>
                          <span className="text-gray-600">•</span>
                          <span className="text-gray-600">{prescription.patient_id}</span>
                        </div>
                      </div>

                      {/* Prescription Details */}
                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <div>
                          <label className="text-xs text-gray-600 uppercase">Frequency</label>
                          <p className="font-medium text-gray-900">{prescription.frequency}</p>
                        </div>
                        <div>
                          <label className="text-xs text-gray-600 uppercase">Duration</label>
                          <p className="font-medium text-gray-900">{prescription.duration}</p>
                        </div>
                        <div>
                          <label className="text-xs text-gray-600 uppercase">Quantity</label>
                          <p className="font-medium text-gray-900">{prescription.quantity}</p>
                        </div>
                        <div>
                          <label className="text-xs text-gray-600 uppercase">Refills</label>
                          <p className="font-medium text-gray-900">{prescription.refills}</p>
                        </div>
                      </div>

                      {/* Dates */}
                      <div className="flex items-center justify-between text-sm text-gray-600 mb-4 pb-4 border-b">
                        <div className="flex items-center space-x-1">
                          <Calendar className="h-3 w-3" />
                          <span>
                            {new Date(prescription.start_date).toLocaleDateString()} -{' '}
                            {new Date(prescription.end_date).toLocaleDateString()}
                          </span>
                        </div>
                      </div>

                      {/* Instructions */}
                      {prescription.instructions && (
                        <div className="mb-4">
                          <label className="text-xs text-gray-600 uppercase">Instructions</label>
                          <p className="text-sm text-gray-900 mt-1">{prescription.instructions}</p>
                        </div>
                      )}

                      {/* Actions */}
                      <div className="flex space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          className="flex-1"
                          onClick={() => handleView(prescription)}
                        >
                          <Eye className="h-4 w-4 mr-2" />
                          View Details
                        </Button>
                        <Button variant="outline" size="sm">
                          <Download className="h-4 w-4 mr-2" />
                          Print
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

      {/* View Prescription Dialog */}
      <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Prescription Details</DialogTitle>
            <DialogDescription>Complete prescription information</DialogDescription>
          </DialogHeader>

          {selectedPrescription && (
            <div className="space-y-6">
              {/* Header */}
              <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    {selectedPrescription.medication_name}
                  </h3>
                  <p className="text-sm text-gray-600">{selectedPrescription.prescription_id}</p>
                </div>
                <Badge variant={getStatusColor(selectedPrescription.status)}>
                  {selectedPrescription.status}
                </Badge>
              </div>

              {/* Patient Info */}
              <div>
                <Label className="text-gray-600">Patient</Label>
                <p className="font-medium text-gray-900">
                  {selectedPrescription.patient_name} ({selectedPrescription.patient_id})
                </p>
              </div>

              {/* Medication Details */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-gray-600">Dosage</Label>
                  <p className="font-medium text-gray-900">{selectedPrescription.dosage}</p>
                </div>
                <div>
                  <Label className="text-gray-600">Frequency</Label>
                  <p className="font-medium text-gray-900">{selectedPrescription.frequency}</p>
                </div>
                <div>
                  <Label className="text-gray-600">Duration</Label>
                  <p className="font-medium text-gray-900">{selectedPrescription.duration}</p>
                </div>
                <div>
                  <Label className="text-gray-600">Quantity</Label>
                  <p className="font-medium text-gray-900">{selectedPrescription.quantity}</p>
                </div>
                <div>
                  <Label className="text-gray-600">Refills Allowed</Label>
                  <p className="font-medium text-gray-900">{selectedPrescription.refills}</p>
                </div>
                <div>
                  <Label className="text-gray-600">Prescribed Date</Label>
                  <p className="font-medium text-gray-900">
                    {new Date(selectedPrescription.prescribed_date).toLocaleDateString()}
                  </p>
                </div>
              </div>

              {/* Period */}
              <div>
                <Label className="text-gray-600">Treatment Period</Label>
                <p className="font-medium text-gray-900">
                  {new Date(selectedPrescription.start_date).toLocaleDateString()} to{' '}
                  {new Date(selectedPrescription.end_date).toLocaleDateString()}
                </p>
              </div>

              {/* Instructions */}
              <div>
                <Label className="text-gray-600">Instructions</Label>
                <p className="text-gray-900 mt-1">{selectedPrescription.instructions}</p>
              </div>

              {/* Notes */}
              {selectedPrescription.notes && (
                <div>
                  <Label className="text-gray-600">Additional Notes</Label>
                  <p className="text-gray-900 mt-1">{selectedPrescription.notes}</p>
                </div>
              )}
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setViewDialogOpen(false)}>
              Close
            </Button>
            <Button>
              <Download className="h-4 w-4 mr-2" />
              Print Prescription
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Create Prescription Dialog */}
      <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>New Prescription</DialogTitle>
            <DialogDescription>Create a new prescription for a patient</DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {/* Patient Info */}
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

            {/* Medication Details */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="medication">Medication Name *</Label>
                <Input
                  id="medication"
                  value={formData.medication_name}
                  onChange={(e) => setFormData({ ...formData, medication_name: e.target.value })}
                  placeholder="e.g., Amoxicillin"
                />
              </div>
              <div>
                <Label htmlFor="dosage">Dosage *</Label>
                <Input
                  id="dosage"
                  value={formData.dosage}
                  onChange={(e) => setFormData({ ...formData, dosage: e.target.value })}
                  placeholder="e.g., 500mg"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="frequency">Frequency *</Label>
                <Select
                  value={formData.frequency}
                  onValueChange={(value) => setFormData({ ...formData, frequency: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select frequency" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Once daily">Once daily</SelectItem>
                    <SelectItem value="Twice daily">Twice daily</SelectItem>
                    <SelectItem value="Three times daily">Three times daily</SelectItem>
                    <SelectItem value="Four times daily">Four times daily</SelectItem>
                    <SelectItem value="Every 6 hours">Every 6 hours</SelectItem>
                    <SelectItem value="Every 8 hours">Every 8 hours</SelectItem>
                    <SelectItem value="As needed">As needed</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="duration">Duration *</Label>
                <Input
                  id="duration"
                  value={formData.duration}
                  onChange={(e) => setFormData({ ...formData, duration: e.target.value })}
                  placeholder="e.g., 7 days, 2 weeks, 1 month"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="quantity">Quantity *</Label>
                <Input
                  id="quantity"
                  type="number"
                  value={formData.quantity}
                  onChange={(e) => setFormData({ ...formData, quantity: parseInt(e.target.value) })}
                  placeholder="Number of pills/units"
                />
              </div>
              <div>
                <Label htmlFor="refills">Refills Allowed *</Label>
                <Input
                  id="refills"
                  type="number"
                  value={formData.refills}
                  onChange={(e) => setFormData({ ...formData, refills: parseInt(e.target.value) })}
                  placeholder="Number of refills"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="start_date">Start Date *</Label>
              <Input
                id="start_date"
                type="date"
                value={formData.start_date}
                onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
              />
            </div>

            <div>
              <Label htmlFor="instructions">Instructions *</Label>
              <Textarea
                id="instructions"
                value={formData.instructions}
                onChange={(e) => setFormData({ ...formData, instructions: e.target.value })}
                placeholder="e.g., Take with food. Complete full course even if symptoms improve."
                rows={3}
              />
            </div>

            <div>
              <Label htmlFor="notes">Additional Notes (Optional)</Label>
              <Textarea
                id="notes"
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                placeholder="Any additional notes or warnings"
                rows={2}
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setCreateDialogOpen(false);
                resetForm();
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleCreate}
              disabled={createMutation.isPending}
            >
              <FileText className="h-4 w-4 mr-2" />
              Create Prescription
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
