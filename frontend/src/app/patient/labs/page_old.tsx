'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
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
} from 'lucide-react';

interface LabResult {
  id: string;
  testName: string;
  orderDate: string;
  resultDate?: string;
  status: 'pending' | 'completed';
  doctor: string;
  results?: {
    parameter: string;
    value: string;
    unit: string;
    range: string;
    status: 'normal' | 'high' | 'low' | 'critical';
  }[];
}

export default function PatientLabResults() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedResult, setSelectedResult] = useState<LabResult | null>(null);
  const [showDetailsDialog, setShowDetailsDialog] = useState(false);

  const [labResults] = useState<LabResult[]>([
    {
      id: 'LAB001',
      testName: 'Complete Blood Count (CBC)',
      orderDate: '2024-10-10',
      resultDate: '2024-10-12',
      status: 'completed',
      doctor: 'Dr. Sarah Johnson',
      results: [
        { parameter: 'White Blood Cells', value: '7.5', unit: 'K/uL', range: '4.5-11.0', status: 'normal' },
        { parameter: 'Red Blood Cells', value: '4.8', unit: 'M/uL', range: '4.5-5.5', status: 'normal' },
        { parameter: 'Hemoglobin', value: '14.2', unit: 'g/dL', range: '13.5-17.5', status: 'normal' },
        { parameter: 'Platelets', value: '250', unit: 'K/uL', range: '150-400', status: 'normal' },
      ],
    },
    {
      id: 'LAB002',
      testName: 'Lipid Panel',
      orderDate: '2024-10-05',
      resultDate: '2024-10-07',
      status: 'completed',
      doctor: 'Dr. Michael Chen',
      results: [
        { parameter: 'Total Cholesterol', value: '210', unit: 'mg/dL', range: '<200', status: 'high' },
        { parameter: 'LDL Cholesterol', value: '130', unit: 'mg/dL', range: '<100', status: 'high' },
        { parameter: 'HDL Cholesterol', value: '55', unit: 'mg/dL', range: '>40', status: 'normal' },
        { parameter: 'Triglycerides', value: '125', unit: 'mg/dL', range: '<150', status: 'normal' },
      ],
    },
    {
      id: 'LAB003',
      testName: 'Thyroid Function Panel',
      orderDate: '2024-10-15',
      status: 'pending',
      doctor: 'Dr. Emily Rodriguez',
    },
    {
      id: 'LAB004',
      testName: 'Vitamin D Level',
      orderDate: '2024-09-20',
      resultDate: '2024-09-22',
      status: 'completed',
      doctor: 'Dr. Sarah Johnson',
      results: [
        { parameter: 'Vitamin D, 25-OH', value: '28', unit: 'ng/mL', range: '30-100', status: 'low' },
      ],
    },
  ]);

  const handleViewDetails = (result: LabResult) => {
    setSelectedResult(result);
    setShowDetailsDialog(true);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'default';
      case 'pending':
        return 'secondary';
      default:
        return 'outline';
    }
  };

  const getResultStatusIcon = (status: string) => {
    switch (status) {
      case 'normal':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'high':
        return <TrendingUp className="h-4 w-4 text-red-600" />;
      case 'low':
        return <TrendingDown className="h-4 w-4 text-orange-600" />;
      case 'critical':
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      default:
        return <Minus className="h-4 w-4 text-gray-600" />;
    }
  };

  const getResultStatusColor = (status: string) => {
    switch (status) {
      case 'normal':
        return 'text-green-600';
      case 'high':
        return 'text-red-600';
      case 'low':
        return 'text-orange-600';
      case 'critical':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const filteredResults = labResults.filter((result) =>
    `${result.testName} ${result.doctor}`.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const completedTests = filteredResults.filter(r => r.status === 'completed');
  const pendingTests = filteredResults.filter(r => r.status === 'pending');
  const abnormalTests = completedTests.filter(r =>
    r.results?.some(res => res.status !== 'normal')
  );

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
              <p className="text-gray-600">View your laboratory test results</p>
            </div>

            {/* Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Total Tests
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">{labResults.length}</p>
                    <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <TestTube className="h-6 w-6 text-blue-600" />
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

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Pending
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">{pendingTests.length}</p>
                    <div className="h-12 w-12 bg-orange-100 rounded-full flex items-center justify-center">
                      <Clock className="h-6 w-6 text-orange-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Abnormal
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">{abnormalTests.length}</p>
                    <div className="h-12 w-12 bg-red-100 rounded-full flex items-center justify-center">
                      <AlertTriangle className="h-6 w-6 text-red-600" />
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
                    placeholder="Search lab tests..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Tabs */}
            <Tabs defaultValue="all" className="space-y-6">
              <TabsList>
                <TabsTrigger value="all">All ({filteredResults.length})</TabsTrigger>
                <TabsTrigger value="completed">Completed ({completedTests.length})</TabsTrigger>
                <TabsTrigger value="pending">Pending ({pendingTests.length})</TabsTrigger>
                <TabsTrigger value="abnormal">Abnormal ({abnormalTests.length})</TabsTrigger>
              </TabsList>

              <TabsContent value="all">
                <div className="space-y-4">
                  {filteredResults.map((result) => (
                    <Card key={result.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="pt-6">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-3 mb-2">
                              <Badge variant={getStatusColor(result.status)}>
                                {result.status}
                              </Badge>
                              {result.results?.some(r => r.status !== 'normal') && (
                                <Badge variant="destructive" className="text-xs">
                                  Abnormal Values
                                </Badge>
                              )}
                            </div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">
                              {result.testName}
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm text-gray-600">
                              <div className="flex items-center space-x-1">
                                <Calendar className="h-4 w-4" />
                                <span>Ordered: {result.orderDate}</span>
                              </div>
                              {result.resultDate && (
                                <div className="flex items-center space-x-1">
                                  <CheckCircle className="h-4 w-4" />
                                  <span>Completed: {result.resultDate}</span>
                                </div>
                              )}
                              <div>
                                <span>Doctor: {result.doctor}</span>
                              </div>
                            </div>

                            {result.results && result.results.length > 0 && (
                              <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                                <p className="text-sm font-medium text-gray-700 mb-2">
                                  Key Results ({result.results.length} parameters):
                                </p>
                                <div className="space-y-1">
                                  {result.results.slice(0, 3).map((res, index) => (
                                    <div key={index} className="flex items-center justify-between text-sm">
                                      <div className="flex items-center space-x-2">
                                        {getResultStatusIcon(res.status)}
                                        <span>{res.parameter}</span>
                                      </div>
                                      <span className={`font-medium ${getResultStatusColor(res.status)}`}>
                                        {res.value} {res.unit}
                                      </span>
                                    </div>
                                  ))}
                                  {result.results.length > 3 && (
                                    <p className="text-xs text-gray-500 pt-1">
                                      +{result.results.length - 3} more parameters
                                    </p>
                                  )}
                                </div>
                              </div>
                            )}
                          </div>

                          <div className="flex flex-col space-y-2 ml-4">
                            {result.status === 'completed' && (
                              <>
                                <Button
                                  size="sm"
                                  onClick={() => handleViewDetails(result)}
                                >
                                  View Details
                                </Button>
                                <Button size="sm" variant="outline">
                                  <Download className="h-4 w-4 mr-1" />
                                  Download
                                </Button>
                              </>
                            )}
                            {result.status === 'pending' && (
                              <Badge variant="secondary" className="text-center py-2">
                                Processing...
                              </Badge>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="completed">
                <div className="space-y-4">
                  {completedTests.map((result) => (
                    <Card key={result.id}>
                      <CardContent className="pt-6">
                        <h3 className="text-lg font-semibold mb-2">{result.testName}</h3>
                        <p className="text-sm text-gray-600">{result.resultDate} - {result.doctor}</p>
                        <Button size="sm" className="mt-3" onClick={() => handleViewDetails(result)}>
                          View Details
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="pending">
                <div className="space-y-4">
                  {pendingTests.map((result) => (
                    <Card key={result.id}>
                      <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <h3 className="text-lg font-semibold mb-2">{result.testName}</h3>
                            <p className="text-sm text-gray-600">Ordered: {result.orderDate} - {result.doctor}</p>
                          </div>
                          <Badge variant="secondary">
                            <Clock className="h-3 w-3 mr-1" />
                            Processing
                          </Badge>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="abnormal">
                <div className="space-y-4">
                  {abnormalTests.map((result) => (
                    <Card key={result.id} className="border-red-200">
                      <CardContent className="pt-6">
                        <h3 className="text-lg font-semibold mb-2">{result.testName}</h3>
                        <p className="text-sm text-gray-600 mb-3">{result.resultDate} - {result.doctor}</p>
                        {result.results?.filter(r => r.status !== 'normal').map((res, index) => (
                          <div key={index} className="flex items-center justify-between p-2 bg-red-50 rounded mb-2">
                            <div className="flex items-center space-x-2">
                              {getResultStatusIcon(res.status)}
                              <span className="font-medium">{res.parameter}</span>
                            </div>
                            <span className={`font-bold ${getResultStatusColor(res.status)}`}>
                              {res.value} {res.unit}
                            </span>
                          </div>
                        ))}
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
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>{selectedResult?.testName}</DialogTitle>
            <DialogDescription>
              Completed on {selectedResult?.resultDate} by {selectedResult?.doctor}
            </DialogDescription>
          </DialogHeader>
          {selectedResult?.results && (
            <div className="space-y-3">
              <div className="border rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Parameter</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Value</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Unit</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Normal Range</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedResult.results.map((res, index) => (
                      <tr key={index} className="border-t">
                        <td className="px-4 py-3 text-sm">{res.parameter}</td>
                        <td className="px-4 py-3 text-sm font-medium">{res.value}</td>
                        <td className="px-4 py-3 text-sm">{res.unit}</td>
                        <td className="px-4 py-3 text-sm">{res.range}</td>
                        <td className="px-4 py-3">
                          <div className="flex items-center space-x-1">
                            {getResultStatusIcon(res.status)}
                            <span className={`text-sm font-medium ${getResultStatusColor(res.status)}`}>
                              {res.status}
                            </span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <Button className="w-full">
                <Download className="h-4 w-4 mr-2" />
                Download Full Report
              </Button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
