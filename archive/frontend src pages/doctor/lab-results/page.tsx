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
  FlaskConical,
  Search,
  Eye,
  FileText,
  Calendar,
  User,
  AlertTriangle,
  CheckCircle,
  Clock,
  TrendingUp,
  TrendingDown,
  Minus,
} from 'lucide-react';
import axios from 'axios';

interface LabTest {
  test_id: string;
  patient_id: string;
  patient_name: string;
  test_name: string;
  test_category: string;
  order_date: string;
  result_date?: string;
  status: string;
  results?: string;
  notes?: string;
  normal_range?: string;
  value?: string;
  unit?: string;
  doctor_review?: string;
  reviewed_by?: string;
  reviewed_date?: string;
}

export default function DoctorLabResults() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const doctorId = 'doctor001'; // TODO: Get from authenticated user

  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [selectedTest, setSelectedTest] = useState<LabTest | null>(null);
  const [reviewDialogOpen, setReviewDialogOpen] = useState(false);
  const [reviewNotes, setReviewNotes] = useState('');

  // Fetch lab results
  const { data: labsData, isLoading } = useQuery({
    queryKey: ['doctor-lab-results', doctorId],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `http://localhost:8000/api/doctors/${doctorId}/lab-results`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data?.data?.lab_tests || [];
    },
    enabled: !!doctorId,
  });

  // Review lab test mutation
  const reviewMutation = useMutation({
    mutationFn: async ({ testId, notes }: { testId: string; notes: string }) => {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `http://localhost:8000/api/lab-tests/${testId}/review`,
        {
          doctor_review: notes,
          reviewed_by: doctorId,
          reviewed_date: new Date().toISOString().split('T')[0],
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
      queryClient.invalidateQueries({ queryKey: ['doctor-lab-results'] });
      setReviewDialogOpen(false);
      setReviewNotes('');
    },
  });

  const labTests: LabTest[] = labsData || [];

  // Filter lab tests
  const filteredTests = labTests.filter((test) => {
    if (statusFilter !== 'all' && test.status !== statusFilter) return false;
    if (categoryFilter !== 'all' && test.test_category !== categoryFilter) return false;
    if (
      searchQuery &&
      !test.patient_name.toLowerCase().includes(searchQuery.toLowerCase()) &&
      !test.test_name.toLowerCase().includes(searchQuery.toLowerCase())
    ) {
      return false;
    }
    return true;
  });

  const handleReview = (test: LabTest) => {
    setSelectedTest(test);
    setReviewNotes(test.doctor_review || '');
    setReviewDialogOpen(true);
  };

  const submitReview = () => {
    if (selectedTest) {
      reviewMutation.mutate({
        testId: selectedTest.test_id,
        notes: reviewNotes,
      });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'default';
      case 'pending':
        return 'secondary';
      case 'in_progress':
        return 'outline';
      case 'cancelled':
        return 'destructive';
      default:
        return 'outline';
    }
  };

  const isAbnormal = (test: LabTest) => {
    // Simple check - in real app, would compare value against normal_range
    return test.results && test.results.toLowerCase().includes('abnormal');
  };

  const getResultIndicator = (test: LabTest) => {
    if (!test.value || !test.normal_range) return null;
    
    const value = parseFloat(test.value);
    const [min, max] = test.normal_range.split('-').map(parseFloat);
    
    if (value < min) return <TrendingDown className="h-4 w-4 text-blue-600" />;
    if (value > max) return <TrendingUp className="h-4 w-4 text-red-600" />;
    return <Minus className="h-4 w-4 text-green-600" />;
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
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Lab Results</h1>
              <p className="text-gray-600">Review and interpret patient laboratory test results</p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Total Tests
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-gray-900">{labTests.length}</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Pending Review
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-orange-600">
                    {labTests.filter((t) => t.status === 'completed' && !t.doctor_review).length}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Abnormal Results
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-red-600">
                    {labTests.filter((t) => isAbnormal(t)).length}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Reviewed
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-green-600">
                    {labTests.filter((t) => t.doctor_review).length}
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
                      placeholder="Search by patient or test name..."
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
                      <SelectItem value="pending">Pending</SelectItem>
                      <SelectItem value="in_progress">In Progress</SelectItem>
                    </SelectContent>
                  </Select>

                  {/* Category Filter */}
                  <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="Category" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Categories</SelectItem>
                      <SelectItem value="Hematology">Hematology</SelectItem>
                      <SelectItem value="Biochemistry">Biochemistry</SelectItem>
                      <SelectItem value="Microbiology">Microbiology</SelectItem>
                      <SelectItem value="Immunology">Immunology</SelectItem>
                      <SelectItem value="Radiology">Radiology</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Tabs */}
            <Tabs defaultValue="pending" className="space-y-6">
              <TabsList>
                <TabsTrigger value="pending">
                  Pending Review ({labTests.filter((t) => t.status === 'completed' && !t.doctor_review).length})
                </TabsTrigger>
                <TabsTrigger value="all">All Results ({filteredTests.length})</TabsTrigger>
                <TabsTrigger value="abnormal">
                  Abnormal ({labTests.filter((t) => isAbnormal(t)).length})
                </TabsTrigger>
              </TabsList>

              {/* Pending Review Tab */}
              <TabsContent value="pending">
                {isLoading ? (
                  <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                      <Card key={i}>
                        <CardContent className="pt-6">
                          <Skeleton className="h-24 w-full" />
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                ) : (
                  <div className="space-y-4">
                    {filteredTests
                      .filter((t) => t.status === 'completed' && !t.doctor_review)
                      .map((test) => (
                        <Card key={test.test_id} className="hover:shadow-lg transition-shadow">
                          <CardContent className="pt-6">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center space-x-3 mb-3">
                                  <div className="h-10 w-10 bg-orange-100 rounded-full flex items-center justify-center">
                                    <FlaskConical className="h-5 w-5 text-orange-600" />
                                  </div>
                                  <div>
                                    <h3 className="font-semibold text-gray-900">{test.test_name}</h3>
                                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                                      <User className="h-3 w-3" />
                                      <span>{test.patient_name}</span>
                                      <span>•</span>
                                      <Calendar className="h-3 w-3" />
                                      <span>{new Date(test.order_date).toLocaleDateString()}</span>
                                    </div>
                                  </div>
                                  {isAbnormal(test) && (
                                    <Badge variant="destructive">
                                      <AlertTriangle className="h-3 w-3 mr-1" />
                                      Abnormal
                                    </Badge>
                                  )}
                                </div>

                                <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
                                  <div>
                                    <label className="text-xs text-gray-600 uppercase">Category</label>
                                    <p className="font-medium text-gray-900">{test.test_category}</p>
                                  </div>
                                  {test.result_date && (
                                    <div>
                                      <label className="text-xs text-gray-600 uppercase">Result Date</label>
                                      <p className="font-medium text-gray-900">
                                        {new Date(test.result_date).toLocaleDateString()}
                                      </p>
                                    </div>
                                  )}
                                  {test.value && (
                                    <div>
                                      <label className="text-xs text-gray-600 uppercase">Value</label>
                                      <div className="flex items-center space-x-2">
                                        {getResultIndicator(test)}
                                        <p className="font-medium text-gray-900">
                                          {test.value} {test.unit}
                                        </p>
                                      </div>
                                    </div>
                                  )}
                                  {test.normal_range && (
                                    <div>
                                      <label className="text-xs text-gray-600 uppercase">Normal Range</label>
                                      <p className="font-medium text-gray-900">{test.normal_range} {test.unit}</p>
                                    </div>
                                  )}
                                </div>
                              </div>

                              <Button onClick={() => handleReview(test)} className="ml-4">
                                <Eye className="h-4 w-4 mr-2" />
                                Review
                              </Button>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    {filteredTests.filter((t) => t.status === 'completed' && !t.doctor_review).length === 0 && (
                      <Card>
                        <CardContent className="pt-12 pb-12 text-center">
                          <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
                          <p className="text-gray-600 text-lg">All results reviewed!</p>
                        </CardContent>
                      </Card>
                    )}
                  </div>
                )}
              </TabsContent>

              {/* All Results Tab */}
              <TabsContent value="all">
                {isLoading ? (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {[1, 2, 3, 4].map((i) => (
                      <Card key={i}>
                        <CardContent className="pt-6">
                          <Skeleton className="h-32 w-full" />
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                ) : (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {filteredTests.map((test) => (
                      <Card key={test.test_id} className="hover:shadow-lg transition-shadow">
                        <CardContent className="pt-6">
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex items-center space-x-3">
                              <div className="h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
                                <FlaskConical className="h-5 w-5 text-blue-600" />
                              </div>
                              <div>
                                <h3 className="font-semibold text-gray-900">{test.test_name}</h3>
                                <p className="text-sm text-gray-600">{test.patient_name}</p>
                              </div>
                            </div>
                            <div className="flex flex-col items-end space-y-1">
                              <Badge variant={getStatusColor(test.status)}>{test.status}</Badge>
                              {test.doctor_review && (
                                <Badge variant="outline" className="text-xs">
                                  <CheckCircle className="h-3 w-3 mr-1" />
                                  Reviewed
                                </Badge>
                              )}
                            </div>
                          </div>

                          <div className="space-y-2 text-sm">
                            <div className="flex items-center justify-between">
                              <span className="text-gray-600">Category:</span>
                              <span className="font-medium text-gray-900">{test.test_category}</span>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-gray-600">Ordered:</span>
                              <span className="font-medium text-gray-900">
                                {new Date(test.order_date).toLocaleDateString()}
                              </span>
                            </div>
                            {test.result_date && (
                              <div className="flex items-center justify-between">
                                <span className="text-gray-600">Result:</span>
                                <span className="font-medium text-gray-900">
                                  {new Date(test.result_date).toLocaleDateString()}
                                </span>
                              </div>
                            )}
                          </div>

                          {test.status === 'completed' && !test.doctor_review && (
                            <Button
                              onClick={() => handleReview(test)}
                              className="w-full mt-4"
                              size="sm"
                            >
                              <Eye className="h-4 w-4 mr-2" />
                              Review Results
                            </Button>
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </TabsContent>

              {/* Abnormal Tab */}
              <TabsContent value="abnormal">
                <div className="space-y-4">
                  {filteredTests.filter((t) => isAbnormal(t)).map((test) => (
                    <Card
                      key={test.test_id}
                      className="border-red-200 hover:shadow-lg transition-shadow"
                    >
                      <CardContent className="pt-6">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-3 mb-3">
                              <div className="h-10 w-10 bg-red-100 rounded-full flex items-center justify-center">
                                <AlertTriangle className="h-5 w-5 text-red-600" />
                              </div>
                              <div>
                                <h3 className="font-semibold text-gray-900">{test.test_name}</h3>
                                <p className="text-sm text-gray-600">{test.patient_name}</p>
                              </div>
                              <Badge variant="destructive">Abnormal</Badge>
                            </div>

                            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                              <p className="text-sm font-medium text-red-900 mb-2">Results:</p>
                              <p className="text-sm text-red-800">{test.results}</p>
                            </div>

                            {test.doctor_review && (
                              <div className="mt-3 bg-gray-50 rounded-lg p-3">
                                <p className="text-xs text-gray-600 mb-1">Doctor's Review:</p>
                                <p className="text-sm text-gray-900">{test.doctor_review}</p>
                              </div>
                            )}
                          </div>

                          {!test.doctor_review && (
                            <Button onClick={() => handleReview(test)} className="ml-4">
                              <Eye className="h-4 w-4 mr-2" />
                              Review
                            </Button>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                  {filteredTests.filter((t) => isAbnormal(t)).length === 0 && (
                    <Card>
                      <CardContent className="pt-12 pb-12 text-center">
                        <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
                        <p className="text-gray-600 text-lg">No abnormal results found</p>
                      </CardContent>
                    </Card>
                  )}
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </main>
      </div>

      {/* Review Dialog */}
      <Dialog open={reviewDialogOpen} onOpenChange={setReviewDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Review Lab Results</DialogTitle>
            <DialogDescription>Add your interpretation and notes</DialogDescription>
          </DialogHeader>

          {selectedTest && (
            <div className="space-y-6">
              {/* Test Info */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <Label className="text-gray-600">Test Name</Label>
                    <p className="font-medium text-gray-900">{selectedTest.test_name}</p>
                  </div>
                  <div>
                    <Label className="text-gray-600">Category</Label>
                    <p className="font-medium text-gray-900">{selectedTest.test_category}</p>
                  </div>
                  <div>
                    <Label className="text-gray-600">Patient</Label>
                    <p className="font-medium text-gray-900">{selectedTest.patient_name}</p>
                  </div>
                  <div>
                    <Label className="text-gray-600">Result Date</Label>
                    <p className="font-medium text-gray-900">
                      {selectedTest.result_date
                        ? new Date(selectedTest.result_date).toLocaleDateString()
                        : 'Pending'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Results */}
              {selectedTest.results && (
                <div>
                  <Label className="text-gray-600">Test Results</Label>
                  <div className={`mt-2 p-4 rounded-lg ${
                    isAbnormal(selectedTest) ? 'bg-red-50 border border-red-200' : 'bg-gray-50'
                  }`}>
                    <p className="text-gray-900">{selectedTest.results}</p>
                  </div>
                </div>
              )}

              {/* Values */}
              {selectedTest.value && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-gray-600">Value</Label>
                    <div className="flex items-center space-x-2 mt-1">
                      {getResultIndicator(selectedTest)}
                      <p className="font-medium text-gray-900">
                        {selectedTest.value} {selectedTest.unit}
                      </p>
                    </div>
                  </div>
                  {selectedTest.normal_range && (
                    <div>
                      <Label className="text-gray-600">Normal Range</Label>
                      <p className="font-medium text-gray-900 mt-1">
                        {selectedTest.normal_range} {selectedTest.unit}
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Review Notes */}
              <div>
                <Label htmlFor="review_notes">Doctor's Review and Interpretation *</Label>
                <Textarea
                  id="review_notes"
                  value={reviewNotes}
                  onChange={(e) => setReviewNotes(e.target.value)}
                  placeholder="Enter your clinical interpretation, recommendations, and follow-up instructions..."
                  rows={6}
                  className="mt-2"
                />
              </div>

              {selectedTest.doctor_review && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <p className="text-sm text-blue-900">
                    <strong>Previously reviewed by:</strong> {selectedTest.reviewed_by} on{' '}
                    {selectedTest.reviewed_date
                      ? new Date(selectedTest.reviewed_date).toLocaleDateString()
                      : 'N/A'}
                  </p>
                </div>
              )}
            </div>
          )}

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setReviewDialogOpen(false);
                setReviewNotes('');
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={submitReview}
              disabled={reviewMutation.isPending || !reviewNotes}
            >
              <FileText className="h-4 w-4 mr-2" />
              Submit Review
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
