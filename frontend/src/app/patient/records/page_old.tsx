'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import Navbar from '@/components/layout/Sidebar';
import Sidebar from '@/components/layout/Sidebar';
import {
  FileText,
  Download,
  Eye,
  Search,
  Calendar,
  Activity,
  Heart,
  Thermometer,
  Weight,
  Ruler,
  User,
} from 'lucide-react';

interface MedicalRecord {
  id: string;
  type: 'visit' | 'diagnosis' | 'procedure' | 'document';
  title: string;
  date: string;
  doctor: string;
  description: string;
  vitals?: {
    bloodPressure?: string;
    heartRate?: number;
    temperature?: number;
    weight?: number;
    height?: number;
  };
  documents?: string[];
}

export default function PatientRecords() {
  const [searchQuery, setSearchQuery] = useState('');
  const [records] = useState<MedicalRecord[]>([
    {
      id: 'REC001',
      type: 'visit',
      title: 'Annual Physical Examination',
      date: '2024-09-15',
      doctor: 'Dr. Sarah Johnson',
      description: 'Comprehensive health checkup with no significant findings',
      vitals: {
        bloodPressure: '120/80',
        heartRate: 72,
        temperature: 98.6,
        weight: 70,
        height: 170,
      },
      documents: ['Lab Results.pdf', 'Physical Exam Report.pdf'],
    },
    {
      id: 'REC002',
      type: 'diagnosis',
      title: 'Seasonal Allergies',
      date: '2024-08-10',
      doctor: 'Dr. Michael Chen',
      description: 'Diagnosed with seasonal allergic rhinitis',
    },
    {
      id: 'REC003',
      type: 'procedure',
      title: 'Dental Cleaning',
      date: '2024-07-20',
      doctor: 'Dr. Emily Rodriguez',
      description: 'Routine dental cleaning and examination',
      documents: ['Dental X-Ray.pdf'],
    },
    {
      id: 'REC004',
      type: 'visit',
      title: 'Follow-up Consultation',
      date: '2024-06-05',
      doctor: 'Dr. Sarah Johnson',
      description: 'Follow-up visit for blood pressure monitoring',
      vitals: {
        bloodPressure: '118/78',
        heartRate: 70,
      },
    },
  ]);

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'visit':
        return 'bg-blue-100 text-blue-800';
      case 'diagnosis':
        return 'bg-red-100 text-red-800';
      case 'procedure':
        return 'bg-green-100 text-green-800';
      case 'document':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredRecords = records.filter((record) =>
    `${record.title} ${record.doctor} ${record.description}`
      .toLowerCase()
      .includes(searchQuery.toLowerCase())
  );

  const visitRecords = filteredRecords.filter(r => r.type === 'visit');
  const diagnosisRecords = filteredRecords.filter(r => r.type === 'diagnosis');
  const procedureRecords = filteredRecords.filter(r => r.type === 'procedure');

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar role="patient" />
        <main className="flex-1 ml-64 mt-16">
          <div className="p-8">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Health Records</h1>
              <p className="text-gray-600">View your medical history and records</p>
            </div>

            {/* Statistics */}
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
                    Visits
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">{visitRecords.length}</p>
                    <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center">
                      <Activity className="h-6 w-6 text-green-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Diagnoses
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">{diagnosisRecords.length}</p>
                    <div className="h-12 w-12 bg-red-100 rounded-full flex items-center justify-center">
                      <Heart className="h-6 w-6 text-red-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Procedures
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">{procedureRecords.length}</p>
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
                    placeholder="Search records by title, doctor, or description..."
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
                <TabsTrigger value="all">All Records ({filteredRecords.length})</TabsTrigger>
                <TabsTrigger value="visits">Visits ({visitRecords.length})</TabsTrigger>
                <TabsTrigger value="diagnoses">Diagnoses ({diagnosisRecords.length})</TabsTrigger>
                <TabsTrigger value="procedures">Procedures ({procedureRecords.length})</TabsTrigger>
              </TabsList>

              <TabsContent value="all">
                <div className="space-y-4">
                  {filteredRecords.map((record) => (
                    <Card key={record.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="pt-6">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex-1">
                            <div className="flex items-center space-x-3 mb-2">
                              <Badge className={getTypeColor(record.type)}>
                                {record.type}
                              </Badge>
                              <h3 className="text-lg font-semibold text-gray-900">
                                {record.title}
                              </h3>
                            </div>
                            <div className="flex items-center space-x-4 text-sm text-gray-600 mb-3">
                              <div className="flex items-center space-x-1">
                                <Calendar className="h-4 w-4" />
                                <span>{record.date}</span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <User className="h-4 w-4" />
                                <span>{record.doctor}</span>
                              </div>
                            </div>
                            <p className="text-gray-700">{record.description}</p>

                            {record.vitals && (
                              <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                                <p className="text-sm font-medium text-gray-700 mb-2">Vital Signs:</p>
                                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                                  {record.vitals.bloodPressure && (
                                    <div className="flex items-center space-x-2">
                                      <Heart className="h-4 w-4 text-red-600" />
                                      <div>
                                        <p className="text-xs text-gray-500">BP</p>
                                        <p className="text-sm font-medium">{record.vitals.bloodPressure}</p>
                                      </div>
                                    </div>
                                  )}
                                  {record.vitals.heartRate && (
                                    <div className="flex items-center space-x-2">
                                      <Activity className="h-4 w-4 text-green-600" />
                                      <div>
                                        <p className="text-xs text-gray-500">HR</p>
                                        <p className="text-sm font-medium">{record.vitals.heartRate} bpm</p>
                                      </div>
                                    </div>
                                  )}
                                  {record.vitals.temperature && (
                                    <div className="flex items-center space-x-2">
                                      <Thermometer className="h-4 w-4 text-orange-600" />
                                      <div>
                                        <p className="text-xs text-gray-500">Temp</p>
                                        <p className="text-sm font-medium">{record.vitals.temperature}°F</p>
                                      </div>
                                    </div>
                                  )}
                                  {record.vitals.weight && (
                                    <div className="flex items-center space-x-2">
                                      <Weight className="h-4 w-4 text-purple-600" />
                                      <div>
                                        <p className="text-xs text-gray-500">Weight</p>
                                        <p className="text-sm font-medium">{record.vitals.weight} kg</p>
                                      </div>
                                    </div>
                                  )}
                                  {record.vitals.height && (
                                    <div className="flex items-center space-x-2">
                                      <Ruler className="h-4 w-4 text-blue-600" />
                                      <div>
                                        <p className="text-xs text-gray-500">Height</p>
                                        <p className="text-sm font-medium">{record.vitals.height} cm</p>
                                      </div>
                                    </div>
                                  )}
                                </div>
                              </div>
                            )}

                            {record.documents && record.documents.length > 0 && (
                              <div className="mt-4">
                                <p className="text-sm font-medium text-gray-700 mb-2">Attachments:</p>
                                <div className="flex flex-wrap gap-2">
                                  {record.documents.map((doc, index) => (
                                    <Badge key={index} variant="outline" className="cursor-pointer">
                                      <FileText className="h-3 w-3 mr-1" />
                                      {doc}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>

                          <div className="flex flex-col space-y-2 ml-4">
                            <Button size="sm" variant="outline">
                              <Eye className="h-4 w-4 mr-1" />
                              View
                            </Button>
                            <Button size="sm" variant="outline">
                              <Download className="h-4 w-4 mr-1" />
                              Download
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="visits">
                <div className="space-y-4">
                  {visitRecords.map((record) => (
                    <Card key={record.id}>
                      <CardContent className="pt-6">
                        <h3 className="text-lg font-semibold mb-2">{record.title}</h3>
                        <p className="text-sm text-gray-600">{record.date} - {record.doctor}</p>
                        <p className="text-gray-700 mt-2">{record.description}</p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="diagnoses">
                <div className="space-y-4">
                  {diagnosisRecords.map((record) => (
                    <Card key={record.id}>
                      <CardContent className="pt-6">
                        <h3 className="text-lg font-semibold mb-2">{record.title}</h3>
                        <p className="text-sm text-gray-600">{record.date} - {record.doctor}</p>
                        <p className="text-gray-700 mt-2">{record.description}</p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="procedures">
                <div className="space-y-4">
                  {procedureRecords.map((record) => (
                    <Card key={record.id}>
                      <CardContent className="pt-6">
                        <h3 className="text-lg font-semibold mb-2">{record.title}</h3>
                        <p className="text-sm text-gray-600">{record.date} - {record.doctor}</p>
                        <p className="text-gray-700 mt-2">{record.description}</p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </main>
      </div>
    </div>
  );
}
