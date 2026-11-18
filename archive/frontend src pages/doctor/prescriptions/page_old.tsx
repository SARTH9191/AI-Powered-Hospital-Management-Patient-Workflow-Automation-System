'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
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
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Pill,
  Plus,
  Search,
  Printer,
  Mail,
  Eye,
  Edit,
  CheckCircle,
  XCircle,
  Clock,
  AlertCircle,
  Calendar,
} from 'lucide-react';
import { toast } from 'sonner';
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';

interface Prescription {
  id: string;
  patientName: string;
  patientId: string;
  medications: {
    name: string;
    dosage: string;
    frequency: string;
    duration: string;
    quantity: number;
    instructions?: string;
  }[];
  diagnosis: string;
  dateIssued: string;
  validUntil: string;
  status: 'active' | 'expired' | 'completed' | 'cancelled';
  refillsAllowed: number;
  refillsUsed: number;
  notes?: string;
}

export default function PrescriptionsPage() {
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([]);
  const [filteredPrescriptions, setFilteredPrescriptions] = useState<Prescription[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false);
  const [selectedPrescription, setSelectedPrescription] = useState<Prescription | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const [newPrescription, setNewPrescription] = useState({
    patientName: '',
    patientId: '',
    diagnosis: '',
    medications: [
      {
        name: '',
        dosage: '',
        frequency: 'Once daily',
        duration: '7 days',
        quantity: 0,
        instructions: '',
      },
    ],
    refillsAllowed: 0,
    notes: '',
  });

  useEffect(() => {
    // Mock prescriptions data
    const mockPrescriptions: Prescription[] = [
      {
        id: '1',
        patientName: 'Emily Davis',
        patientId: 'P1234',
        medications: [
          {
            name: 'Amoxicillin 500mg',
            dosage: '500mg',
            frequency: '3 times daily',
            duration: '14 days',
            quantity: 42,
            instructions: 'Take with meals',
          },
        ],
        diagnosis: 'Bacterial infection',
        dateIssued: '2024-10-15',
        validUntil: '2024-10-29',
        status: 'active',
        refillsAllowed: 0,
        refillsUsed: 0,
        notes: 'Complete full course even if symptoms improve',
      },
      {
        id: '2',
        patientName: 'James Wilson',
        patientId: 'P1235',
        medications: [
          {
            name: 'Atorvastatin 20mg',
            dosage: '20mg',
            frequency: 'Once daily',
            duration: '90 days',
            quantity: 90,
            instructions: 'Take at bedtime',
          },
          {
            name: 'Aspirin 81mg',
            dosage: '81mg',
            frequency: 'Once daily',
            duration: '90 days',
            quantity: 90,
            instructions: 'Take in the morning',
          },
        ],
        diagnosis: 'Hyperlipidemia, Cardiovascular disease prevention',
        dateIssued: '2024-09-20',
        validUntil: '2024-12-20',
        status: 'active',
        refillsAllowed: 3,
        refillsUsed: 1,
        notes: 'Regular lipid panel monitoring required',
      },
      {
        id: '3',
        patientName: 'Sarah Miller',
        patientId: 'P1236',
        medications: [
          {
            name: 'Ibuprofen 400mg',
            dosage: '400mg',
            frequency: '3 times daily as needed',
            duration: '14 days',
            quantity: 42,
            instructions: 'Take with food',
          },
        ],
        diagnosis: 'Post-surgical pain management',
        dateIssued: '2024-10-10',
        validUntil: '2024-10-24',
        status: 'active',
        refillsAllowed: 1,
        refillsUsed: 0,
        notes: 'Do not exceed maximum daily dose of 1200mg',
      },
      {
        id: '4',
        patientName: 'Michael Brown',
        patientId: 'P1237',
        medications: [
          {
            name: 'Metformin 500mg',
            dosage: '500mg',
            frequency: 'Twice daily',
            duration: '90 days',
            quantity: 180,
            instructions: 'Take with breakfast and dinner',
          },
        ],
        diagnosis: 'Type 2 Diabetes Mellitus',
        dateIssued: '2024-08-15',
        validUntil: '2024-11-15',
        status: 'active',
        refillsAllowed: 5,
        refillsUsed: 2,
        notes: 'Monitor blood glucose regularly',
      },
      {
        id: '5',
        patientName: 'Linda Taylor',
        patientId: 'P1238',
        medications: [
          {
            name: 'Lisinopril 10mg',
            dosage: '10mg',
            frequency: 'Once daily',
            duration: '90 days',
            quantity: 90,
            instructions: 'Take in the morning',
          },
        ],
        diagnosis: 'Hypertension',
        dateIssued: '2024-07-20',
        validUntil: '2024-10-20',
        status: 'expired',
        refillsAllowed: 3,
        refillsUsed: 3,
        notes: 'Prescription expired - renewal required',
      },
      {
        id: '6',
        patientName: 'Robert Johnson',
        patientId: 'P1239',
        medications: [
          {
            name: 'Omeprazole 20mg',
            dosage: '20mg',
            frequency: 'Once daily',
            duration: '30 days',
            quantity: 30,
            instructions: 'Take before breakfast',
          },
        ],
        diagnosis: 'Gastroesophageal reflux disease (GERD)',
        dateIssued: '2024-09-18',
        validUntil: '2024-10-18',
        status: 'completed',
        refillsAllowed: 0,
        refillsUsed: 0,
        notes: 'Treatment completed successfully',
      },
    ];

    setTimeout(() => {
      setPrescriptions(mockPrescriptions);
      setFilteredPrescriptions(mockPrescriptions);
      setIsLoading(false);
    }, 500);
  }, []);

  useEffect(() => {
    let filtered = prescriptions;

    if (searchQuery) {
      filtered = filtered.filter(
        (rx) =>
          rx.patientName.toLowerCase().includes(searchQuery.toLowerCase()) ||
          rx.patientId.toLowerCase().includes(searchQuery.toLowerCase()) ||
          rx.medications.some((med) => med.name.toLowerCase().includes(searchQuery.toLowerCase())) ||
          rx.diagnosis.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter((rx) => rx.status === statusFilter);
    }

    setFilteredPrescriptions(filtered);
  }, [searchQuery, statusFilter, prescriptions]);

  const handleCreatePrescription = () => {
    const today = new Date();
    const validUntil = new Date(today);
    validUntil.setDate(today.getDate() + 90);

    const prescription: Prescription = {
      id: Date.now().toString(),
      patientName: newPrescription.patientName,
      patientId: newPrescription.patientId,
      medications: newPrescription.medications.filter((med) => med.name && med.dosage),
      diagnosis: newPrescription.diagnosis,
      dateIssued: today.toISOString().split('T')[0],
      validUntil: validUntil.toISOString().split('T')[0],
      status: 'active',
      refillsAllowed: newPrescription.refillsAllowed,
      refillsUsed: 0,
      notes: newPrescription.notes,
    };

    setPrescriptions([prescription, ...prescriptions]);
    toast.success('Prescription created successfully', {
      description: `For patient: ${newPrescription.patientName}`,
    });

    setIsCreateDialogOpen(false);
    setNewPrescription({
      patientName: '',
      patientId: '',
      diagnosis: '',
      medications: [
        {
          name: '',
          dosage: '',
          frequency: 'Once daily',
          duration: '7 days',
          quantity: 0,
          instructions: '',
        },
      ],
      refillsAllowed: 0,
      notes: '',
    });
  };

  const addMedicationField = () => {
    setNewPrescription({
      ...newPrescription,
      medications: [
        ...newPrescription.medications,
        {
          name: '',
          dosage: '',
          frequency: 'Once daily',
          duration: '7 days',
          quantity: 0,
          instructions: '',
        },
      ],
    });
  };

  const updateMedication = (index: number, field: string, value: any) => {
    const updatedMedications = [...newPrescription.medications];
    updatedMedications[index] = { ...updatedMedications[index], [field]: value };
    setNewPrescription({ ...newPrescription, medications: updatedMedications });
  };

  const removeMedication = (index: number) => {
    if (newPrescription.medications.length > 1) {
      const updatedMedications = newPrescription.medications.filter((_, i) => i !== index);
      setNewPrescription({ ...newPrescription, medications: updatedMedications });
    }
  };

  const handlePrint = (prescription: Prescription) => {
    toast.success('Printing prescription', {
      description: `For patient: ${prescription.patientName}`,
    });
  };

  const handleEmail = (prescription: Prescription) => {
    toast.success('Email sent', {
      description: `Prescription sent to ${prescription.patientName}`,
    });
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      active: 'bg-green-100 text-green-800',
      expired: 'bg-red-100 text-red-800',
      completed: 'bg-gray-100 text-gray-800',
      cancelled: 'bg-orange-100 text-orange-800',
    };
    return <Badge className={styles[status as keyof typeof styles] || 'bg-gray-100 text-gray-800'}>{status}</Badge>;
  };

  const getStatusIcon = (status: string) => {
    if (status === 'active') return <CheckCircle className="h-5 w-5 text-green-600" />;
    if (status === 'expired') return <XCircle className="h-5 w-5 text-red-600" />;
    if (status === 'completed') return <CheckCircle className="h-5 w-5 text-gray-600" />;
    return <AlertCircle className="h-5 w-5 text-orange-600" />;
  };

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
                <h1 className="text-3xl font-bold text-gray-900">Prescriptions</h1>
                <p className="text-gray-500 mt-1">Create and manage patient prescriptions</p>
              </div>
              <Button onClick={() => setIsCreateDialogOpen(true)} className="bg-blue-600 hover:bg-blue-700">
                <Plus className="h-4 w-4 mr-2" />
                New Prescription
              </Button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>Total Prescriptions</CardDescription>
                  <CardTitle className="text-3xl">{prescriptions.length}</CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>Active</CardDescription>
                  <CardTitle className="text-3xl text-green-600">
                    {prescriptions.filter((rx) => rx.status === 'active').length}
                  </CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>Expiring Soon</CardDescription>
                  <CardTitle className="text-3xl text-orange-600">
                    {
                      prescriptions.filter((rx) => {
                        const daysUntilExpiry = Math.floor(
                          (new Date(rx.validUntil).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)
                        );
                        return daysUntilExpiry <= 7 && daysUntilExpiry >= 0 && rx.status === 'active';
                      }).length
                    }
                  </CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>This Month</CardDescription>
                  <CardTitle className="text-3xl">
                    {
                      prescriptions.filter((rx) => {
                        const monthAgo = new Date();
                        monthAgo.setMonth(monthAgo.getMonth() - 1);
                        return new Date(rx.dateIssued) >= monthAgo;
                      }).length
                    }
                  </CardTitle>
                </CardHeader>
              </Card>
            </div>

            {/* Filters */}
            <Card>
              <CardHeader>
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="flex-1 relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Search by patient name, medication, or diagnosis..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger className="w-[180px]">
                      <SelectValue placeholder="Filter by status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Status</SelectItem>
                      <SelectItem value="active">Active</SelectItem>
                      <SelectItem value="expired">Expired</SelectItem>
                      <SelectItem value="completed">Completed</SelectItem>
                      <SelectItem value="cancelled">Cancelled</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardHeader>
            </Card>

            {/* Prescriptions List */}
            <Tabs defaultValue="all" className="space-y-6">
              <TabsList>
                <TabsTrigger value="all">All ({filteredPrescriptions.length})</TabsTrigger>
                <TabsTrigger value="active">
                  Active ({filteredPrescriptions.filter((rx) => rx.status === 'active').length})
                </TabsTrigger>
                <TabsTrigger value="expired">
                  Expired ({filteredPrescriptions.filter((rx) => rx.status === 'expired').length})
                </TabsTrigger>
              </TabsList>

              <TabsContent value="all" className="space-y-4">
                {filteredPrescriptions.length === 0 ? (
                  <Card>
                    <CardContent className="py-12 text-center text-gray-500">No prescriptions found</CardContent>
                  </Card>
                ) : (
                  filteredPrescriptions.map((rx) => (
                    <Card key={rx.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="pt-6">
                        <div className="flex items-start justify-between">
                          <div className="flex items-start space-x-4 flex-1">
                            <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
                              {getStatusIcon(rx.status)}
                            </div>
                            <div className="flex-1">
                              <div className="flex items-center space-x-3 mb-2">
                                <h3 className="font-semibold text-lg">{rx.patientName}</h3>
                                {getStatusBadge(rx.status)}
                              </div>
                              <p className="text-gray-600 mb-3">{rx.diagnosis}</p>

                              {/* Medications */}
                              <div className="space-y-2 mb-3">
                                {rx.medications.map((med, idx) => (
                                  <div key={idx} className="flex items-start space-x-2 text-sm">
                                    <Pill className="h-4 w-4 text-blue-600 mt-0.5" />
                                    <div>
                                      <span className="font-medium">{med.name}</span>
                                      <span className="text-gray-500">
                                        {' '}
                                        - {med.dosage}, {med.frequency} for {med.duration}
                                      </span>
                                      {med.instructions && (
                                        <p className="text-gray-500 italic text-xs">{med.instructions}</p>
                                      )}
                                    </div>
                                  </div>
                                ))}
                              </div>

                              <div className="flex items-center space-x-4 text-sm text-gray-500">
                                <span className="flex items-center">
                                  <Calendar className="h-3 w-3 mr-1" />
                                  Issued: {new Date(rx.dateIssued).toLocaleDateString()}
                                </span>
                                <span className="flex items-center">
                                  <Clock className="h-3 w-3 mr-1" />
                                  Valid until: {new Date(rx.validUntil).toLocaleDateString()}
                                </span>
                                <span>
                                  Refills: {rx.refillsUsed}/{rx.refillsAllowed}
                                </span>
                              </div>
                            </div>
                          </div>
                          <div className="flex space-x-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => {
                                setSelectedPrescription(rx);
                                setIsViewDialogOpen(true);
                              }}
                            >
                              <Eye className="h-4 w-4 mr-2" />
                              View
                            </Button>
                            <Button variant="outline" size="sm" onClick={() => handlePrint(rx)}>
                              <Printer className="h-4 w-4 mr-2" />
                              Print
                            </Button>
                            <Button variant="outline" size="sm" onClick={() => handleEmail(rx)}>
                              <Mail className="h-4 w-4 mr-2" />
                              Email
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))
                )}
              </TabsContent>

              <TabsContent value="active" className="space-y-4">
                {filteredPrescriptions
                  .filter((rx) => rx.status === 'active')
                  .map((rx) => (
                    <Card key={rx.id}>
                      <CardContent className="pt-6">
                        <div className="flex items-start justify-between">
                          <div>
                            <h3 className="font-semibold text-lg mb-1">{rx.patientName}</h3>
                            <p className="text-gray-600 mb-2">{rx.diagnosis}</p>
                            <div className="space-y-1">
                              {rx.medications.map((med, idx) => (
                                <p key={idx} className="text-sm text-gray-700">
                                  • {med.name} - {med.frequency}
                                </p>
                              ))}
                            </div>
                          </div>
                          <div className="flex space-x-2">
                            <Button variant="outline" size="sm" onClick={() => handlePrint(rx)}>
                              <Printer className="h-4 w-4" />
                            </Button>
                            <Button variant="outline" size="sm" onClick={() => handleEmail(rx)}>
                              <Mail className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
              </TabsContent>

              <TabsContent value="expired" className="space-y-4">
                {filteredPrescriptions
                  .filter((rx) => rx.status === 'expired')
                  .map((rx) => (
                    <Card key={rx.id} className="border-red-200 bg-red-50">
                      <CardContent className="pt-6">
                        <div className="flex items-start justify-between">
                          <div>
                            <div className="flex items-center space-x-2 mb-2">
                              <XCircle className="h-5 w-5 text-red-600" />
                              <h3 className="font-semibold text-lg">{rx.patientName}</h3>
                            </div>
                            <p className="text-gray-700 mb-1">{rx.diagnosis}</p>
                            <p className="text-sm text-red-700">
                              Expired: {new Date(rx.validUntil).toLocaleDateString()}
                            </p>
                          </div>
                          <Button className="bg-blue-600 hover:bg-blue-700">Renew Prescription</Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
              </TabsContent>
            </Tabs>

            {/* Create Prescription Dialog */}
            <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
              <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>Create New Prescription</DialogTitle>
                  <DialogDescription>Write a new prescription for a patient</DialogDescription>
                </DialogHeader>
                <div className="space-y-6 py-4">
                  {/* Patient Info */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="patient-name">Patient Name *</Label>
                      <Input
                        id="patient-name"
                        value={newPrescription.patientName}
                        onChange={(e) => setNewPrescription({ ...newPrescription, patientName: e.target.value })}
                        placeholder="John Doe"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="patient-id">Patient ID *</Label>
                      <Input
                        id="patient-id"
                        value={newPrescription.patientId}
                        onChange={(e) => setNewPrescription({ ...newPrescription, patientId: e.target.value })}
                        placeholder="P1234"
                      />
                    </div>
                  </div>

                  {/* Diagnosis */}
                  <div className="space-y-2">
                    <Label htmlFor="diagnosis">Diagnosis *</Label>
                    <Input
                      id="diagnosis"
                      value={newPrescription.diagnosis}
                      onChange={(e) => setNewPrescription({ ...newPrescription, diagnosis: e.target.value })}
                      placeholder="e.g., Hypertension, Type 2 Diabetes"
                    />
                  </div>

                  {/* Medications */}
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <Label>Medications *</Label>
                      <Button type="button" variant="outline" size="sm" onClick={addMedicationField}>
                        <Plus className="h-4 w-4 mr-2" />
                        Add Medication
                      </Button>
                    </div>

                    {newPrescription.medications.map((med, index) => (
                      <Card key={index} className="p-4">
                        <div className="space-y-4">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-semibold text-sm">Medication {index + 1}</h4>
                            {newPrescription.medications.length > 1 && (
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                onClick={() => removeMedication(index)}
                                className="text-red-600 hover:bg-red-50"
                              >
                                Remove
                              </Button>
                            )}
                          </div>

                          <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                              <Label>Medication Name</Label>
                              <Input
                                value={med.name}
                                onChange={(e) => updateMedication(index, 'name', e.target.value)}
                                placeholder="e.g., Amoxicillin"
                              />
                            </div>
                            <div className="space-y-2">
                              <Label>Dosage</Label>
                              <Input
                                value={med.dosage}
                                onChange={(e) => updateMedication(index, 'dosage', e.target.value)}
                                placeholder="e.g., 500mg"
                              />
                            </div>
                          </div>

                          <div className="grid grid-cols-3 gap-4">
                            <div className="space-y-2">
                              <Label>Frequency</Label>
                              <Select
                                value={med.frequency}
                                onValueChange={(value) => updateMedication(index, 'frequency', value)}
                              >
                                <SelectTrigger>
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="Once daily">Once daily</SelectItem>
                                  <SelectItem value="Twice daily">Twice daily</SelectItem>
                                  <SelectItem value="3 times daily">3 times daily</SelectItem>
                                  <SelectItem value="4 times daily">4 times daily</SelectItem>
                                  <SelectItem value="As needed">As needed</SelectItem>
                                  <SelectItem value="Every 4 hours">Every 4 hours</SelectItem>
                                  <SelectItem value="Every 6 hours">Every 6 hours</SelectItem>
                                  <SelectItem value="Every 8 hours">Every 8 hours</SelectItem>
                                </SelectContent>
                              </Select>
                            </div>
                            <div className="space-y-2">
                              <Label>Duration</Label>
                              <Select
                                value={med.duration}
                                onValueChange={(value) => updateMedication(index, 'duration', value)}
                              >
                                <SelectTrigger>
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="3 days">3 days</SelectItem>
                                  <SelectItem value="7 days">7 days</SelectItem>
                                  <SelectItem value="14 days">14 days</SelectItem>
                                  <SelectItem value="30 days">30 days</SelectItem>
                                  <SelectItem value="60 days">60 days</SelectItem>
                                  <SelectItem value="90 days">90 days</SelectItem>
                                  <SelectItem value="Ongoing">Ongoing</SelectItem>
                                </SelectContent>
                              </Select>
                            </div>
                            <div className="space-y-2">
                              <Label>Quantity</Label>
                              <Input
                                type="number"
                                value={med.quantity}
                                onChange={(e) => updateMedication(index, 'quantity', Number(e.target.value))}
                                placeholder="30"
                              />
                            </div>
                          </div>

                          <div className="space-y-2">
                            <Label>Instructions</Label>
                            <Input
                              value={med.instructions}
                              onChange={(e) => updateMedication(index, 'instructions', e.target.value)}
                              placeholder="e.g., Take with food, Avoid alcohol"
                            />
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>

                  {/* Refills */}
                  <div className="space-y-2">
                    <Label htmlFor="refills">Refills Allowed</Label>
                    <Select
                      value={newPrescription.refillsAllowed.toString()}
                      onValueChange={(value) =>
                        setNewPrescription({ ...newPrescription, refillsAllowed: Number(value) })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="0">No refills</SelectItem>
                        <SelectItem value="1">1 refill</SelectItem>
                        <SelectItem value="2">2 refills</SelectItem>
                        <SelectItem value="3">3 refills</SelectItem>
                        <SelectItem value="5">5 refills</SelectItem>
                        <SelectItem value="11">11 refills (1 year)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Notes */}
                  <div className="space-y-2">
                    <Label htmlFor="notes">Additional Notes</Label>
                    <Textarea
                      id="notes"
                      value={newPrescription.notes}
                      onChange={(e) => setNewPrescription({ ...newPrescription, notes: e.target.value })}
                      placeholder="Any special instructions or warnings..."
                      rows={3}
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleCreatePrescription} className="bg-blue-600 hover:bg-blue-700">
                    Create Prescription
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>

            {/* View Prescription Dialog */}
            <Dialog open={isViewDialogOpen} onOpenChange={setIsViewDialogOpen}>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>Prescription Details</DialogTitle>
                </DialogHeader>
                {selectedPrescription && (
                  <div className="space-y-6 py-4">
                    <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
                      <div>
                        <p className="text-sm text-gray-500">Patient</p>
                        <p className="font-semibold">{selectedPrescription.patientName}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Patient ID</p>
                        <p className="font-semibold">{selectedPrescription.patientId}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Date Issued</p>
                        <p className="font-semibold">
                          {new Date(selectedPrescription.dateIssued).toLocaleDateString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Valid Until</p>
                        <p className="font-semibold">
                          {new Date(selectedPrescription.validUntil).toLocaleDateString()}
                        </p>
                      </div>
                    </div>

                    <div>
                      <h3 className="font-semibold mb-2">Diagnosis</h3>
                      <p className="text-gray-700">{selectedPrescription.diagnosis}</p>
                    </div>

                    <div>
                      <h3 className="font-semibold mb-3">Medications</h3>
                      <div className="space-y-3">
                        {selectedPrescription.medications.map((med, idx) => (
                          <div key={idx} className="p-4 border rounded-lg">
                            <h4 className="font-semibold text-blue-900 mb-2">{med.name}</h4>
                            <div className="grid grid-cols-2 gap-2 text-sm">
                              <div>
                                <span className="text-gray-500">Dosage:</span> {med.dosage}
                              </div>
                              <div>
                                <span className="text-gray-500">Frequency:</span> {med.frequency}
                              </div>
                              <div>
                                <span className="text-gray-500">Duration:</span> {med.duration}
                              </div>
                              <div>
                                <span className="text-gray-500">Quantity:</span> {med.quantity}
                              </div>
                            </div>
                            {med.instructions && (
                              <p className="text-sm text-gray-600 mt-2 italic">{med.instructions}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>

                    {selectedPrescription.notes && (
                      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                        <h3 className="font-semibold text-yellow-900 mb-2">Notes</h3>
                        <p className="text-yellow-800">{selectedPrescription.notes}</p>
                      </div>
                    )}

                    <div className="flex justify-end space-x-2">
                      <Button variant="outline" onClick={() => setIsViewDialogOpen(false)}>
                        Close
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => handlePrint(selectedPrescription)}
                        className="border-blue-600 text-blue-600 hover:bg-blue-50"
                      >
                        <Printer className="h-4 w-4 mr-2" />
                        Print
                      </Button>
                      <Button
                        onClick={() => handleEmail(selectedPrescription)}
                        className="bg-blue-600 hover:bg-blue-700"
                      >
                        <Mail className="h-4 w-4 mr-2" />
                        Email to Patient
                      </Button>
                    </div>
                  </div>
                )}
              </DialogContent>
            </Dialog>
          </div>
        </main>
      </div>
    </div>
  );
}
