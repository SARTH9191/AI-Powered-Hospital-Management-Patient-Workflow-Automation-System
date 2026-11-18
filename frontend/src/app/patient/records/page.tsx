'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/hooks/useAuth';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
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
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';
import {
  FileText,
  Upload,
  Download,
  Search,
  Calendar,
  Activity,
  Heart,
  Stethoscope,
  Pill,
  ClipboardList,
  Image as ImageIcon,
  File,
  Eye,
  Trash2,
  Plus,
  Loader2,
  CheckCircle,
  Clock,
  AlertCircle,
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

interface MedicalRecord {
  record_id: string;
  patient_id: string;
  record_type: string;
  title: string;
  description?: string;
  record_date: string;
  provider_name?: string;
  department?: string;
  diagnosis?: string;
  treatment?: string;
  notes?: string;
  attachments?: Attachment[];
  created_at: string;
  updated_at?: string;
}

interface Attachment {
  file_id: string;
  file_name: string;
  file_type: string;
  file_size: number;
  uploaded_at: string;
  url?: string;
}

export default function PatientRecords() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const patientId = 'patient001'; // TODO: Get from authenticated user

  // Fetch medical records
  const { data: recordsData, isLoading } = useQuery({
    queryKey: ['medical-records', patientId],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `http://localhost:8000/api/records/patient/${patientId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data?.data?.records || [];
    },
    enabled: !!patientId,
  });

  const records = recordsData || [];

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRecord, setSelectedRecord] = useState<MedicalRecord | null>(null);
  const [showDetailsDialog, setShowDetailsDialog] = useState(false);
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [uploadForm, setUploadForm] = useState({
    record_type: 'consultation',
    title: '',
    description: '',
    record_date: new Date().toISOString().split('T')[0],
    provider_name: '',
    notes: '',
  });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Upload record mutation
  const uploadMutation = useMutation({
    mutationFn: async (formData: FormData) => {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        'http://localhost:8000/api/records/upload',
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['medical-records'] });
      toast.success('Record uploaded successfully!');
      setShowUploadDialog(false);
      resetUploadForm();
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to upload record');
    },
  });

  // Delete record mutation
  const deleteMutation = useMutation({
    mutationFn: async (recordId: string) => {
      const token = localStorage.getItem('token');
      const response = await axios.delete(
        `http://localhost:8000/api/records/${recordId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['medical-records'] });
      toast.success('Record deleted successfully!');
      setShowDetailsDialog(false);
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to delete record');
    },
  });

  // Filter records
  const filteredRecords = records.filter((record: MedicalRecord) =>
    record.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    record.record_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
    record.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Categorize by type
  const consultationRecords = filteredRecords.filter((r: MedicalRecord) => r.record_type === 'consultation');
  const labRecords = filteredRecords.filter((r: MedicalRecord) => r.record_type === 'lab_result');
  const imagingRecords = filteredRecords.filter((r: MedicalRecord) => r.record_type === 'imaging');
  const prescriptionRecords = filteredRecords.filter((r: MedicalRecord) => r.record_type === 'prescription');
  const otherRecords = filteredRecords.filter((r: MedicalRecord) => 
    !['consultation', 'lab_result', 'imaging', 'prescription'].includes(r.record_type)
  );

  // Helper functions
  const getRecordIcon = (type: string) => {
    switch (type) {
      case 'consultation':
        return <Stethoscope className="h-5 w-5" />;
      case 'lab_result':
        return <Activity className="h-5 w-5" />;
      case 'imaging':
        return <ImageIcon className="h-5 w-5" />;
      case 'prescription':
        return <Pill className="h-5 w-5" />;
      case 'diagnosis':
        return <Heart className="h-5 w-5" />;
      default:
        return <FileText className="h-5 w-5" />;
    }
  };

  const getRecordColor = (type: string) => {
    switch (type) {
      case 'consultation':
        return 'bg-blue-100 text-blue-700';
      case 'lab_result':
        return 'bg-green-100 text-green-700';
      case 'imaging':
        return 'bg-purple-100 text-purple-700';
      case 'prescription':
        return 'bg-orange-100 text-orange-700';
      case 'diagnosis':
        return 'bg-red-100 text-red-700';
      default:
        return 'bg-gray-100 text-gray-700';
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

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const resetUploadForm = () => {
    setUploadForm({
      record_type: 'consultation',
      title: '',
      description: '',
      record_date: new Date().toISOString().split('T')[0],
      provider_name: '',
      notes: '',
    });
    setSelectedFile(null);
  };

  const handleViewDetails = (record: MedicalRecord) => {
    setSelectedRecord(record);
    setShowDetailsDialog(true);
  };

  const handleUploadRecord = () => {
    if (!uploadForm.title.trim()) {
      toast.error('Please enter a title');
      return;
    }

    const formData = new FormData();
    formData.append('patient_id', patientId);
    formData.append('record_type', uploadForm.record_type);
    formData.append('title', uploadForm.title);
    formData.append('description', uploadForm.description);
    formData.append('record_date', uploadForm.record_date);
    formData.append('provider_name', uploadForm.provider_name);
    formData.append('notes', uploadForm.notes);

    if (selectedFile) {
      formData.append('file', selectedFile);
    }

    uploadMutation.mutate(formData);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleDownloadAttachment = (attachment: Attachment) => {
    toast.info('File download feature coming soon!');
    // TODO: Implement file download
  };

  const handleDeleteRecord = (record: MedicalRecord) => {
    if (confirm('Are you sure you want to delete this record?')) {
      deleteMutation.mutate(record.record_id);
    }
  };

  // Sort records by date (newest first)
  const sortedRecords = [...filteredRecords].sort((a, b) => 
    new Date(b.record_date).getTime() - new Date(a.record_date).getTime()
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
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900 mb-2">Medical Records</h1>
                  <p className="text-gray-600">View and manage your medical history</p>
                </div>
                <Button onClick={() => setShowUploadDialog(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Upload Record
                </Button>
              </div>
            </div>

            {/* Statistics */}
            {isLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                {[1, 2, 3, 4].map((i) => (
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
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-gray-600">
                      Total Records
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <p className="text-3xl font-bold text-gray-900">{records.length}</p>
                      <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
                        <FileText className="h-6 w-6 text-blue-600" />
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-gray-600">
                      Consultations
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <p className="text-3xl font-bold text-gray-900">{consultationRecords.length}</p>
                      <div className="h-12 w-12 bg-purple-100 rounded-full flex items-center justify-center">
                        <Stethoscope className="h-6 w-6 text-purple-600" />
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-gray-600">
                      Lab Results
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <p className="text-3xl font-bold text-gray-900">{labRecords.length}</p>
                      <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center">
                        <Activity className="h-6 w-6 text-green-600" />
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-gray-600">
                      Imaging Reports
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <p className="text-3xl font-bold text-gray-900">{imagingRecords.length}</p>
                      <div className="h-12 w-12 bg-orange-100 rounded-full flex items-center justify-center">
                        <ImageIcon className="h-6 w-6 text-orange-600" />
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
                  placeholder="Search records by title, type, or description..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Tabs */}
            <Tabs defaultValue="all" className="space-y-6">
              <TabsList>
                <TabsTrigger value="all">All Records ({filteredRecords.length})</TabsTrigger>
                <TabsTrigger value="consultations">Consultations ({consultationRecords.length})</TabsTrigger>
                <TabsTrigger value="labs">Labs ({labRecords.length})</TabsTrigger>
                <TabsTrigger value="imaging">Imaging ({imagingRecords.length})</TabsTrigger>
              </TabsList>

              {/* All Records - Timeline View */}
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
                ) : sortedRecords.length === 0 ? (
                  <Card>
                    <CardContent className="p-12 text-center">
                      <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600 mb-4">No medical records found</p>
                      <Button onClick={() => setShowUploadDialog(true)}>
                        <Plus className="h-4 w-4 mr-2" />
                        Upload First Record
                      </Button>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="relative">
                    {/* Timeline line */}
                    <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-300"></div>

                    <div className="space-y-6">
                      {sortedRecords.map((record: MedicalRecord, index: number) => (
                        <div key={record.record_id} className="relative pl-16">
                          {/* Timeline dot */}
                          <div className={`absolute left-6 top-6 h-5 w-5 rounded-full border-4 border-white ${getRecordColor(record.record_type)}`}></div>

                          <Card className="hover:shadow-lg transition-shadow">
                            <CardContent className="p-6">
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <div className="flex items-center space-x-3 mb-3">
                                    <div className={`p-2 rounded-lg ${getRecordColor(record.record_type)}`}>
                                      {getRecordIcon(record.record_type)}
                                    </div>
                                    <div>
                                      <h3 className="text-lg font-semibold text-gray-900">
                                        {record.title}
                                      </h3>
                                      <div className="flex items-center space-x-2 text-sm text-gray-600">
                                        <Calendar className="h-4 w-4" />
                                        <span>{formatDate(record.record_date)}</span>
                                        {record.provider_name && (
                                          <>
                                            <span>•</span>
                                            <span>{record.provider_name}</span>
                                          </>
                                        )}
                                      </div>
                                    </div>
                                  </div>

                                  {record.description && (
                                    <p className="text-sm text-gray-700 mb-3">
                                      {record.description}
                                    </p>
                                  )}

                                  {record.diagnosis && (
                                    <div className="mb-2">
                                      <span className="text-xs font-semibold text-gray-600">Diagnosis: </span>
                                      <span className="text-sm text-gray-900">{record.diagnosis}</span>
                                    </div>
                                  )}

                                  {record.treatment && (
                                    <div className="mb-2">
                                      <span className="text-xs font-semibold text-gray-600">Treatment: </span>
                                      <span className="text-sm text-gray-900">{record.treatment}</span>
                                    </div>
                                  )}

                                  {record.attachments && record.attachments.length > 0 && (
                                    <div className="mt-3 flex items-center space-x-2">
                                      <File className="h-4 w-4 text-gray-500" />
                                      <span className="text-sm text-gray-600">
                                        {record.attachments.length} attachment(s)
                                      </span>
                                    </div>
                                  )}
                                </div>

                                <div className="flex flex-col space-y-2 ml-4">
                                  <Button
                                    size="sm"
                                    onClick={() => handleViewDetails(record)}
                                  >
                                    <Eye className="h-4 w-4 mr-2" />
                                    View
                                  </Button>
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => handleDownloadAttachment(record.attachments?.[0] as Attachment)}
                                    disabled={!record.attachments || record.attachments.length === 0}
                                  >
                                    <Download className="h-4 w-4 mr-2" />
                                    Download
                                  </Button>
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </TabsContent>

              {/* Consultations */}
              <TabsContent value="consultations">
                {consultationRecords.length === 0 ? (
                  <Card>
                    <CardContent className="p-12 text-center">
                      <Stethoscope className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">No consultation records found</p>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="space-y-4">
                    {consultationRecords.map((record: MedicalRecord) => (
                      <Card key={record.record_id}>
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                                {record.title}
                              </h3>
                              <p className="text-sm text-gray-600 mb-2">
                                {formatDate(record.record_date)} • {record.provider_name}
                              </p>
                              {record.description && (
                                <p className="text-sm text-gray-700">{record.description}</p>
                              )}
                            </div>
                            <Button size="sm" onClick={() => handleViewDetails(record)}>
                              View Details
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </TabsContent>

              {/* Labs */}
              <TabsContent value="labs">
                {labRecords.length === 0 ? (
                  <Card>
                    <CardContent className="p-12 text-center">
                      <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">No lab result records found</p>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="space-y-4">
                    {labRecords.map((record: MedicalRecord) => (
                      <Card key={record.record_id}>
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                                {record.title}
                              </h3>
                              <p className="text-sm text-gray-600">
                                {formatDate(record.record_date)}
                              </p>
                            </div>
                            <Button size="sm" onClick={() => handleViewDetails(record)}>
                              View Details
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </TabsContent>

              {/* Imaging */}
              <TabsContent value="imaging">
                {imagingRecords.length === 0 ? (
                  <Card>
                    <CardContent className="p-12 text-center">
                      <ImageIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">No imaging records found</p>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="space-y-4">
                    {imagingRecords.map((record: MedicalRecord) => (
                      <Card key={record.record_id}>
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                                {record.title}
                              </h3>
                              <p className="text-sm text-gray-600">
                                {formatDate(record.record_date)}
                              </p>
                            </div>
                            <Button size="sm" onClick={() => handleViewDetails(record)}>
                              View Details
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

      {/* Record Details Dialog */}
      <Dialog open={showDetailsDialog} onOpenChange={setShowDetailsDialog}>
        <DialogContent className="sm:max-w-[700px]">
          <DialogHeader>
            <DialogTitle>{selectedRecord?.title}</DialogTitle>
            <DialogDescription>
              {selectedRecord?.record_type.replace('_', ' ')} • {selectedRecord && formatDate(selectedRecord.record_date)}
            </DialogDescription>
          </DialogHeader>
          {selectedRecord && (
            <div className="py-4 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-gray-600">Record Type</p>
                  <p className="text-sm text-gray-900 capitalize">{selectedRecord.record_type.replace('_', ' ')}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600">Date</p>
                  <p className="text-sm text-gray-900">{formatDate(selectedRecord.record_date)}</p>
                </div>
                {selectedRecord.provider_name && (
                  <div>
                    <p className="text-sm font-medium text-gray-600">Provider</p>
                    <p className="text-sm text-gray-900">{selectedRecord.provider_name}</p>
                  </div>
                )}
                {selectedRecord.department && (
                  <div>
                    <p className="text-sm font-medium text-gray-600">Department</p>
                    <p className="text-sm text-gray-900">{selectedRecord.department}</p>
                  </div>
                )}
              </div>

              {selectedRecord.description && (
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Description</p>
                  <p className="text-sm text-gray-700">{selectedRecord.description}</p>
                </div>
              )}

              {selectedRecord.diagnosis && (
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Diagnosis</p>
                  <p className="text-sm text-gray-900">{selectedRecord.diagnosis}</p>
                </div>
              )}

              {selectedRecord.treatment && (
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Treatment</p>
                  <p className="text-sm text-gray-900">{selectedRecord.treatment}</p>
                </div>
              )}

              {selectedRecord.notes && (
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Notes</p>
                  <p className="text-sm text-gray-700">{selectedRecord.notes}</p>
                </div>
              )}

              {selectedRecord.attachments && selectedRecord.attachments.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-2">Attachments</p>
                  <div className="space-y-2">
                    {selectedRecord.attachments.map((attachment) => (
                      <div key={attachment.file_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <File className="h-5 w-5 text-gray-500" />
                          <div>
                            <p className="text-sm font-medium text-gray-900">{attachment.file_name}</p>
                            <p className="text-xs text-gray-600">
                              {formatFileSize(attachment.file_size)} • {formatDate(attachment.uploaded_at)}
                            </p>
                          </div>
                        </div>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDownloadAttachment(attachment)}
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDetailsDialog(false)}>
              Close
            </Button>
            {selectedRecord && (
              <Button
                variant="destructive"
                onClick={() => handleDeleteRecord(selectedRecord)}
                disabled={deleteMutation.isPending}
              >
                {deleteMutation.isPending ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Trash2 className="h-4 w-4 mr-2" />
                )}
                Delete
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Upload Record Dialog */}
      <Dialog open={showUploadDialog} onOpenChange={setShowUploadDialog}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>Upload Medical Record</DialogTitle>
            <DialogDescription>
              Add a new record to your medical history
            </DialogDescription>
          </DialogHeader>
          <div className="py-4 space-y-4">
            <div>
              <Label htmlFor="record-type">Record Type</Label>
              <Select
                value={uploadForm.record_type}
                onValueChange={(value) => setUploadForm({ ...uploadForm, record_type: value })}
              >
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="consultation">Consultation</SelectItem>
                  <SelectItem value="lab_result">Lab Result</SelectItem>
                  <SelectItem value="imaging">Imaging/Radiology</SelectItem>
                  <SelectItem value="prescription">Prescription</SelectItem>
                  <SelectItem value="diagnosis">Diagnosis</SelectItem>
                  <SelectItem value="procedure">Procedure</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="title">Title *</Label>
              <Input
                id="title"
                value={uploadForm.title}
                onChange={(e) => setUploadForm({ ...uploadForm, title: e.target.value })}
                placeholder="e.g., Annual Physical Exam"
                className="mt-1"
              />
            </div>

            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={uploadForm.description}
                onChange={(e) => setUploadForm({ ...uploadForm, description: e.target.value })}
                placeholder="Brief description of the record"
                className="mt-1"
                rows={3}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="record-date">Record Date</Label>
                <Input
                  id="record-date"
                  type="date"
                  value={uploadForm.record_date}
                  onChange={(e) => setUploadForm({ ...uploadForm, record_date: e.target.value })}
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="provider">Provider Name</Label>
                <Input
                  id="provider"
                  value={uploadForm.provider_name}
                  onChange={(e) => setUploadForm({ ...uploadForm, provider_name: e.target.value })}
                  placeholder="Doctor's name"
                  className="mt-1"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="notes">Notes</Label>
              <Textarea
                id="notes"
                value={uploadForm.notes}
                onChange={(e) => setUploadForm({ ...uploadForm, notes: e.target.value })}
                placeholder="Additional notes"
                className="mt-1"
                rows={2}
              />
            </div>

            <div>
              <Label htmlFor="file">Attach File (Optional)</Label>
              <Input
                id="file"
                type="file"
                onChange={handleFileSelect}
                className="mt-1"
                accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
              />
              {selectedFile && (
                <p className="text-sm text-gray-600 mt-1">
                  Selected: {selectedFile.name} ({formatFileSize(selectedFile.size)})
                </p>
              )}
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setShowUploadDialog(false);
                resetUploadForm();
              }}
              disabled={uploadMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              onClick={handleUploadRecord}
              disabled={uploadMutation.isPending}
            >
              {uploadMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" />
                  Upload Record
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
