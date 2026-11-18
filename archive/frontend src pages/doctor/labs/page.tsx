'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
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
import {
  TestTube,
  Download,
  Eye,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  TrendingDown,
  Search,
  Filter,
  Calendar,
} from 'lucide-react';
import { toast } from 'sonner';
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';

interface LabResult {
  id: string;
  patientName: string;
  patientId: string;
  testName: string;
  testType: 'blood' | 'urine' | 'imaging' | 'biopsy' | 'other';
  dateOrdered: string;
  dateCompleted?: string;
  status: 'pending' | 'completed' | 'abnormal';
  results?: {
    parameter: string;
    value: string;
    unit: string;
    normalRange: string;
    status: 'normal' | 'high' | 'low' | 'critical';
  }[];
  notes?: string;
  orderedBy: string;
}

export default function LabResultsPage() {
  const [labResults, setLabResults] = useState<LabResult[]>([]);
  const [filteredResults, setFilteredResults] = useState<LabResult[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [selectedResult, setSelectedResult] = useState<LabResult | null>(null);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Mock lab results data
    const mockLabResults: LabResult[] = [
      {
        id: '1',
        patientName: 'Emily Davis',
        patientId: 'P1234',
        testName: 'Complete Blood Count (CBC)',
        testType: 'blood',
        dateOrdered: '2024-10-16',
        dateCompleted: '2024-10-17',
        status: 'completed',
        orderedBy: 'Dr. Smith',
        results: [
          { parameter: 'WBC', value: '7.2', unit: 'K/uL', normalRange: '4.5-11.0', status: 'normal' },
          { parameter: 'RBC', value: '4.8', unit: 'M/uL', normalRange: '4.5-5.9', status: 'normal' },
          { parameter: 'Hemoglobin', value: '14.5', unit: 'g/dL', normalRange: '13.5-17.5', status: 'normal' },
          { parameter: 'Hematocrit', value: '42', unit: '%', normalRange: '38.3-48.6', status: 'normal' },
          { parameter: 'Platelets', value: '250', unit: 'K/uL', normalRange: '150-400', status: 'normal' },
        ],
        notes: 'All values within normal limits',
      },
      {
        id: '2',
        patientName: 'James Wilson',
        patientId: 'P1235',
        testName: 'Lipid Panel',
        testType: 'blood',
        dateOrdered: '2024-10-15',
        dateCompleted: '2024-10-16',
        status: 'abnormal',
        orderedBy: 'Dr. Johnson',
        results: [
          { parameter: 'Total Cholesterol', value: '240', unit: 'mg/dL', normalRange: '<200', status: 'high' },
          { parameter: 'LDL Cholesterol', value: '160', unit: 'mg/dL', normalRange: '<100', status: 'high' },
          { parameter: 'HDL Cholesterol', value: '38', unit: 'mg/dL', normalRange: '>40', status: 'low' },
          { parameter: 'Triglycerides', value: '180', unit: 'mg/dL', normalRange: '<150', status: 'high' },
        ],
        notes: 'Elevated cholesterol levels. Recommend lifestyle modifications and consider statin therapy.',
      },
      {
        id: '3',
        patientName: 'Sarah Miller',
        patientId: 'P1236',
        testName: 'Urinalysis',
        testType: 'urine',
        dateOrdered: '2024-10-17',
        dateCompleted: '2024-10-18',
        status: 'completed',
        orderedBy: 'Dr. Smith',
        results: [
          { parameter: 'Color', value: 'Yellow', unit: '', normalRange: 'Yellow', status: 'normal' },
          { parameter: 'pH', value: '6.0', unit: '', normalRange: '4.5-8.0', status: 'normal' },
          { parameter: 'Protein', value: 'Negative', unit: '', normalRange: 'Negative', status: 'normal' },
          { parameter: 'Glucose', value: 'Negative', unit: '', normalRange: 'Negative', status: 'normal' },
          { parameter: 'Blood', value: 'Negative', unit: '', normalRange: 'Negative', status: 'normal' },
        ],
        notes: 'Normal urinalysis',
      },
      {
        id: '4',
        patientName: 'Michael Brown',
        patientId: 'P1237',
        testName: 'Thyroid Function Test',
        testType: 'blood',
        dateOrdered: '2024-10-18',
        status: 'pending',
        orderedBy: 'Dr. Taylor',
        notes: 'Testing for hypothyroidism symptoms',
      },
      {
        id: '5',
        patientName: 'Linda Taylor',
        patientId: 'P1238',
        testName: 'HbA1c (Diabetes)',
        testType: 'blood',
        dateOrdered: '2024-10-14',
        dateCompleted: '2024-10-15',
        status: 'abnormal',
        orderedBy: 'Dr. Smith',
        results: [
          { parameter: 'HbA1c', value: '7.2', unit: '%', normalRange: '<5.7', status: 'high' },
          { parameter: 'Fasting Glucose', value: '135', unit: 'mg/dL', normalRange: '70-100', status: 'high' },
        ],
        notes: 'Indicates poor glucose control. Adjust diabetes medication and schedule follow-up.',
      },
      {
        id: '6',
        patientName: 'Robert Johnson',
        patientId: 'P1239',
        testName: 'Liver Function Test',
        testType: 'blood',
        dateOrdered: '2024-10-13',
        dateCompleted: '2024-10-14',
        status: 'abnormal',
        orderedBy: 'Dr. Wilson',
        results: [
          { parameter: 'ALT', value: '85', unit: 'U/L', normalRange: '7-56', status: 'high' },
          { parameter: 'AST', value: '72', unit: 'U/L', normalRange: '10-40', status: 'high' },
          { parameter: 'Bilirubin', value: '1.5', unit: 'mg/dL', normalRange: '0.1-1.2', status: 'high' },
          { parameter: 'Albumin', value: '4.2', unit: 'g/dL', normalRange: '3.4-5.4', status: 'normal' },
        ],
        notes: 'Elevated liver enzymes. Recommend alcohol abstinence and repeat test in 2 weeks.',
      },
      {
        id: '7',
        patientName: 'Mary Smith',
        patientId: 'P1240',
        testName: 'Chest X-Ray',
        testType: 'imaging',
        dateOrdered: '2024-10-17',
        dateCompleted: '2024-10-18',
        status: 'completed',
        orderedBy: 'Dr. Brown',
        notes: 'No acute cardiopulmonary findings. Lungs clear, heart size normal.',
      },
    ];

    setTimeout(() => {
      setLabResults(mockLabResults);
      setFilteredResults(mockLabResults);
      setIsLoading(false);
    }, 500);
  }, []);

  useEffect(() => {
    let filtered = labResults;

    if (searchQuery) {
      filtered = filtered.filter(
        (result) =>
          result.patientName.toLowerCase().includes(searchQuery.toLowerCase()) ||
          result.testName.toLowerCase().includes(searchQuery.toLowerCase()) ||
          result.patientId.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter((result) => result.status === statusFilter);
    }

    if (typeFilter !== 'all') {
      filtered = filtered.filter((result) => result.testType === typeFilter);
    }

    setFilteredResults(filtered);
  }, [searchQuery, statusFilter, typeFilter, labResults]);

  const getStatusBadge = (status: string) => {
    const styles = {
      completed: 'bg-green-100 text-green-800',
      pending: 'bg-yellow-100 text-yellow-800',
      abnormal: 'bg-red-100 text-red-800',
    };
    return <Badge className={styles[status as keyof typeof styles] || 'bg-gray-100 text-gray-800'}>{status}</Badge>;
  };

  const getResultStatusIcon = (status: string) => {
    if (status === 'normal') return <CheckCircle className="h-4 w-4 text-green-600" />;
    if (status === 'high') return <TrendingUp className="h-4 w-4 text-red-600" />;
    if (status === 'low') return <TrendingDown className="h-4 w-4 text-orange-600" />;
    if (status === 'critical') return <AlertTriangle className="h-4 w-4 text-red-600" />;
    return null;
  };

  const handleViewDetails = (result: LabResult) => {
    setSelectedResult(result);
    setIsDetailsOpen(true);
  };

  const handleDownloadPDF = (result: LabResult) => {
    toast.success(`Downloading ${result.testName} report`, {
      description: `For patient: ${result.patientName}`,
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar role="doctor" />
        <main className="flex-1 ml-64 mt-16">
          <div className="p-8">
            {/* Header */}
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Lab Results</h1>
              <p className="text-gray-500 mt-1">View and manage patient lab test results</p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>Total Tests</CardDescription>
                  <CardTitle className="text-3xl">{labResults.length}</CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>Pending</CardDescription>
                  <CardTitle className="text-3xl text-yellow-600">
                    {labResults.filter((r) => r.status === 'pending').length}
                  </CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>Abnormal Results</CardDescription>
                  <CardTitle className="text-3xl text-red-600">
                    {labResults.filter((r) => r.status === 'abnormal').length}
                  </CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>This Week</CardDescription>
                  <CardTitle className="text-3xl">
                    {
                      labResults.filter((r) => {
                        const weekAgo = new Date();
                        weekAgo.setDate(weekAgo.getDate() - 7);
                        return new Date(r.dateOrdered) >= weekAgo;
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
                      placeholder="Search by patient name, test name, or ID..."
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
                      <SelectItem value="completed">Completed</SelectItem>
                      <SelectItem value="pending">Pending</SelectItem>
                      <SelectItem value="abnormal">Abnormal</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={typeFilter} onValueChange={setTypeFilter}>
                    <SelectTrigger className="w-[180px]">
                      <SelectValue placeholder="Filter by type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Types</SelectItem>
                      <SelectItem value="blood">Blood Test</SelectItem>
                      <SelectItem value="urine">Urine Test</SelectItem>
                      <SelectItem value="imaging">Imaging</SelectItem>
                      <SelectItem value="biopsy">Biopsy</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardHeader>
            </Card>

            {/* Results Tabs */}
            <Tabs defaultValue="all" className="space-y-6">
              <TabsList>
                <TabsTrigger value="all">All Results ({filteredResults.length})</TabsTrigger>
                <TabsTrigger value="abnormal">
                  Abnormal ({filteredResults.filter((r) => r.status === 'abnormal').length})
                </TabsTrigger>
                <TabsTrigger value="pending">
                  Pending ({filteredResults.filter((r) => r.status === 'pending').length})
                </TabsTrigger>
                <TabsTrigger value="completed">
                  Completed ({filteredResults.filter((r) => r.status === 'completed').length})
                </TabsTrigger>
              </TabsList>

              <TabsContent value="all" className="space-y-4">
                {filteredResults.length === 0 ? (
                  <Card>
                    <CardContent className="py-12 text-center text-gray-500">No lab results found</CardContent>
                  </Card>
                ) : (
                  filteredResults.map((result) => (
                    <Card key={result.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="pt-6">
                        <div className="flex items-start justify-between">
                          <div className="flex items-start space-x-4 flex-1">
                            <Avatar className="h-12 w-12">
                              <AvatarFallback>
                                {result.patientName
                                  .split(' ')
                                  .map((n) => n[0])
                                  .join('')}
                              </AvatarFallback>
                            </Avatar>
                            <div className="flex-1">
                              <div className="flex items-center space-x-3 mb-2">
                                <h3 className="font-semibold text-lg">{result.patientName}</h3>
                                {getStatusBadge(result.status)}
                                <Badge variant="outline" className="capitalize">
                                  {result.testType}
                                </Badge>
                              </div>
                              <p className="text-gray-600 mb-2">{result.testName}</p>
                              <div className="flex items-center space-x-4 text-sm text-gray-500">
                                <span className="flex items-center">
                                  <Calendar className="h-3 w-3 mr-1" />
                                  Ordered: {new Date(result.dateOrdered).toLocaleDateString()}
                                </span>
                                {result.dateCompleted && (
                                  <span className="flex items-center">
                                    <TestTube className="h-3 w-3 mr-1" />
                                    Completed: {new Date(result.dateCompleted).toLocaleDateString()}
                                  </span>
                                )}
                                <span>Ordered by: {result.orderedBy}</span>
                              </div>
                              {result.status === 'abnormal' && result.results && (
                                <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                                  <div className="flex items-center space-x-2 text-red-800 mb-2">
                                    <AlertTriangle className="h-4 w-4" />
                                    <span className="font-semibold text-sm">Abnormal Values Detected</span>
                                  </div>
                                  <div className="text-sm text-red-700">
                                    {result.results
                                      .filter((r) => r.status !== 'normal')
                                      .map((r) => `${r.parameter}: ${r.value} ${r.unit}`)
                                      .join(', ')}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                          <div className="flex space-x-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleViewDetails(result)}
                              disabled={result.status === 'pending'}
                            >
                              <Eye className="h-4 w-4 mr-2" />
                              View Details
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleDownloadPDF(result)}
                              disabled={result.status === 'pending'}
                            >
                              <Download className="h-4 w-4 mr-2" />
                              Download
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))
                )}
              </TabsContent>

              <TabsContent value="abnormal" className="space-y-4">
                {filteredResults
                  .filter((r) => r.status === 'abnormal')
                  .map((result) => (
                    <Card key={result.id} className="border-red-200">
                      <CardContent className="pt-6">
                        <div className="flex items-start justify-between">
                          <div className="flex items-start space-x-4 flex-1">
                            <Avatar className="h-12 w-12">
                              <AvatarFallback>
                                {result.patientName
                                  .split(' ')
                                  .map((n) => n[0])
                                  .join('')}
                              </AvatarFallback>
                            </Avatar>
                            <div className="flex-1">
                              <h3 className="font-semibold text-lg mb-2">{result.patientName}</h3>
                              <p className="text-gray-600 mb-2">{result.testName}</p>
                              {result.results && (
                                <div className="space-y-1">
                                  {result.results
                                    .filter((r) => r.status !== 'normal')
                                    .map((r, idx) => (
                                      <div key={idx} className="flex items-center space-x-2 text-sm">
                                        {getResultStatusIcon(r.status)}
                                        <span className="font-medium">{r.parameter}:</span>
                                        <span className="text-red-600">
                                          {r.value} {r.unit}
                                        </span>
                                        <span className="text-gray-500">(Normal: {r.normalRange})</span>
                                      </div>
                                    ))}
                                </div>
                              )}
                            </div>
                          </div>
                          <Button variant="outline" size="sm" onClick={() => handleViewDetails(result)}>
                            <Eye className="h-4 w-4 mr-2" />
                            View Full Report
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
              </TabsContent>

              <TabsContent value="pending" className="space-y-4">
                {filteredResults
                  .filter((r) => r.status === 'pending')
                  .map((result) => (
                    <Card key={result.id}>
                      <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <div className="h-12 w-12 bg-yellow-100 rounded-full flex items-center justify-center">
                              <TestTube className="h-6 w-6 text-yellow-600" />
                            </div>
                            <div>
                              <h3 className="font-semibold">{result.testName}</h3>
                              <p className="text-gray-600 text-sm">
                                {result.patientName} • Ordered: {new Date(result.dateOrdered).toLocaleDateString()}
                              </p>
                            </div>
                          </div>
                          <Badge className="bg-yellow-100 text-yellow-800">In Progress</Badge>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
              </TabsContent>

              <TabsContent value="completed" className="space-y-4">
                {filteredResults
                  .filter((r) => r.status === 'completed')
                  .map((result) => (
                    <Card key={result.id}>
                      <CardContent className="pt-6">
                        <div className="flex items-start justify-between">
                          <div className="flex items-start space-x-4">
                            <Avatar className="h-12 w-12">
                              <AvatarFallback>
                                {result.patientName
                                  .split(' ')
                                  .map((n) => n[0])
                                  .join('')}
                              </AvatarFallback>
                            </Avatar>
                            <div>
                              <h3 className="font-semibold">{result.patientName}</h3>
                              <p className="text-gray-600">{result.testName}</p>
                              <p className="text-sm text-gray-500 mt-1">
                                Completed: {result.dateCompleted && new Date(result.dateCompleted).toLocaleDateString()}
                              </p>
                            </div>
                          </div>
                          <div className="flex space-x-2">
                            <Button variant="outline" size="sm" onClick={() => handleViewDetails(result)}>
                              <Eye className="h-4 w-4" />
                            </Button>
                            <Button variant="outline" size="sm" onClick={() => handleDownloadPDF(result)}>
                              <Download className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
              </TabsContent>
            </Tabs>

            {/* Details Dialog */}
            <Dialog open={isDetailsOpen} onOpenChange={setIsDetailsOpen}>
              <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>Lab Result Details</DialogTitle>
                  <DialogDescription>
                    {selectedResult?.testName} - {selectedResult?.patientName}
                  </DialogDescription>
                </DialogHeader>
                {selectedResult && (
                  <div className="space-y-6 py-4">
                    {/* Patient Info */}
                    <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
                      <div>
                        <p className="text-sm text-gray-500">Patient</p>
                        <p className="font-semibold">{selectedResult.patientName}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Patient ID</p>
                        <p className="font-semibold">{selectedResult.patientId}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Date Ordered</p>
                        <p className="font-semibold">{new Date(selectedResult.dateOrdered).toLocaleDateString()}</p>
                      </div>
                      {selectedResult.dateCompleted && (
                        <div>
                          <p className="text-sm text-gray-500">Date Completed</p>
                          <p className="font-semibold">{new Date(selectedResult.dateCompleted).toLocaleDateString()}</p>
                        </div>
                      )}
                    </div>

                    {/* Test Results */}
                    {selectedResult.results && (
                      <div>
                        <h3 className="font-semibold mb-4">Test Results</h3>
                        <div className="border rounded-lg overflow-hidden">
                          <table className="w-full">
                            <thead className="bg-gray-50">
                              <tr>
                                <th className="px-4 py-3 text-left text-sm font-semibold">Parameter</th>
                                <th className="px-4 py-3 text-left text-sm font-semibold">Value</th>
                                <th className="px-4 py-3 text-left text-sm font-semibold">Normal Range</th>
                                <th className="px-4 py-3 text-left text-sm font-semibold">Status</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y">
                              {selectedResult.results.map((result, idx) => (
                                <tr key={idx} className={result.status !== 'normal' ? 'bg-red-50' : ''}>
                                  <td className="px-4 py-3 font-medium">{result.parameter}</td>
                                  <td className="px-4 py-3">
                                    {result.value} {result.unit}
                                  </td>
                                  <td className="px-4 py-3 text-gray-600">{result.normalRange}</td>
                                  <td className="px-4 py-3">
                                    <div className="flex items-center space-x-2">
                                      {getResultStatusIcon(result.status)}
                                      <span className="capitalize text-sm">{result.status}</span>
                                    </div>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )}

                    {/* Notes */}
                    {selectedResult.notes && (
                      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                        <h3 className="font-semibold mb-2 text-blue-900">Clinical Notes</h3>
                        <p className="text-blue-800">{selectedResult.notes}</p>
                      </div>
                    )}

                    <div className="flex justify-end space-x-2">
                      <Button variant="outline" onClick={() => setIsDetailsOpen(false)}>
                        Close
                      </Button>
                      <Button onClick={() => handleDownloadPDF(selectedResult)} className="bg-blue-600 hover:bg-blue-700">
                        <Download className="h-4 w-4 mr-2" />
                        Download PDF
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
