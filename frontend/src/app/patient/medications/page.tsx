'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/hooks/useAuth';
import { pharmacyAPI, type Prescription } from '@/lib/api/pharmacy';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';
import {
  Pill,
  Search,
  Calendar,
  User,
  Clock,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  XCircle,
  Info,
  FileText,
  Loader2,
} from 'lucide-react';
import { toast } from 'sonner';

export default function PatientMedications() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const patientId = 'patient001'; // TODO: Get from authenticated user

  // Fetch prescriptions
  const { data: prescriptionsData, isLoading } = useQuery({
    queryKey: ['prescriptions', patientId],
    queryFn: () => pharmacyAPI.getAllPrescriptions({ patient_id: patientId }),
    enabled: !!patientId,
  });

  const prescriptions = prescriptionsData?.prescriptions || [];

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPrescription, setSelectedPrescription] = useState<Prescription | null>(null);
  const [showDetailsDialog, setShowDetailsDialog] = useState(false);
  const [showRefillDialog, setShowRefillDialog] = useState(false);
  const [refillNotes, setRefillNotes] = useState('');

  // Request refill mutation
  const refillMutation = useMutation({
    mutationFn: (data: { prescription_id: string; notes?: string }) =>
      pharmacyAPI.requestRefill(data.prescription_id, data.notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prescriptions'] });
      toast.success('Refill request submitted successfully!');
      setShowRefillDialog(false);
      setSelectedPrescription(null);
      setRefillNotes('');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to request refill');
    },
  });

  // Filter prescriptions based on search
  const filteredPrescriptions = prescriptions.filter((rx: Prescription) =>
    rx.medication_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    rx.doctor_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Categorize prescriptions
  const activePrescriptions = filteredPrescriptions.filter((rx: Prescription) => rx.status === 'active');
  const expiredPrescriptions = filteredPrescriptions.filter((rx: Prescription) => 
    rx.status === 'expired' || rx.status === 'completed' || rx.status === 'cancelled'
  );
  const allPrescriptions = filteredPrescriptions;

  // Helper functions
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'default';
      case 'expired':
        return 'destructive';
      case 'completed':
        return 'secondary';
      case 'cancelled':
        return 'outline';
      default:
        return 'outline';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'expired':
        return <XCircle className="h-4 w-4 text-red-600" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-gray-600" />;
      case 'cancelled':
        return <XCircle className="h-4 w-4 text-gray-600" />;
      default:
        return null;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const handleViewDetails = (prescription: Prescription) => {
    setSelectedPrescription(prescription);
    setShowDetailsDialog(true);
  };

  const handleRequestRefill = (prescription: Prescription) => {
    setSelectedPrescription(prescription);
    setShowRefillDialog(true);
  };

  const handleConfirmRefill = () => {
    if (selectedPrescription) {
      refillMutation.mutate({
        prescription_id: selectedPrescription.prescription_id,
        notes: refillNotes,
      });
    }
  };

  const isRefillAvailable = (prescription: Prescription) => {
    return prescription.status === 'active' && prescription.refills_remaining > 0;
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
              <h1 className="text-3xl font-bold text-gray-900 mb-2">My Medications</h1>
              <p className="text-gray-600">View and manage your prescriptions</p>
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
                      Total Prescriptions
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <p className="text-3xl font-bold text-gray-900">{allPrescriptions.length}</p>
                      <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
                        <Pill className="h-6 w-6 text-blue-600" />
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-gray-600">
                      Active Medications
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <p className="text-3xl font-bold text-gray-900">{activePrescriptions.length}</p>
                      <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center">
                        <CheckCircle className="h-6 w-6 text-green-600" />
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-gray-600">
                      Refills Available
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <p className="text-3xl font-bold text-gray-900">
                        {activePrescriptions.reduce((sum: number, rx: Prescription) => 
                          sum + rx.refills_remaining, 0
                        )}
                      </p>
                      <div className="h-12 w-12 bg-orange-100 rounded-full flex items-center justify-center">
                        <RefreshCw className="h-6 w-6 text-orange-600" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Search */}
            <div className="mb-6">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search medications..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Tabs */}
            <Tabs defaultValue="active" className="space-y-6">
              <TabsList>
                <TabsTrigger value="active">Active ({activePrescriptions.length})</TabsTrigger>
                <TabsTrigger value="all">All ({allPrescriptions.length})</TabsTrigger>
                <TabsTrigger value="expired">Expired ({expiredPrescriptions.length})</TabsTrigger>
              </TabsList>

              {/* Active Medications */}
              <TabsContent value="active">
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
                ) : activePrescriptions.length === 0 ? (
                  <Card>
                    <CardContent className="p-12 text-center">
                      <Pill className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">No active medications</p>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="space-y-4">
                    {activePrescriptions.map((prescription: Prescription) => (
                      <Card key={prescription.prescription_id}>
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3 mb-3">
                                <h3 className="text-lg font-semibold text-gray-900">
                                  {prescription.medication_name}
                                </h3>
                                <Badge variant={getStatusColor(prescription.status)}>
                                  <div className="flex items-center space-x-1">
                                    {getStatusIcon(prescription.status)}
                                    <span className="capitalize">{prescription.status}</span>
                                  </div>
                                </Badge>
                                {prescription.refills_remaining > 0 && (
                                  <Badge variant="outline">
                                    {prescription.refills_remaining} refill{prescription.refills_remaining > 1 ? 's' : ''} left
                                  </Badge>
                                )}
                              </div>

                              <div className="grid grid-cols-2 gap-4 text-sm mb-3">
                                <div>
                                  <div className="flex items-start text-gray-600 mb-2">
                                    <Pill className="h-4 w-4 mr-2 mt-0.5" />
                                    <div>
                                      <p className="font-medium">Dosage</p>
                                      <p>{prescription.dosage} - {prescription.frequency}</p>
                                    </div>
                                  </div>
                                  <div className="flex items-start text-gray-600">
                                    <User className="h-4 w-4 mr-2 mt-0.5" />
                                    <div>
                                      <p className="font-medium">Prescribed by</p>
                                      <p>{prescription.doctor_name}</p>
                                    </div>
                                  </div>
                                </div>

                                <div>
                                  <div className="flex items-start text-gray-600 mb-2">
                                    <Calendar className="h-4 w-4 mr-2 mt-0.5" />
                                    <div>
                                      <p className="font-medium">Issued</p>
                                      <p>{formatDate(prescription.issued_date)}</p>
                                    </div>
                                  </div>
                                  <div className="flex items-start text-gray-600">
                                    <Clock className="h-4 w-4 mr-2 mt-0.5" />
                                    <div>
                                      <p className="font-medium">Expires</p>
                                      <p>{formatDate(prescription.expiry_date)}</p>
                                    </div>
                                  </div>
                                </div>
                              </div>

                              {prescription.instructions && (
                                <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                                  <div className="flex items-start">
                                    <Info className="h-4 w-4 text-blue-600 mr-2 mt-0.5" />
                                    <div>
                                      <p className="text-sm font-medium text-blue-900">Instructions</p>
                                      <p className="text-sm text-blue-700">{prescription.instructions}</p>
                                    </div>
                                  </div>
                                </div>
                              )}

                              {prescription.side_effects && (
                                <div className="mt-2 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                                  <div className="flex items-start">
                                    <AlertCircle className="h-4 w-4 text-yellow-600 mr-2 mt-0.5" />
                                    <div>
                                      <p className="text-sm font-medium text-yellow-900">Possible Side Effects</p>
                                      <p className="text-sm text-yellow-700">{prescription.side_effects}</p>
                                    </div>
                                  </div>
                                </div>
                              )}
                            </div>

                            <div className="flex flex-col space-y-2 ml-4">
                              <Button
                                size="sm"
                                onClick={() => handleViewDetails(prescription)}
                              >
                                <FileText className="h-4 w-4 mr-2" />
                                Details
                              </Button>
                              {isRefillAvailable(prescription) && (
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => handleRequestRefill(prescription)}
                                  disabled={refillMutation.isPending}
                                >
                                  <RefreshCw className="h-4 w-4 mr-2" />
                                  Request Refill
                                </Button>
                              )}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </TabsContent>

              {/* All Medications */}
              <TabsContent value="all">
                {allPrescriptions.length === 0 ? (
                  <Card>
                    <CardContent className="p-12 text-center">
                      <Pill className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">No medications found</p>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="space-y-4">
                    {allPrescriptions.map((prescription: Prescription) => (
                      <Card key={prescription.prescription_id}>
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3 mb-3">
                                <h3 className="text-lg font-semibold text-gray-900">
                                  {prescription.medication_name}
                                </h3>
                                <Badge variant={getStatusColor(prescription.status)}>
                                  <div className="flex items-center space-x-1">
                                    {getStatusIcon(prescription.status)}
                                    <span className="capitalize">{prescription.status}</span>
                                  </div>
                                </Badge>
                              </div>

                              <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                  <p className="text-gray-600">Dosage: {prescription.dosage}</p>
                                  <p className="text-gray-600">Frequency: {prescription.frequency}</p>
                                </div>
                                <div>
                                  <p className="text-gray-600">Issued: {formatDate(prescription.issued_date)}</p>
                                  <p className="text-gray-600">Expires: {formatDate(prescription.expiry_date)}</p>
                                </div>
                              </div>
                            </div>

                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleViewDetails(prescription)}
                            >
                              <FileText className="h-4 w-4 mr-2" />
                              Details
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </TabsContent>

              {/* Expired Medications */}
              <TabsContent value="expired">
                {expiredPrescriptions.length === 0 ? (
                  <Card>
                    <CardContent className="p-12 text-center">
                      <XCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">No expired medications</p>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="space-y-4">
                    {expiredPrescriptions.map((prescription: Prescription) => (
                      <Card key={prescription.prescription_id}>
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3 mb-3">
                                <h3 className="text-lg font-semibold text-gray-900">
                                  {prescription.medication_name}
                                </h3>
                                <Badge variant={getStatusColor(prescription.status)}>
                                  <div className="flex items-center space-x-1">
                                    {getStatusIcon(prescription.status)}
                                    <span className="capitalize">{prescription.status}</span>
                                  </div>
                                </Badge>
                              </div>

                              <div className="text-sm text-gray-600">
                                <p>Expired on: {formatDate(prescription.expiry_date)}</p>
                              </div>
                            </div>

                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleViewDetails(prescription)}
                            >
                              <FileText className="h-4 w-4 mr-2" />
                              Details
                            </Button>
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

      {/* Details Dialog */}
      <Dialog open={showDetailsDialog} onOpenChange={setShowDetailsDialog}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>Prescription Details</DialogTitle>
            <DialogDescription>
              {selectedPrescription?.medication_name}
            </DialogDescription>
          </DialogHeader>
          {selectedPrescription && (
            <div className="py-4">
              <div className="grid gap-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Medication</p>
                    <p className="text-sm text-gray-900">{selectedPrescription.medication_name}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">Status</p>
                    <Badge variant={getStatusColor(selectedPrescription.status)}>
                      {selectedPrescription.status}
                    </Badge>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">Dosage</p>
                    <p className="text-sm text-gray-900">{selectedPrescription.dosage}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">Frequency</p>
                    <p className="text-sm text-gray-900">{selectedPrescription.frequency}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">Duration</p>
                    <p className="text-sm text-gray-900">{selectedPrescription.duration}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">Quantity</p>
                    <p className="text-sm text-gray-900">{selectedPrescription.quantity}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">Refills Remaining</p>
                    <p className="text-sm text-gray-900">{selectedPrescription.refills_remaining}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">Prescribed By</p>
                    <p className="text-sm text-gray-900">{selectedPrescription.doctor_name}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">Issued Date</p>
                    <p className="text-sm text-gray-900">{formatDate(selectedPrescription.issued_date)}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">Expiry Date</p>
                    <p className="text-sm text-gray-900">{formatDate(selectedPrescription.expiry_date)}</p>
                  </div>
                </div>

                {selectedPrescription.instructions && (
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">Instructions</p>
                    <p className="text-sm text-gray-700 p-3 bg-blue-50 rounded-lg">
                      {selectedPrescription.instructions}
                    </p>
                  </div>
                )}

                {selectedPrescription.side_effects && (
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">Possible Side Effects</p>
                    <p className="text-sm text-gray-700 p-3 bg-yellow-50 rounded-lg">
                      {selectedPrescription.side_effects}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}
          <div className="flex justify-end space-x-2">
            <Button
              variant="outline"
              onClick={() => setShowDetailsDialog(false)}
            >
              Close
            </Button>
            {selectedPrescription && isRefillAvailable(selectedPrescription) && (
              <Button onClick={() => {
                setShowDetailsDialog(false);
                handleRequestRefill(selectedPrescription);
              }}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Request Refill
              </Button>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Refill Request Dialog */}
      <Dialog open={showRefillDialog} onOpenChange={setShowRefillDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Request Prescription Refill</DialogTitle>
            <DialogDescription>
              Request a refill for {selectedPrescription?.medication_name}
            </DialogDescription>
          </DialogHeader>
          {selectedPrescription && (
            <div className="py-4">
              <div className="space-y-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm"><strong>Medication:</strong> {selectedPrescription.medication_name}</p>
                  <p className="text-sm"><strong>Dosage:</strong> {selectedPrescription.dosage}</p>
                  <p className="text-sm"><strong>Refills Available:</strong> {selectedPrescription.refills_remaining}</p>
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-700">Additional Notes (Optional)</label>
                  <Textarea
                    value={refillNotes}
                    onChange={(e) => setRefillNotes(e.target.value)}
                    placeholder="Any special instructions or notes for the pharmacy..."
                    rows={3}
                    className="mt-1"
                  />
                </div>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setShowRefillDialog(false);
                setRefillNotes('');
              }}
              disabled={refillMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              onClick={handleConfirmRefill}
              disabled={refillMutation.isPending}
            >
              {refillMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Submit Request
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
