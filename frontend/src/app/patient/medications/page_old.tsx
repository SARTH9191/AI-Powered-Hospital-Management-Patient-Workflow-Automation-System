'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';
import {
  Pill,
  Search,
  Calendar,
  Clock,
  AlertCircle,
  CheckCircle,
  RefreshCw,
  FileText,
  Bell,
} from 'lucide-react';

interface Medication {
  id: string;
  name: string;
  dosage: string;
  frequency: string;
  prescribedDate: string;
  prescribedBy: string;
  status: 'active' | 'completed' | 'refill_needed';
  startDate: string;
  endDate?: string;
  refillsRemaining: number;
  instructions: string;
  sideEffects?: string[];
  interactions?: string[];
}

export default function PatientMedications() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMedication, setSelectedMedication] = useState<Medication | null>(null);
  const [showDetailsDialog, setShowDetailsDialog] = useState(false);
  const [showRefillDialog, setShowRefillDialog] = useState(false);
  const [refillReason, setRefillReason] = useState('');

  const [medications] = useState<Medication[]>([
    {
      id: 'MED001',
      name: 'Lisinopril',
      dosage: '10mg',
      frequency: 'Once daily',
      prescribedDate: '2024-09-01',
      prescribedBy: 'Dr. Sarah Johnson',
      status: 'active',
      startDate: '2024-09-01',
      endDate: '2025-03-01',
      refillsRemaining: 3,
      instructions: 'Take once daily in the morning with or without food',
      sideEffects: ['Dizziness', 'Dry cough', 'Fatigue'],
      interactions: ['NSAIDs', 'Potassium supplements'],
    },
    {
      id: 'MED002',
      name: 'Metformin',
      dosage: '500mg',
      frequency: 'Twice daily',
      prescribedDate: '2024-08-15',
      prescribedBy: 'Dr. Michael Chen',
      status: 'active',
      startDate: '2024-08-15',
      endDate: '2025-02-15',
      refillsRemaining: 2,
      instructions: 'Take with meals (breakfast and dinner)',
      sideEffects: ['Nausea', 'Diarrhea', 'Stomach upset'],
      interactions: ['Alcohol', 'Cimetidine'],
    },
    {
      id: 'MED003',
      name: 'Atorvastatin',
      dosage: '20mg',
      frequency: 'Once daily',
      prescribedDate: '2024-10-01',
      prescribedBy: 'Dr. Michael Chen',
      status: 'active',
      startDate: '2024-10-01',
      endDate: '2025-04-01',
      refillsRemaining: 5,
      instructions: 'Take once daily in the evening',
      sideEffects: ['Muscle pain', 'Headache', 'Digestive issues'],
      interactions: ['Grapefruit juice', 'Clarithromycin'],
    },
    {
      id: 'MED004',
      name: 'Vitamin D3',
      dosage: '2000 IU',
      frequency: 'Once daily',
      prescribedDate: '2024-09-20',
      prescribedBy: 'Dr. Sarah Johnson',
      status: 'refill_needed',
      startDate: '2024-09-20',
      endDate: '2025-03-20',
      refillsRemaining: 0,
      instructions: 'Take once daily with food for better absorption',
      sideEffects: ['Minimal side effects at recommended dose'],
    },
    {
      id: 'MED005',
      name: 'Amoxicillin',
      dosage: '500mg',
      frequency: 'Three times daily',
      prescribedDate: '2024-09-10',
      prescribedBy: 'Dr. Emily Rodriguez',
      status: 'completed',
      startDate: '2024-09-10',
      endDate: '2024-09-17',
      refillsRemaining: 0,
      instructions: 'Take three times daily for 7 days. Complete full course even if feeling better.',
      sideEffects: ['Diarrhea', 'Nausea', 'Rash'],
    },
  ]);

  const handleViewDetails = (medication: Medication) => {
    setSelectedMedication(medication);
    setShowDetailsDialog(true);
  };

  const handleRequestRefill = (medication: Medication) => {
    setSelectedMedication(medication);
    setShowRefillDialog(true);
  };

  const handleSubmitRefill = () => {
    // TODO: Submit refill request
    console.log('Refill request submitted for:', selectedMedication?.name, 'Reason:', refillReason);
    setShowRefillDialog(false);
    setRefillReason('');
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'default';
      case 'completed':
        return 'secondary';
      case 'refill_needed':
        return 'destructive';
      default:
        return 'outline';
    }
  };

  const filteredMedications = medications.filter((med) =>
    `${med.name} ${med.prescribedBy}`.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const activeMedications = filteredMedications.filter(m => m.status === 'active');
  const refillNeeded = filteredMedications.filter(m => m.status === 'refill_needed');
  const completedMedications = filteredMedications.filter(m => m.status === 'completed');

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar role="patient" />
        <main className="flex-1 ml-64 mt-16">
          <div className="p-8">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">My Medications</h1>
              <p className="text-gray-600">Manage your prescriptions and medication history</p>
            </div>

            {/* Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Active Medications
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">{activeMedications.length}</p>
                    <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <Pill className="h-6 w-6 text-blue-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Refill Needed
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">{refillNeeded.length}</p>
                    <div className="h-12 w-12 bg-red-100 rounded-full flex items-center justify-center">
                      <AlertCircle className="h-6 w-6 text-red-600" />
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
                    <p className="text-3xl font-bold text-gray-900">{completedMedications.length}</p>
                    <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center">
                      <CheckCircle className="h-6 w-6 text-green-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Total Prescriptions
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">{medications.length}</p>
                    <div className="h-12 w-12 bg-purple-100 rounded-full flex items-center justify-center">
                      <FileText className="h-6 w-6 text-purple-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Search */}
            <Card className="mb-6">
              <CardContent className="pt-6">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    type="text"
                    placeholder="Search medications..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Refill Alerts */}
            {refillNeeded.length > 0 && (
              <Card className="mb-6 border-red-200 bg-red-50">
                <CardContent className="pt-6">
                  <div className="flex items-start space-x-3">
                    <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
                    <div>
                      <h3 className="font-semibold text-red-900 mb-1">Refill Needed</h3>
                      <p className="text-sm text-red-700 mb-3">
                        {refillNeeded.length} medication{refillNeeded.length > 1 ? 's need' : ' needs'} refilling
                      </p>
                      <div className="space-y-2">
                        {refillNeeded.map((med) => (
                          <div key={med.id} className="flex items-center justify-between bg-white p-3 rounded">
                            <span className="font-medium">{med.name} - {med.dosage}</span>
                            <Button size="sm" onClick={() => handleRequestRefill(med)}>
                              <RefreshCw className="h-4 w-4 mr-1" />
                              Request Refill
                            </Button>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Tabs */}
            <Tabs defaultValue="active" className="space-y-6">
              <TabsList>
                <TabsTrigger value="active">Active ({activeMedications.length})</TabsTrigger>
                <TabsTrigger value="all">All ({filteredMedications.length})</TabsTrigger>
                <TabsTrigger value="completed">Completed ({completedMedications.length})</TabsTrigger>
              </TabsList>

              <TabsContent value="active">
                <div className="space-y-4">
                  {activeMedications.map((medication) => (
                    <Card key={medication.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="pt-6">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-3 mb-2">
                              <Badge variant={getStatusColor(medication.status)}>
                                {medication.status.replace('_', ' ')}
                              </Badge>
                              {medication.refillsRemaining === 0 && (
                                <Badge variant="destructive" className="text-xs">
                                  No Refills Left
                                </Badge>
                              )}
                            </div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-1">
                              {medication.name}
                            </h3>
                            <p className="text-2xl font-bold text-blue-600 mb-3">
                              {medication.dosage}
                            </p>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-gray-600">
                              <div className="flex items-center space-x-1">
                                <Clock className="h-4 w-4" />
                                <span>Frequency: {medication.frequency}</span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <Calendar className="h-4 w-4" />
                                <span>Prescribed: {medication.prescribedDate}</span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <FileText className="h-4 w-4" />
                                <span>Doctor: {medication.prescribedBy}</span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <RefreshCw className="h-4 w-4" />
                                <span>Refills: {medication.refillsRemaining}</span>
                              </div>
                            </div>
                            <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                              <p className="text-sm font-medium text-blue-900 mb-1">
                                <Bell className="h-4 w-4 inline mr-1" />
                                Instructions:
                              </p>
                              <p className="text-sm text-blue-800">{medication.instructions}</p>
                            </div>
                          </div>

                          <div className="flex flex-col space-y-2 ml-4">
                            <Button
                              size="sm"
                              onClick={() => handleViewDetails(medication)}
                            >
                              View Details
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleRequestRefill(medication)}
                            >
                              <RefreshCw className="h-4 w-4 mr-1" />
                              Request Refill
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="all">
                <div className="space-y-4">
                  {filteredMedications.map((medication) => (
                    <Card key={medication.id}>
                      <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <Badge variant={getStatusColor(medication.status)} className="mb-2">
                              {medication.status.replace('_', ' ')}
                            </Badge>
                            <h3 className="text-lg font-semibold mb-1">{medication.name} - {medication.dosage}</h3>
                            <p className="text-sm text-gray-600">{medication.frequency} - {medication.prescribedBy}</p>
                          </div>
                          <Button size="sm" onClick={() => handleViewDetails(medication)}>
                            View Details
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="completed">
                <div className="space-y-4">
                  {completedMedications.map((medication) => (
                    <Card key={medication.id}>
                      <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <Badge variant="secondary" className="mb-2">Completed</Badge>
                            <h3 className="text-lg font-semibold mb-1">{medication.name} - {medication.dosage}</h3>
                            <p className="text-sm text-gray-600">
                              {medication.startDate} to {medication.endDate}
                            </p>
                          </div>
                          <Button size="sm" variant="outline" onClick={() => handleViewDetails(medication)}>
                            View Details
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </main>
      </div>

      {/* Details Dialog */}
      <Dialog open={showDetailsDialog} onOpenChange={setShowDetailsDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{selectedMedication?.name}</DialogTitle>
            <DialogDescription>
              {selectedMedication?.dosage} - {selectedMedication?.frequency}
            </DialogDescription>
          </DialogHeader>
          {selectedMedication && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium text-gray-600">Prescribed By</Label>
                  <p className="text-sm mt-1">{selectedMedication.prescribedBy}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-600">Prescribed Date</Label>
                  <p className="text-sm mt-1">{selectedMedication.prescribedDate}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-600">Start Date</Label>
                  <p className="text-sm mt-1">{selectedMedication.startDate}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-600">End Date</Label>
                  <p className="text-sm mt-1">{selectedMedication.endDate || 'Ongoing'}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-600">Refills Remaining</Label>
                  <p className="text-sm mt-1">{selectedMedication.refillsRemaining}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-600">Status</Label>
                  <Badge variant={getStatusColor(selectedMedication.status)} className="mt-1">
                    {selectedMedication.status.replace('_', ' ')}
                  </Badge>
                </div>
              </div>

              <div>
                <Label className="text-sm font-medium text-gray-600">Instructions</Label>
                <p className="text-sm mt-1 p-3 bg-blue-50 rounded">{selectedMedication.instructions}</p>
              </div>

              {selectedMedication.sideEffects && selectedMedication.sideEffects.length > 0 && (
                <div>
                  <Label className="text-sm font-medium text-gray-600">Possible Side Effects</Label>
                  <ul className="text-sm mt-1 list-disc list-inside p-3 bg-orange-50 rounded">
                    {selectedMedication.sideEffects.map((effect, index) => (
                      <li key={index}>{effect}</li>
                    ))}
                  </ul>
                </div>
              )}

              {selectedMedication.interactions && selectedMedication.interactions.length > 0 && (
                <div>
                  <Label className="text-sm font-medium text-gray-600">Drug Interactions</Label>
                  <ul className="text-sm mt-1 list-disc list-inside p-3 bg-red-50 rounded">
                    {selectedMedication.interactions.map((interaction, index) => (
                      <li key={index}>{interaction}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Refill Dialog */}
      <Dialog open={showRefillDialog} onOpenChange={setShowRefillDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Request Refill</DialogTitle>
            <DialogDescription>
              Request a refill for {selectedMedication?.name}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Medication</Label>
              <p className="text-sm mt-1">{selectedMedication?.name} - {selectedMedication?.dosage}</p>
            </div>
            <div>
              <Label>Reason for Refill (Optional)</Label>
              <Textarea
                placeholder="Enter any notes for your doctor..."
                value={refillReason}
                onChange={(e) => setRefillReason(e.target.value)}
                className="mt-1"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowRefillDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleSubmitRefill}>
              Submit Request
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
