'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';
import {
  Users,
  UserPlus,
  Search,
  Phone,
  Mail,
  MapPin,
  Calendar,
  FileText,
  Edit,
  Trash2,
  Eye,
} from 'lucide-react';
import { toast } from 'sonner';

interface Patient {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  dateOfBirth: string;
  gender: string;
  address: string;
  emergencyContact: string;
  emergencyPhone: string;
  bloodGroup: string;
  registeredDate: string;
  status: 'active' | 'inactive';
}

export default function PatientRegistration() {
  const [searchQuery, setSearchQuery] = useState('');
  const [showRegistrationForm, setShowRegistrationForm] = useState(false);
  const [patients] = useState<Patient[]>([
    {
      id: 'P001',
      firstName: 'Emily',
      lastName: 'Davis',
      email: 'emily.davis@email.com',
      phone: '+1 (555) 123-4567',
      dateOfBirth: '1990-05-15',
      gender: 'Female',
      address: '123 Main St, New York, NY 10001',
      emergencyContact: 'John Davis',
      emergencyPhone: '+1 (555) 123-4568',
      bloodGroup: 'O+',
      registeredDate: '2024-01-15',
      status: 'active',
    },
    {
      id: 'P002',
      firstName: 'James',
      lastName: 'Wilson',
      email: 'james.wilson@email.com',
      phone: '+1 (555) 234-5678',
      dateOfBirth: '1985-08-22',
      gender: 'Male',
      address: '456 Oak Ave, Los Angeles, CA 90001',
      emergencyContact: 'Sarah Wilson',
      emergencyPhone: '+1 (555) 234-5679',
      bloodGroup: 'A+',
      registeredDate: '2024-02-10',
      status: 'active',
    },
    {
      id: 'P003',
      firstName: 'Sarah',
      lastName: 'Miller',
      email: 'sarah.miller@email.com',
      phone: '+1 (555) 345-6789',
      dateOfBirth: '1992-11-30',
      gender: 'Female',
      address: '789 Pine Rd, Chicago, IL 60601',
      emergencyContact: 'Michael Miller',
      emergencyPhone: '+1 (555) 345-6780',
      bloodGroup: 'B+',
      registeredDate: '2024-03-05',
      status: 'active',
    },
    {
      id: 'P004',
      firstName: 'Michael',
      lastName: 'Brown',
      email: 'michael.brown@email.com',
      phone: '+1 (555) 456-7890',
      dateOfBirth: '1988-03-12',
      gender: 'Male',
      address: '321 Elm St, Houston, TX 77001',
      emergencyContact: 'Lisa Brown',
      emergencyPhone: '+1 (555) 456-7891',
      bloodGroup: 'AB+',
      registeredDate: '2024-04-20',
      status: 'active',
    },
  ]);

  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    dateOfBirth: '',
    gender: '',
    address: '',
    emergencyContact: '',
    emergencyPhone: '',
    bloodGroup: '',
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    toast.success('Patient registered successfully!');
    setShowRegistrationForm(false);
    setFormData({
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
      dateOfBirth: '',
      gender: '',
      address: '',
      emergencyContact: '',
      emergencyPhone: '',
      bloodGroup: '',
    });
  };

  const filteredPatients = patients.filter((patient) =>
    `${patient.firstName} ${patient.lastName} ${patient.email} ${patient.phone} ${patient.id}`
      .toLowerCase()
      .includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar role="staff" />
        <main className="flex-1 ml-64 mt-16">
          <div className="p-8">
            {/* Header */}
            <div className="mb-8">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900 mb-2">Patient Registration</h1>
                  <p className="text-gray-600">Register new patients and manage patient records</p>
                </div>
                <Button
                  onClick={() => setShowRegistrationForm(!showRegistrationForm)}
                  className="flex items-center space-x-2"
                >
                  <UserPlus className="h-4 w-4" />
                  <span>{showRegistrationForm ? 'Hide Form' : 'Register New Patient'}</span>
                </Button>
              </div>
            </div>

            {/* Registration Form */}
            {showRegistrationForm && (
              <Card className="mb-8">
                <CardHeader>
                  <CardTitle>New Patient Registration</CardTitle>
                  <CardDescription>Fill in the patient information below</CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmit}>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* Personal Information */}
                      <div className="space-y-4">
                        <h3 className="font-semibold text-gray-900">Personal Information</h3>
                        
                        <div>
                          <Label htmlFor="firstName">First Name *</Label>
                          <Input
                            id="firstName"
                            name="firstName"
                            value={formData.firstName}
                            onChange={handleInputChange}
                            required
                            placeholder="Enter first name"
                          />
                        </div>

                        <div>
                          <Label htmlFor="lastName">Last Name *</Label>
                          <Input
                            id="lastName"
                            name="lastName"
                            value={formData.lastName}
                            onChange={handleInputChange}
                            required
                            placeholder="Enter last name"
                          />
                        </div>

                        <div>
                          <Label htmlFor="dateOfBirth">Date of Birth *</Label>
                          <Input
                            id="dateOfBirth"
                            name="dateOfBirth"
                            type="date"
                            value={formData.dateOfBirth}
                            onChange={handleInputChange}
                            required
                          />
                        </div>

                        <div>
                          <Label htmlFor="gender">Gender *</Label>
                          <select
                            id="gender"
                            name="gender"
                            value={formData.gender}
                            onChange={handleInputChange}
                            required
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          >
                            <option value="">Select gender</option>
                            <option value="male">Male</option>
                            <option value="female">Female</option>
                            <option value="other">Other</option>
                          </select>
                        </div>

                        <div>
                          <Label htmlFor="bloodGroup">Blood Group</Label>
                          <select
                            id="bloodGroup"
                            name="bloodGroup"
                            value={formData.bloodGroup}
                            onChange={handleInputChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          >
                            <option value="">Select blood group</option>
                            <option value="A+">A+</option>
                            <option value="A-">A-</option>
                            <option value="B+">B+</option>
                            <option value="B-">B-</option>
                            <option value="AB+">AB+</option>
                            <option value="AB-">AB-</option>
                            <option value="O+">O+</option>
                            <option value="O-">O-</option>
                          </select>
                        </div>
                      </div>

                      {/* Contact Information */}
                      <div className="space-y-4">
                        <h3 className="font-semibold text-gray-900">Contact Information</h3>
                        
                        <div>
                          <Label htmlFor="email">Email *</Label>
                          <Input
                            id="email"
                            name="email"
                            type="email"
                            value={formData.email}
                            onChange={handleInputChange}
                            required
                            placeholder="patient@email.com"
                          />
                        </div>

                        <div>
                          <Label htmlFor="phone">Phone Number *</Label>
                          <Input
                            id="phone"
                            name="phone"
                            type="tel"
                            value={formData.phone}
                            onChange={handleInputChange}
                            required
                            placeholder="+1 (555) 123-4567"
                          />
                        </div>

                        <div>
                          <Label htmlFor="address">Address *</Label>
                          <Textarea
                            id="address"
                            name="address"
                            value={formData.address}
                            onChange={handleInputChange}
                            required
                            placeholder="Street, City, State, ZIP"
                            rows={3}
                          />
                        </div>

                        <div>
                          <Label htmlFor="emergencyContact">Emergency Contact Name *</Label>
                          <Input
                            id="emergencyContact"
                            name="emergencyContact"
                            value={formData.emergencyContact}
                            onChange={handleInputChange}
                            required
                            placeholder="Contact person name"
                          />
                        </div>

                        <div>
                          <Label htmlFor="emergencyPhone">Emergency Contact Phone *</Label>
                          <Input
                            id="emergencyPhone"
                            name="emergencyPhone"
                            type="tel"
                            value={formData.emergencyPhone}
                            onChange={handleInputChange}
                            required
                            placeholder="+1 (555) 123-4567"
                          />
                        </div>
                      </div>
                    </div>

                    <div className="flex justify-end space-x-4 mt-6">
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => setShowRegistrationForm(false)}
                      >
                        Cancel
                      </Button>
                      <Button type="submit">
                        Register Patient
                      </Button>
                    </div>
                  </form>
                </CardContent>
              </Card>
            )}

            {/* Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Total Patients
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">{patients.length}</p>
                    <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <Users className="h-6 w-6 text-blue-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Active Patients
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">
                      {patients.filter((p) => p.status === 'active').length}
                    </p>
                    <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center">
                      <Users className="h-6 w-6 text-green-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    New This Month
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">4</p>
                    <div className="h-12 w-12 bg-purple-100 rounded-full flex items-center justify-center">
                      <UserPlus className="h-6 w-6 text-purple-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Pending Verification
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">0</p>
                    <div className="h-12 w-12 bg-orange-100 rounded-full flex items-center justify-center">
                      <FileText className="h-6 w-6 text-orange-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Patient List */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Registered Patients</CardTitle>
                    <CardDescription>View and manage all registered patients</CardDescription>
                  </div>
                  <div className="relative w-64">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      type="text"
                      placeholder="Search patients..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Patient ID</TableHead>
                      <TableHead>Name</TableHead>
                      <TableHead>Contact</TableHead>
                      <TableHead>DOB</TableHead>
                      <TableHead>Blood Group</TableHead>
                      <TableHead>Registered Date</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredPatients.map((patient) => (
                      <TableRow key={patient.id}>
                        <TableCell className="font-medium">{patient.id}</TableCell>
                        <TableCell>
                          <div>
                            <p className="font-medium">{patient.firstName} {patient.lastName}</p>
                            <p className="text-sm text-gray-500">{patient.gender}</p>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div>
                            <p className="text-sm flex items-center space-x-1">
                              <Mail className="h-3 w-3" />
                              <span>{patient.email}</span>
                            </p>
                            <p className="text-sm flex items-center space-x-1">
                              <Phone className="h-3 w-3" />
                              <span>{patient.phone}</span>
                            </p>
                          </div>
                        </TableCell>
                        <TableCell>{patient.dateOfBirth}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{patient.bloodGroup}</Badge>
                        </TableCell>
                        <TableCell>{patient.registeredDate}</TableCell>
                        <TableCell>
                          <Badge variant={patient.status === 'active' ? 'default' : 'secondary'}>
                            {patient.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center space-x-2">
                            <Button variant="ghost" size="sm">
                              <Eye className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <Trash2 className="h-4 w-4 text-red-600" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
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
