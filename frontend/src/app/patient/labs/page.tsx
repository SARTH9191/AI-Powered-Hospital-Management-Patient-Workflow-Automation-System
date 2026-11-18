'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@/hooks/useAuth';
import { labsAPI, type LabTest } from '@/lib/api/labs';
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
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';
import {
  TestTube,
  Download,
  Search,
  Calendar,
  AlertTriangle,
  CheckCircle,
  Clock,
  TrendingUp,
  TrendingDown,
  Minus,
  FileText,
  User,
} from 'lucide-react';
import { toast } from 'sonner';

export default function PatientLabResults() {
  const { user } = useAuth();
  const patientId = 'patient001'; // TODO: Get from authenticated user

  // Fetch lab tests
  const { data: labsData, isLoading } = useQuery({
    queryKey: ['labs', patientId],
    queryFn: () => labsAPI.getAllLabTests({ patient_id: patientId }),
    enabled: !!patientId,
  });

  const labTests = labsData?.tests || [];

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedResult, setSelectedResult] = useState<LabTest | null>(null);
  const [showDetailsDialog, setShowDetailsDialog] = useState(false);

  // Filter tests based on search
  const filteredTests = labTests.filter((test) =>
    (test.test_name ?? '').toLowerCase().includes(searchQuery.toLowerCase()) ||
    (test.test_type ?? '').toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Categorize tests
  const pendingTests = filteredTests.filter((t) => t.status === 'pending' || t.status === 'in_progress');
  const completedTests = filteredTests.filter((t) => t.status === 'completed');
  const allTests = filteredTests;

  // Helper functions
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'default';
      case 'pending':
        return 'secondary';
      case 'in_progress':
        return 'outline';
      default:
        return 'outline';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-600" />;
      case 'in_progress':
        return <TestTube className="h-4 w-4 text-blue-600" />;
      default:
        return null;
    }
  };

  const getPriorityColor = (priority?: string) => {
    switch (priority?.toLowerCase()) {
      case 'urgent':
      case 'high':
        return 'destructive';
      case 'normal':
        return 'secondary';
      case 'low':
        return 'outline';
      default:
        return 'outline';
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

  const handleViewDetails = (test: LabTest) => {
    setSelectedResult(test);
    setShowDetailsDialog(true);
  };

  const handleDownloadPDF = (test: LabTest) => {
    toast.info('PDF download feature coming soon!');
    // TODO: Implement PDF download
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
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Lab Results</h1>
              <p className="text-gray-600">View your lab test results and history</p>
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
                      All Tests
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <p className="text-3xl font-bold text-gray-900">{allTests.length}</p>
                      <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
                        <TestTube className="h-6 w-6 text-blue-600" />
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
                      <p className="text-3xl font-bold text-gray-900">{pendingTests.length}</p>
                      <div className="h-12 w-12 bg-yellow-100 rounded-full flex items-center justify-center">
                        <Clock className="h-6 w-6 text-yellow-600" />
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
                      <p className="text-3xl font-bold text-gray-900">{completedTests.length}</p>
                      <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center">
                        <CheckCircle className="h-6 w-6 text-green-600" />
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
                  placeholder="Search lab tests..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Tabs */}
            <Tabs defaultValue="all" className="space-y-6">
              <TabsList>
                <TabsTrigger value="all">All Tests ({allTests.length})</TabsTrigger>
                <TabsTrigger value="pending">Pending ({pendingTests.length})</TabsTrigger>
                <TabsTrigger value="completed">Completed ({completedTests.length})</TabsTrigger>
              </TabsList>

              {/* All Tests */}
              <TabsContent value="all">
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
                ) : allTests.length === 0 ? (
                  <Card>
                    <CardContent className="p-12 text-center">
                      <TestTube className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">No lab tests found</p>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="space-y-4">
                    {allTests.map((test: LabTest) => (
                      <Card key={test.test_id}>
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3 mb-3">
                                <h3 className="text-lg font-semibold text-gray-900">
                                  {test.test_name}
                                </h3>
                                <Badge variant={getStatusColor(test.status)}>
                                  <div className="flex items-center space-x-1">
                                    {getStatusIcon(test.status)}
                                    <span className="capitalize">{test.status}</span>
                                  </div>
                                </Badge>
                                {test.priority && (
                                  <Badge variant={getPriorityColor(test.priority)}>
                                    {test.priority}
                                  </Badge>
                                )}
                              </div>

                              <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                  <div className="flex items-center text-gray-600 mb-2">
                                    <FileText className="h-4 w-4 mr-2" />
                                    <span>Type: {test.test_type}</span>
                                  </div>
                                  <div className="flex items-center text-gray-600">
                                    <User className="h-4 w-4 mr-2" />
                                    <span>Ordered by: {test.ordered_by}</span>
                                  </div>
                                </div>

                                <div>
                                  <div className="flex items-center text-gray-600 mb-2">
                                    <Calendar className="h-4 w-4 mr-2" />
                                    <span>Ordered: {formatDate(test.order_date)}</span>
                                  </div>
                                  {test.completed_date && (
                                    <div className="flex items-center text-gray-600">
                                      <CheckCircle className="h-4 w-4 mr-2" />
                                      <span>Completed: {formatDate(test.completed_date)}</span>
                                    </div>
                                  )}
                                  {test.scheduled_date && !test.completed_date && (
                                    <div className="flex items-center text-gray-600">
                                      <Clock className="h-4 w-4 mr-2" />
                                      <span>Scheduled: {formatDate(test.scheduled_date)}</span>
                                    </div>
                                  )}
                                </div>
                              </div>

                              {test.notes && (
                                <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                                  <p className="text-sm text-gray-700">
                                    <span className="font-medium">Notes: </span>
                                    {test.notes}
                                  </p>
                                </div>
                              )}
                            </div>

                            <div className="flex flex-col space-y-2 ml-4">
                              {test.status === 'completed' && (
                                <>
                                  <Button
                                    size="sm"
                                    onClick={() => handleViewDetails(test)}
                                  >
                                    <FileText className="h-4 w-4 mr-2" />
                                    View Results
                                  </Button>
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => handleDownloadPDF(test)}
                                  >
                                    <Download className="h-4 w-4 mr-2" />
                                    Download PDF
                                  </Button>
                                </>
                              )}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </TabsContent>

              {/* Pending Tests */}
              <TabsContent value="pending">
                {pendingTests.length === 0 ? (
                  <Card>
                    <CardContent className="p-12 text-center">
                      <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">No pending lab tests</p>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="space-y-4">
                    {pendingTests.map((test: LabTest) => (
                      <Card key={test.test_id}>
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3 mb-3">
                                <h3 className="text-lg font-semibold text-gray-900">
                                  {test.test_name}
                                </h3>
                                <Badge variant={getStatusColor(test.status)}>
                                  <div className="flex items-center space-x-1">
                                    {getStatusIcon(test.status)}
                                    <span className="capitalize">{test.status}</span>
                                  </div>
                                </Badge>
                              </div>

                              <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                  <div className="flex items-center text-gray-600 mb-2">
                                    <FileText className="h-4 w-4 mr-2" />
                                    <span>Type: {test.test_type}</span>
                                  </div>
                                  <div className="flex items-center text-gray-600">
                                    <User className="h-4 w-4 mr-2" />
                                    <span>Ordered by: {test.ordered_by}</span>
                                  </div>
                                </div>

                                <div>
                                  {test.scheduled_date && (
                                    <div className="flex items-center text-gray-600">
                                      <Clock className="h-4 w-4 mr-2" />
                                      <span>Scheduled: {formatDate(test.scheduled_date)}</span>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </TabsContent>

              {/* Completed Tests */}
              <TabsContent value="completed">
                {completedTests.length === 0 ? (
                  <Card>
                    <CardContent className="p-12 text-center">
                      <CheckCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">No completed lab tests</p>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="space-y-4">
                    {completedTests.map((test: LabTest) => (
                      <Card key={test.test_id}>
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3 mb-3">
                                <h3 className="text-lg font-semibold text-gray-900">
                                  {test.test_name}
                                </h3>
                                <Badge variant={getStatusColor(test.status)}>
                                  <div className="flex items-center space-x-1">
                                    {getStatusIcon(test.status)}
                                    <span className="capitalize">{test.status}</span>
                                  </div>
                                </Badge>
                              </div>

                              <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                  <div className="flex items-center text-gray-600 mb-2">
                                    <FileText className="h-4 w-4 mr-2" />
                                    <span>Type: {test.test_type}</span>
                                  </div>
                                  <div className="flex items-center text-gray-600">
                                    <User className="h-4 w-4 mr-2" />
                                    <span>Ordered by: {test.ordered_by}</span>
                                  </div>
                                </div>

                                <div>
                                  {test.completed_date && (
                                    <div className="flex items-center text-gray-600">
                                      <CheckCircle className="h-4 w-4 mr-2" />
                                      <span>Completed: {formatDate(test.completed_date)}</span>
                                    </div>
                                  )}
                                </div>
                              </div>

                              {test.results && (
                                <div className="mt-3 p-3 bg-green-50 rounded-lg border border-green-200">
                                  <p className="text-sm font-medium text-green-900">
                                    ✓ Results Available
                                  </p>
                                </div>
                              )}
                            </div>

                            <div className="flex flex-col space-y-2 ml-4">
                              <Button
                                size="sm"
                                onClick={() => handleViewDetails(test)}
                              >
                                <FileText className="h-4 w-4 mr-2" />
                                View Results
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleDownloadPDF(test)}
                              >
                                <Download className="h-4 w-4 mr-2" />
                                Download PDF
                              </Button>
                            </div>
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

      {/* Test Details Dialog */}
      <Dialog open={showDetailsDialog} onOpenChange={setShowDetailsDialog}>
        <DialogContent className="sm:max-w-[700px]">
          <DialogHeader>
            <DialogTitle>Lab Test Results</DialogTitle>
            <DialogDescription>
              {selectedResult?.test_name}
            </DialogDescription>
          </DialogHeader>
          {selectedResult && (
            <div className="py-4">
              <div className="grid gap-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Test Type</p>
                    <p className="text-sm text-gray-900">{selectedResult.test_type}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">Ordered By</p>
                    <p className="text-sm text-gray-900">{selectedResult.ordered_by}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">Order Date</p>
                    <p className="text-sm text-gray-900">{formatDate(selectedResult.order_date)}</p>
                  </div>
                  {selectedResult.completed_date && (
                    <div>
                      <p className="text-sm font-medium text-gray-600">Completed Date</p>
                      <p className="text-sm text-gray-900">{formatDate(selectedResult.completed_date)}</p>
                    </div>
                  )}
                </div>

                {selectedResult.results && (
                  <div className="mt-4">
                    <h4 className="font-medium text-gray-900 mb-3">Test Results</h4>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                        {JSON.stringify(selectedResult.results, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}

                {selectedResult.notes && (
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">Notes</p>
                    <p className="text-sm text-gray-700">{selectedResult.notes}</p>
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
            {selectedResult && (
              <Button onClick={() => handleDownloadPDF(selectedResult)}>
                <Download className="h-4 w-4 mr-2" />
                Download PDF
              </Button>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
