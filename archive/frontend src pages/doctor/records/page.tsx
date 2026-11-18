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
  FileText,
  Download,
  Eye,
  Search,
  Calendar,
  User,
  Activity,
  Heart,
  Thermometer,
  Weight,
  Ruler,
} from 'lucide-react';
import { toast } from 'sonner';
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';

interface MedicalRecord {
  id: string;
  patientName: string;
  patientId: string;
  recordType: 'visit' | 'diagnosis' | 'procedure' | 'vital_signs' | 'document';
  date: string;
  title: string;
  diagnosis?: string;
  chiefComplaint?: string;
  notes?: string;
  vitalSigns?: {
    bloodPressure?: string;
    heartRate?: number;
    temperature?: number;
    weight?: number;
    height?: number;
    bmi?: number;
  };
  medications?: string[];
  documents?: { name: string; type: string }[];
}

export default function MedicalRecordsPage() {
  const [records, setRecords] = useState<MedicalRecord[]>([]);
  const [filteredRecords, setFilteredRecords] = useState<MedicalRecord[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [selectedRecord, setSelectedRecord] = useState<MedicalRecord | null>(null);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Mock medical records data
    const mockRecords: MedicalRecord[] = [
      {
        id: '1',
        patientName: 'Emily Davis',
        patientId: 'P1234',
        recordType: 'visit',
        date: '2024-10-18',
        title: 'Annual Physical Examination',
        chiefComplaint: 'Routine checkup',
        diagnosis: 'No acute issues, patient in good health',
        notes: 'Continue current medications. Follow up in 6 months.',
        vitalSigns: {
          bloodPressure: '120/80',
          heartRate: 72,
          temperature: 98.6,
          weight: 140,
          height: 65,
          bmi: 23.3,
        },
        medications: ['Multivitamin', 'Vitamin D 2000 IU'],
      },
      {
        id: '2',
        patientName: 'James Wilson',
        patientId: 'P1235',
        recordType: 'diagnosis',
        date: '2024-10-15',
        title: 'Hyperlipidemia - New Diagnosis',
        diagnosis: 'Hyperlipidemia (High Cholesterol)',
        chiefComplaint: 'Elevated cholesterol on recent lab work',
        notes:
          'Started on Atorvastatin 20mg daily. Recommend lifestyle modifications: low-fat diet, regular exercise. Repeat lipid panel in 3 months.',
        medications: ['Atorvastatin 20mg', 'Aspirin 81mg'],
      },
      {
        id: '3',
        patientName: 'Sarah Miller',
        patientId: 'P1236',
        recordType: 'procedure',
        date: '2024-10-12',
        title: 'Minor Surgical Procedure - Skin Lesion Removal',
        diagnosis: 'Benign skin lesion',
        notes: 'Excision of 0.5cm lesion from left forearm. Sent for pathology. Wound healing well, sutures removed.',
        documents: [
          { name: 'Pathology Report', type: 'PDF' },
          { name: 'Procedure Note', type: 'PDF' },
        ],
      },
      {
        id: '4',
        patientName: 'Michael Brown',
        patientId: 'P1237',
        recordType: 'vital_signs',
        date: '2024-10-10',
        title: 'Vital Signs - Follow-up Visit',
        vitalSigns: {
          bloodPressure: '145/92',
          heartRate: 88,
          temperature: 98.4,
          weight: 210,
          height: 70,
          bmi: 30.1,
        },
        notes: 'Blood pressure elevated. Discussed medication compliance. Patient admits missing doses.',
      },
      {
        id: '5',
        patientName: 'Linda Taylor',
        patientId: 'P1238',
        recordType: 'visit',
        date: '2024-10-08',
        title: 'Cardiology Consultation',
        chiefComplaint: 'Chest pain and shortness of breath',
        diagnosis: 'Atypical chest pain, likely musculoskeletal. EKG normal.',
        notes:
          'Reassured patient. No cardiac concerns at this time. Recommended anti-inflammatory medication for muscle pain.',
        vitalSigns: {
          bloodPressure: '130/85',
          heartRate: 76,
          temperature: 98.7,
        },
        documents: [{ name: 'EKG Report', type: 'PDF' }],
      },
      {
        id: '6',
        patientName: 'Robert Johnson',
        patientId: 'P1239',
        recordType: 'document',
        date: '2024-10-05',
        title: 'Hospital Discharge Summary',
        diagnosis: 'Pneumonia, resolved',
        notes: '3-day hospital admission for community-acquired pneumonia. Treated with IV antibiotics, discharged on oral antibiotics.',
        documents: [
          { name: 'Discharge Summary', type: 'PDF' },
          { name: 'Chest X-Ray', type: 'Image' },
          { name: 'Lab Results', type: 'PDF' },
        ],
        medications: ['Amoxicillin 500mg', 'Azithromycin 250mg'],
      },
      {
        id: '7',
        patientName: 'Mary Smith',
        patientId: 'P1240',
        recordType: 'visit',
        date: '2024-10-03',
        title: 'Diabetes Management Visit',
        chiefComplaint: 'Diabetes follow-up',
        diagnosis: 'Type 2 Diabetes Mellitus - controlled',
        notes: 'HbA1c improved to 6.8% from 7.5%. Good medication compliance. Continue current regimen.',
        vitalSigns: {
          bloodPressure: '125/82',
          heartRate: 70,
          weight: 165,
          bmi: 27.4,
        },
        medications: ['Metformin 500mg twice daily', 'Glipizide 5mg'],
      },
    ];

    setTimeout(() => {
      setRecords(mockRecords);
      setFilteredRecords(mockRecords);
      setIsLoading(false);
    }, 500);
  }, []);

  useEffect(() => {
    let filtered = records;

    if (searchQuery) {
      filtered = filtered.filter(
        (record) =>
          record.patientName.toLowerCase().includes(searchQuery.toLowerCase()) ||
          record.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          record.patientId.toLowerCase().includes(searchQuery.toLowerCase()) ||
          record.diagnosis?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (typeFilter !== 'all') {
      filtered = filtered.filter((record) => record.recordType === typeFilter);
    }

    setFilteredRecords(filtered);
  }, [searchQuery, typeFilter, records]);

  const getTypeBadge = (type: string) => {
    const styles = {
      visit: 'bg-blue-100 text-blue-800',
      diagnosis: 'bg-purple-100 text-purple-800',
      procedure: 'bg-green-100 text-green-800',
      vital_signs: 'bg-orange-100 text-orange-800',
      document: 'bg-gray-100 text-gray-800',
    };
    const labels = {
      visit: 'Visit',
      diagnosis: 'Diagnosis',
      procedure: 'Procedure',
      vital_signs: 'Vital Signs',
      document: 'Document',
    };
    return (
      <Badge className={styles[type as keyof typeof styles] || 'bg-gray-100 text-gray-800'}>
        {labels[type as keyof typeof labels] || type}
      </Badge>
    );
  };

  const handleViewDetails = (record: MedicalRecord) => {
    setSelectedRecord(record);
    setIsDetailsOpen(true);
  };

  const handleDownload = (record: MedicalRecord) => {
    toast.success('Downloading medical record', {
      description: `${record.title} for ${record.patientName}`,
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
              <h1 className="text-3xl font-bold text-gray-900">Medical Records</h1>
              <p className="text-gray-500 mt-1">Access and manage patient medical records</p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>Total Records</CardDescription>
                  <CardTitle className="text-3xl">{records.length}</CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>Recent Visits</CardDescription>
                  <CardTitle className="text-3xl text-blue-600">
                    {records.filter((r) => r.recordType === 'visit').length}
                  </CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>Documents</CardDescription>
                  <CardTitle className="text-3xl text-gray-600">
                    {records.filter((r) => r.documents && r.documents.length > 0).length}
                  </CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>This Week</CardDescription>
                  <CardTitle className="text-3xl">
                    {
                      records.filter((r) => {
                        const weekAgo = new Date();
                        weekAgo.setDate(weekAgo.getDate() - 7);
                        return new Date(r.date) >= weekAgo;
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
                      placeholder="Search by patient name, record type, or diagnosis..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  <Select value={typeFilter} onValueChange={setTypeFilter}>
                    <SelectTrigger className="w-[200px]">
                      <SelectValue placeholder="Filter by type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Types</SelectItem>
                      <SelectItem value="visit">Visits</SelectItem>
                      <SelectItem value="diagnosis">Diagnoses</SelectItem>
                      <SelectItem value="procedure">Procedures</SelectItem>
                      <SelectItem value="vital_signs">Vital Signs</SelectItem>
                      <SelectItem value="document">Documents</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardHeader>
            </Card>

            {/* Records Tabs */}
            <Tabs defaultValue="all" className="space-y-6">
              <TabsList>
                <TabsTrigger value="all">All Records ({filteredRecords.length})</TabsTrigger>
                <TabsTrigger value="visits">
                  Visits ({filteredRecords.filter((r) => r.recordType === 'visit').length})
                </TabsTrigger>
                <TabsTrigger value="documents">
                  Documents ({filteredRecords.filter((r) => r.documents && r.documents.length > 0).length})
                </TabsTrigger>
              </TabsList>

              <TabsContent value="all" className="space-y-4">
                {filteredRecords.length === 0 ? (
                  <Card>
                    <CardContent className="py-12 text-center text-gray-500">No medical records found</CardContent>
                  </Card>
                ) : (
                  filteredRecords.map((record) => (
                    <Card key={record.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="pt-6">
                        <div className="flex items-start justify-between">
                          <div className="flex items-start space-x-4 flex-1">
                            <Avatar className="h-12 w-12">
                              <AvatarFallback>
                                {record.patientName
                                  .split(' ')
                                  .map((n) => n[0])
                                  .join('')}
                              </AvatarFallback>
                            </Avatar>
                            <div className="flex-1">
                              <div className="flex items-center space-x-3 mb-2">
                                <h3 className="font-semibold text-lg">{record.patientName}</h3>
                                {getTypeBadge(record.recordType)}
                              </div>
                              <p className="text-gray-900 font-medium mb-2">{record.title}</p>
                              {record.diagnosis && (
                                <p className="text-sm text-gray-700 mb-2">
                                  <span className="font-medium">Diagnosis:</span> {record.diagnosis}
                                </p>
                              )}
                              {record.chiefComplaint && (
                                <p className="text-sm text-gray-600 mb-2">
                                  <span className="font-medium">Chief Complaint:</span> {record.chiefComplaint}
                                </p>
                              )}
                              <div className="flex items-center space-x-4 text-sm text-gray-500">
                                <span className="flex items-center">
                                  <Calendar className="h-3 w-3 mr-1" />
                                  {new Date(record.date).toLocaleDateString()}
                                </span>
                                <span className="flex items-center">
                                  <User className="h-3 w-3 mr-1" />
                                  {record.patientId}
                                </span>
                                {record.documents && record.documents.length > 0 && (
                                  <span className="flex items-center">
                                    <FileText className="h-3 w-3 mr-1" />
                                    {record.documents.length} document{record.documents.length > 1 ? 's' : ''}
                                  </span>
                                )}
                              </div>
                              {record.vitalSigns && (
                                <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                                  <div className="grid grid-cols-3 gap-3 text-sm">
                                    {record.vitalSigns.bloodPressure && (
                                      <div className="flex items-center space-x-2">
                                        <Heart className="h-4 w-4 text-red-600" />
                                        <span className="text-gray-700">BP: {record.vitalSigns.bloodPressure}</span>
                                      </div>
                                    )}
                                    {record.vitalSigns.heartRate && (
                                      <div className="flex items-center space-x-2">
                                        <Activity className="h-4 w-4 text-green-600" />
                                        <span className="text-gray-700">HR: {record.vitalSigns.heartRate} bpm</span>
                                      </div>
                                    )}
                                    {record.vitalSigns.temperature && (
                                      <div className="flex items-center space-x-2">
                                        <Thermometer className="h-4 w-4 text-orange-600" />
                                        <span className="text-gray-700">Temp: {record.vitalSigns.temperature}°F</span>
                                      </div>
                                    )}
                                    {record.vitalSigns.weight && (
                                      <div className="flex items-center space-x-2">
                                        <Weight className="h-4 w-4 text-purple-600" />
                                        <span className="text-gray-700">Weight: {record.vitalSigns.weight} lbs</span>
                                      </div>
                                    )}
                                    {record.vitalSigns.height && (
                                      <div className="flex items-center space-x-2">
                                        <Ruler className="h-4 w-4 text-blue-600" />
                                        <span className="text-gray-700">Height: {record.vitalSigns.height} in</span>
                                      </div>
                                    )}
                                    {record.vitalSigns.bmi && (
                                      <div className="flex items-center space-x-2">
                                        <Activity className="h-4 w-4 text-indigo-600" />
                                        <span className="text-gray-700">BMI: {record.vitalSigns.bmi}</span>
                                      </div>
                                    )}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                          <div className="flex space-x-2">
                            <Button variant="outline" size="sm" onClick={() => handleViewDetails(record)}>
                              <Eye className="h-4 w-4 mr-2" />
                              View
                            </Button>
                            <Button variant="outline" size="sm" onClick={() => handleDownload(record)}>
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

              <TabsContent value="visits" className="space-y-4">
                {filteredRecords
                  .filter((r) => r.recordType === 'visit')
                  .map((record) => (
                    <Card key={record.id}>
                      <CardContent className="pt-6">
                        <div className="flex items-start justify-between">
                          <div>
                            <h3 className="font-semibold text-lg mb-1">{record.patientName}</h3>
                            <p className="text-gray-700 mb-2">{record.title}</p>
                            {record.chiefComplaint && (
                              <p className="text-sm text-gray-600 mb-1">
                                <span className="font-medium">Complaint:</span> {record.chiefComplaint}
                              </p>
                            )}
                            <p className="text-sm text-gray-500">
                              {new Date(record.date).toLocaleDateString()}
                            </p>
                          </div>
                          <Button variant="outline" size="sm" onClick={() => handleViewDetails(record)}>
                            <Eye className="h-4 w-4" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
              </TabsContent>

              <TabsContent value="documents" className="space-y-4">
                {filteredRecords
                  .filter((r) => r.documents && r.documents.length > 0)
                  .map((record) => (
                    <Card key={record.id}>
                      <CardContent className="pt-6">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-2">
                              <FileText className="h-5 w-5 text-gray-600" />
                              <h3 className="font-semibold">{record.title}</h3>
                            </div>
                            <p className="text-sm text-gray-600 mb-2">{record.patientName}</p>
                            {record.documents && (
                              <div className="space-y-1">
                                {record.documents.map((doc, idx) => (
                                  <div key={idx} className="flex items-center space-x-2 text-sm">
                                    <Badge variant="outline">{doc.type}</Badge>
                                    <span className="text-gray-700">{doc.name}</span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                          <Button variant="outline" size="sm" onClick={() => handleDownload(record)}>
                            <Download className="h-4 w-4" />
                          </Button>
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
                  <DialogTitle>Medical Record Details</DialogTitle>
                  <DialogDescription>
                    {selectedRecord?.title} - {selectedRecord?.patientName}
                  </DialogDescription>
                </DialogHeader>
                {selectedRecord && (
                  <div className="space-y-6 py-4">
                    {/* Patient Info */}
                    <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
                      <div>
                        <p className="text-sm text-gray-500">Patient</p>
                        <p className="font-semibold">{selectedRecord.patientName}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Patient ID</p>
                        <p className="font-semibold">{selectedRecord.patientId}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Date</p>
                        <p className="font-semibold">{new Date(selectedRecord.date).toLocaleDateString()}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Record Type</p>
                        {getTypeBadge(selectedRecord.recordType)}
                      </div>
                    </div>

                    {/* Chief Complaint */}
                    {selectedRecord.chiefComplaint && (
                      <div>
                        <h3 className="font-semibold mb-2">Chief Complaint</h3>
                        <p className="text-gray-700">{selectedRecord.chiefComplaint}</p>
                      </div>
                    )}

                    {/* Diagnosis */}
                    {selectedRecord.diagnosis && (
                      <div>
                        <h3 className="font-semibold mb-2">Diagnosis</h3>
                        <p className="text-gray-700">{selectedRecord.diagnosis}</p>
                      </div>
                    )}

                    {/* Vital Signs */}
                    {selectedRecord.vitalSigns && (
                      <div>
                        <h3 className="font-semibold mb-3">Vital Signs</h3>
                        <div className="grid grid-cols-2 gap-4">
                          {selectedRecord.vitalSigns.bloodPressure && (
                            <div className="p-3 border rounded-lg">
                              <div className="flex items-center space-x-2 mb-1">
                                <Heart className="h-4 w-4 text-red-600" />
                                <span className="text-sm text-gray-500">Blood Pressure</span>
                              </div>
                              <p className="text-lg font-semibold">{selectedRecord.vitalSigns.bloodPressure}</p>
                            </div>
                          )}
                          {selectedRecord.vitalSigns.heartRate && (
                            <div className="p-3 border rounded-lg">
                              <div className="flex items-center space-x-2 mb-1">
                                <Activity className="h-4 w-4 text-green-600" />
                                <span className="text-sm text-gray-500">Heart Rate</span>
                              </div>
                              <p className="text-lg font-semibold">{selectedRecord.vitalSigns.heartRate} bpm</p>
                            </div>
                          )}
                          {selectedRecord.vitalSigns.temperature && (
                            <div className="p-3 border rounded-lg">
                              <div className="flex items-center space-x-2 mb-1">
                                <Thermometer className="h-4 w-4 text-orange-600" />
                                <span className="text-sm text-gray-500">Temperature</span>
                              </div>
                              <p className="text-lg font-semibold">{selectedRecord.vitalSigns.temperature}°F</p>
                            </div>
                          )}
                          {selectedRecord.vitalSigns.weight && (
                            <div className="p-3 border rounded-lg">
                              <div className="flex items-center space-x-2 mb-1">
                                <Weight className="h-4 w-4 text-purple-600" />
                                <span className="text-sm text-gray-500">Weight</span>
                              </div>
                              <p className="text-lg font-semibold">{selectedRecord.vitalSigns.weight} lbs</p>
                            </div>
                          )}
                          {selectedRecord.vitalSigns.height && (
                            <div className="p-3 border rounded-lg">
                              <div className="flex items-center space-x-2 mb-1">
                                <Ruler className="h-4 w-4 text-blue-600" />
                                <span className="text-sm text-gray-500">Height</span>
                              </div>
                              <p className="text-lg font-semibold">{selectedRecord.vitalSigns.height} in</p>
                            </div>
                          )}
                          {selectedRecord.vitalSigns.bmi && (
                            <div className="p-3 border rounded-lg">
                              <div className="flex items-center space-x-2 mb-1">
                                <Activity className="h-4 w-4 text-indigo-600" />
                                <span className="text-sm text-gray-500">BMI</span>
                              </div>
                              <p className="text-lg font-semibold">{selectedRecord.vitalSigns.bmi}</p>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Medications */}
                    {selectedRecord.medications && selectedRecord.medications.length > 0 && (
                      <div>
                        <h3 className="font-semibold mb-3">Medications</h3>
                        <div className="space-y-2">
                          {selectedRecord.medications.map((med, idx) => (
                            <div key={idx} className="flex items-center space-x-2 p-2 bg-blue-50 rounded">
                              <div className="h-2 w-2 bg-blue-600 rounded-full"></div>
                              <span className="text-gray-700">{med}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Documents */}
                    {selectedRecord.documents && selectedRecord.documents.length > 0 && (
                      <div>
                        <h3 className="font-semibold mb-3">Attached Documents</h3>
                        <div className="space-y-2">
                          {selectedRecord.documents.map((doc, idx) => (
                            <div key={idx} className="flex items-center justify-between p-3 border rounded-lg">
                              <div className="flex items-center space-x-3">
                                <FileText className="h-5 w-5 text-gray-600" />
                                <div>
                                  <p className="font-medium">{doc.name}</p>
                                  <p className="text-sm text-gray-500">{doc.type}</p>
                                </div>
                              </div>
                              <Button variant="outline" size="sm" onClick={() => handleDownload(selectedRecord)}>
                                <Download className="h-4 w-4" />
                              </Button>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Clinical Notes */}
                    {selectedRecord.notes && (
                      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                        <h3 className="font-semibold mb-2 text-yellow-900">Clinical Notes</h3>
                        <p className="text-yellow-800">{selectedRecord.notes}</p>
                      </div>
                    )}

                    <div className="flex justify-end space-x-2">
                      <Button variant="outline" onClick={() => setIsDetailsOpen(false)}>
                        Close
                      </Button>
                      <Button onClick={() => handleDownload(selectedRecord)} className="bg-blue-600 hover:bg-blue-700">
                        <Download className="h-4 w-4 mr-2" />
                        Download Record
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
