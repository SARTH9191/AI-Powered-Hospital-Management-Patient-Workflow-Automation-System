'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Search, Filter, MoreVertical, Eye, FileText, Phone, Mail } from 'lucide-react';
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';

interface Patient {
  id: string;
  name: string;
  age: number;
  gender: string;
  condition: string;
  lastVisit: string;
  nextAppointment: string;
  status: 'active' | 'recovering' | 'critical';
  phone: string;
  email: string;
}

export default function MyPatientsPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [filteredPatients, setFilteredPatients] = useState<Patient[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Mock data - replace with real API call
    const mockPatients: Patient[] = [
      {
        id: '1',
        name: 'John Doe',
        age: 45,
        gender: 'Male',
        condition: 'Hypertension',
        lastVisit: '2024-10-15',
        nextAppointment: '2024-10-25',
        status: 'active',
        phone: '+1 (555) 123-4567',
        email: 'john.doe@email.com',
      },
      {
        id: '2',
        name: 'Mary Smith',
        age: 32,
        gender: 'Female',
        condition: 'Diabetes Type 2',
        lastVisit: '2024-10-16',
        nextAppointment: '2024-10-23',
        status: 'recovering',
        phone: '+1 (555) 234-5678',
        email: 'mary.smith@email.com',
      },
      {
        id: '3',
        name: 'Robert Johnson',
        age: 58,
        gender: 'Male',
        condition: 'Heart Disease',
        lastVisit: '2024-10-17',
        nextAppointment: '2024-10-20',
        status: 'critical',
        phone: '+1 (555) 345-6789',
        email: 'robert.j@email.com',
      },
      {
        id: '4',
        name: 'Sarah Williams',
        age: 28,
        gender: 'Female',
        condition: 'Asthma',
        lastVisit: '2024-10-14',
        nextAppointment: '2024-10-28',
        status: 'active',
        phone: '+1 (555) 456-7890',
        email: 'sarah.w@email.com',
      },
      {
        id: '5',
        name: 'Michael Brown',
        age: 52,
        gender: 'Male',
        condition: 'Arthritis',
        lastVisit: '2024-10-13',
        nextAppointment: '2024-10-27',
        status: 'recovering',
        phone: '+1 (555) 567-8901',
        email: 'michael.b@email.com',
      },
      {
        id: '6',
        name: 'Emily Davis',
        age: 39,
        gender: 'Female',
        condition: 'Migraine',
        lastVisit: '2024-10-18',
        nextAppointment: '2024-10-30',
        status: 'active',
        phone: '+1 (555) 678-9012',
        email: 'emily.d@email.com',
      },
    ];

    setTimeout(() => {
      setPatients(mockPatients);
      setFilteredPatients(mockPatients);
      setIsLoading(false);
    }, 500);
  }, []);

  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredPatients(patients);
    } else {
      const query = searchQuery.toLowerCase();
      const filtered = patients.filter(
        (patient) =>
          patient.name.toLowerCase().includes(query) ||
          patient.condition.toLowerCase().includes(query) ||
          patient.email.toLowerCase().includes(query)
      );
      setFilteredPatients(filtered);
    }
  }, [searchQuery, patients]);

  const getStatusBadge = (status: Patient['status']) => {
    switch (status) {
      case 'active':
        return <Badge variant="default">Active</Badge>;
      case 'recovering':
        return <Badge variant="secondary" className="bg-yellow-100 text-yellow-700">Recovering</Badge>;
      case 'critical':
        return <Badge variant="destructive">Critical</Badge>;
    }
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar role="doctor" />
        <main className="flex-1 ml-64 mt-16">
          <div className="p-8">
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">My Patients</h1>
              <p className="text-gray-600">Manage and view your patient roster</p>
            </div>

            {/* Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <Card>
                <CardContent className="pt-6">
                  <p className="text-sm text-gray-600">Total Patients</p>
                  <p className="text-2xl font-bold text-gray-900">{patients.length}</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <p className="text-sm text-gray-600">Active</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {patients.filter((p) => p.status === 'active').length}
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <p className="text-sm text-gray-600">Recovering</p>
                  <p className="text-2xl font-bold text-yellow-600">
                    {patients.filter((p) => p.status === 'recovering').length}
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <p className="text-sm text-gray-600">Critical</p>
                  <p className="text-2xl font-bold text-red-600">
                    {patients.filter((p) => p.status === 'critical').length}
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Search and Filter */}
            <div className="flex items-center justify-between mb-6">
              <div className="relative w-96">
                <Search className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                <Input
                  type="text"
                  placeholder="Search by name, condition, or email..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filter
              </Button>
            </div>

            {/* Patients Table */}
            <Card>
              <CardHeader>
                <CardTitle>Patient List</CardTitle>
                <CardDescription>All patients under your care</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Patient</TableHead>
                      <TableHead>Age/Gender</TableHead>
                      <TableHead>Condition</TableHead>
                      <TableHead>Last Visit</TableHead>
                      <TableHead>Next Appointment</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {isLoading ? (
                      <TableRow>
                        <TableCell colSpan={7} className="text-center py-8">
                          Loading patients...
                        </TableCell>
                      </TableRow>
                    ) : filteredPatients.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={7} className="text-center py-8 text-gray-500">
                          No patients found
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredPatients.map((patient) => (
                        <TableRow key={patient.id}>
                          <TableCell>
                            <div className="flex items-center space-x-3">
                              <Avatar>
                                <AvatarFallback className="bg-blue-100 text-blue-600">
                                  {getInitials(patient.name)}
                                </AvatarFallback>
                              </Avatar>
                              <div>
                                <p className="font-medium text-gray-900">{patient.name}</p>
                                <p className="text-sm text-gray-500">ID: {patient.id}</p>
                              </div>
                            </div>
                          </TableCell>
                          <TableCell className="text-gray-600">
                            {patient.age} / {patient.gender}
                          </TableCell>
                          <TableCell>
                            <span className="text-sm font-medium text-gray-900">
                              {patient.condition}
                            </span>
                          </TableCell>
                          <TableCell className="text-gray-600">
                            {new Date(patient.lastVisit).toLocaleDateString()}
                          </TableCell>
                          <TableCell className="text-gray-600">
                            {new Date(patient.nextAppointment).toLocaleDateString()}
                          </TableCell>
                          <TableCell>{getStatusBadge(patient.status)}</TableCell>
                          <TableCell className="text-right">
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="sm">
                                  <MoreVertical className="h-4 w-4" />
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end">
                                <DropdownMenuLabel>Actions</DropdownMenuLabel>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem>
                                  <Eye className="h-4 w-4 mr-2" />
                                  View Details
                                </DropdownMenuItem>
                                <DropdownMenuItem>
                                  <FileText className="h-4 w-4 mr-2" />
                                  Medical Records
                                </DropdownMenuItem>
                                <DropdownMenuItem>
                                  <Phone className="h-4 w-4 mr-2" />
                                  Call Patient
                                </DropdownMenuItem>
                                <DropdownMenuItem>
                                  <Mail className="h-4 w-4 mr-2" />
                                  Send Email
                                </DropdownMenuItem>
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}
