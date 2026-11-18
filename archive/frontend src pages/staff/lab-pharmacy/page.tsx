'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
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
  TestTube,
  Pill,
  Plus,
  Search,
  Clock,
  CheckCircle,
  Package,
  AlertCircle,
  FileText,
  Trash2,
  Edit,
} from 'lucide-react';
import { toast } from 'sonner';

interface LabOrder {
  id: string;
  patientName: string;
  patientId: string;
  testType: string;
  orderedBy: string;
  orderDate: string;
  status: 'pending' | 'in_progress' | 'completed';
  priority: 'routine' | 'urgent' | 'stat';
  notes?: string;
}

interface Medication {
  id: string;
  name: string;
  category: string;
  stock: number;
  reorderLevel: number;
  unit: string;
  price: number;
  expiryDate: string;
}

interface PrescriptionOrder {
  id: string;
  patientName: string;
  patientId: string;
  medication: string;
  dosage: string;
  quantity: number;
  prescribedBy: string;
  orderDate: string;
  status: 'pending' | 'filled' | 'dispensed';
}

export default function LabPharmacyManagement() {
  const [labOrders, setLabOrders] = useState<LabOrder[]>([
    {
      id: 'LAB001',
      patientName: 'Emily Davis',
      patientId: 'P001',
      testType: 'Complete Blood Count (CBC)',
      orderedBy: 'Dr. Sarah Johnson',
      orderDate: '2024-10-18',
      status: 'pending',
      priority: 'routine',
      notes: 'Fasting required',
    },
    {
      id: 'LAB002',
      patientName: 'James Wilson',
      patientId: 'P002',
      testType: 'Lipid Panel',
      orderedBy: 'Dr. Michael Chen',
      orderDate: '2024-10-18',
      status: 'in_progress',
      priority: 'routine',
    },
    {
      id: 'LAB003',
      patientName: 'Sarah Miller',
      patientId: 'P003',
      testType: 'Cardiac Enzymes',
      orderedBy: 'Dr. Emily Rodriguez',
      orderDate: '2024-10-18',
      status: 'pending',
      priority: 'stat',
      notes: 'Urgent - chest pain evaluation',
    },
  ]);

  const [medications, setMedications] = useState<Medication[]>([
    {
      id: 'MED001',
      name: 'Amoxicillin 500mg',
      category: 'Antibiotics',
      stock: 150,
      reorderLevel: 50,
      unit: 'Capsules',
      price: 0.75,
      expiryDate: '2025-06-30',
    },
    {
      id: 'MED002',
      name: 'Lisinopril 10mg',
      category: 'Cardiovascular',
      stock: 30,
      reorderLevel: 50,
      unit: 'Tablets',
      price: 0.25,
      expiryDate: '2025-03-15',
    },
    {
      id: 'MED003',
      name: 'Metformin 500mg',
      category: 'Diabetes',
      stock: 200,
      reorderLevel: 75,
      unit: 'Tablets',
      price: 0.15,
      expiryDate: '2025-08-20',
    },
    {
      id: 'MED004',
      name: 'Ibuprofen 200mg',
      category: 'Pain Relief',
      stock: 500,
      reorderLevel: 100,
      unit: 'Tablets',
      price: 0.05,
      expiryDate: '2025-12-31',
    },
  ]);

  const [prescriptionOrders, setPrescriptionOrders] = useState<PrescriptionOrder[]>([
    {
      id: 'RX001',
      patientName: 'Emily Davis',
      patientId: 'P001',
      medication: 'Amoxicillin 500mg',
      dosage: '1 capsule 3x daily',
      quantity: 21,
      prescribedBy: 'Dr. Sarah Johnson',
      orderDate: '2024-10-18',
      status: 'pending',
    },
    {
      id: 'RX002',
      patientName: 'Michael Brown',
      patientId: 'P004',
      medication: 'Lisinopril 10mg',
      dosage: '1 tablet daily',
      quantity: 30,
      prescribedBy: 'Dr. Michael Chen',
      orderDate: '2024-10-17',
      status: 'filled',
    },
  ]);

  const [showLabDialog, setShowLabDialog] = useState(false);
  const [showPharmacyDialog, setShowPharmacyDialog] = useState(false);
  const [labFormData, setLabFormData] = useState({
    patientId: '',
    patientName: '',
    testType: '',
    orderedBy: '',
    priority: 'routine',
    notes: '',
  });

  const [rxFormData, setRxFormData] = useState({
    patientId: '',
    patientName: '',
    medication: '',
    dosage: '',
    quantity: 0,
    prescribedBy: '',
  });

  const handleLabOrderSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const today = new Date().toISOString().split('T')[0];
    const newOrder: LabOrder = {
      id: `LAB${(labOrders.length + 1).toString().padStart(3, '0')}`,
      ...labFormData,
      orderDate: today,
      status: 'pending',
      priority: labFormData.priority as LabOrder['priority'],
    };
    setLabOrders([...labOrders, newOrder]);
    toast.success('Lab test ordered successfully!');
    setShowLabDialog(false);
    setLabFormData({
      patientId: '',
      patientName: '',
      testType: '',
      orderedBy: '',
      priority: 'routine',
      notes: '',
    });
  };

  const handlePrescriptionSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const today = new Date().toISOString().split('T')[0];
    const newOrder: PrescriptionOrder = {
      id: `RX${(prescriptionOrders.length + 1).toString().padStart(3, '0')}`,
      ...rxFormData,
      orderDate: today,
      status: 'pending',
    };
    setPrescriptionOrders([...prescriptionOrders, newOrder]);
    toast.success('Prescription ordered successfully!');
    setShowPharmacyDialog(false);
    setRxFormData({
      patientId: '',
      patientName: '',
      medication: '',
      dosage: '',
      quantity: 0,
      prescribedBy: '',
    });
  };

  const updateLabStatus = (id: string, status: LabOrder['status']) => {
    setLabOrders(labOrders.map(order => 
      order.id === id ? { ...order, status } : order
    ));
    toast.success(`Lab order ${status}`);
  };

  const updateRxStatus = (id: string, status: PrescriptionOrder['status']) => {
    setPrescriptionOrders(prescriptionOrders.map(order => 
      order.id === id ? { ...order, status } : order
    ));
    toast.success(`Prescription ${status}`);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'stat':
        return 'destructive';
      case 'urgent':
        return 'default';
      case 'routine':
        return 'secondary';
      default:
        return 'secondary';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
      case 'dispensed':
        return 'default';
      case 'in_progress':
      case 'filled':
        return 'secondary';
      case 'pending':
        return 'outline';
      default:
        return 'outline';
    }
  };

  const lowStockMeds = medications.filter(med => med.stock <= med.reorderLevel);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar role="staff" />
        <main className="flex-1 ml-64 mt-16">
          <div className="p-8">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Lab & Pharmacy Management</h1>
              <p className="text-gray-600">Order lab tests and manage pharmacy inventory</p>
            </div>

            {/* Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Pending Lab Tests
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">
                      {labOrders.filter(o => o.status === 'pending').length}
                    </p>
                    <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <TestTube className="h-6 w-6 text-blue-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Pending Prescriptions
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">
                      {prescriptionOrders.filter(o => o.status === 'pending').length}
                    </p>
                    <div className="h-12 w-12 bg-purple-100 rounded-full flex items-center justify-center">
                      <Pill className="h-6 w-6 text-purple-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Low Stock Items
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">{lowStockMeds.length}</p>
                    <div className="h-12 w-12 bg-orange-100 rounded-full flex items-center justify-center">
                      <AlertCircle className="h-6 w-6 text-orange-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Total Medications
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">{medications.length}</p>
                    <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center">
                      <Package className="h-6 w-6 text-green-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Tabs */}
            <Tabs defaultValue="lab" className="space-y-6">
              <TabsList>
                <TabsTrigger value="lab">Lab Tests</TabsTrigger>
                <TabsTrigger value="pharmacy">Prescriptions</TabsTrigger>
                <TabsTrigger value="inventory">Medication Inventory</TabsTrigger>
              </TabsList>

              {/* Lab Tests Tab */}
              <TabsContent value="lab">
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle>Lab Test Orders</CardTitle>
                        <CardDescription>Order and track lab tests</CardDescription>
                      </div>
                      <Button onClick={() => setShowLabDialog(true)}>
                        <Plus className="h-4 w-4 mr-2" />
                        Order Lab Test
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Order ID</TableHead>
                          <TableHead>Patient</TableHead>
                          <TableHead>Test Type</TableHead>
                          <TableHead>Ordered By</TableHead>
                          <TableHead>Date</TableHead>
                          <TableHead>Priority</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {labOrders.map((order) => (
                          <TableRow key={order.id}>
                            <TableCell className="font-medium">{order.id}</TableCell>
                            <TableCell>
                              <div>
                                <p className="font-medium">{order.patientName}</p>
                                <p className="text-sm text-gray-500">{order.patientId}</p>
                              </div>
                            </TableCell>
                            <TableCell>{order.testType}</TableCell>
                            <TableCell>{order.orderedBy}</TableCell>
                            <TableCell>{order.orderDate}</TableCell>
                            <TableCell>
                              <Badge variant={getPriorityColor(order.priority)}>
                                {order.priority}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <Badge variant={getStatusColor(order.status)}>
                                {order.status.replace('_', ' ')}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <div className="flex items-center space-x-2">
                                {order.status === 'pending' && (
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => updateLabStatus(order.id, 'in_progress')}
                                  >
                                    Start
                                  </Button>
                                )}
                                {order.status === 'in_progress' && (
                                  <Button
                                    size="sm"
                                    onClick={() => updateLabStatus(order.id, 'completed')}
                                  >
                                    Complete
                                  </Button>
                                )}
                                <Button variant="ghost" size="sm">
                                  <FileText className="h-4 w-4" />
                                </Button>
                              </div>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Prescriptions Tab */}
              <TabsContent value="pharmacy">
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle>Prescription Orders</CardTitle>
                        <CardDescription>Fill and dispense prescriptions</CardDescription>
                      </div>
                      <Button onClick={() => setShowPharmacyDialog(true)}>
                        <Plus className="h-4 w-4 mr-2" />
                        New Prescription
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Rx ID</TableHead>
                          <TableHead>Patient</TableHead>
                          <TableHead>Medication</TableHead>
                          <TableHead>Dosage</TableHead>
                          <TableHead>Quantity</TableHead>
                          <TableHead>Prescribed By</TableHead>
                          <TableHead>Date</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {prescriptionOrders.map((order) => (
                          <TableRow key={order.id}>
                            <TableCell className="font-medium">{order.id}</TableCell>
                            <TableCell>
                              <div>
                                <p className="font-medium">{order.patientName}</p>
                                <p className="text-sm text-gray-500">{order.patientId}</p>
                              </div>
                            </TableCell>
                            <TableCell>{order.medication}</TableCell>
                            <TableCell>{order.dosage}</TableCell>
                            <TableCell>{order.quantity}</TableCell>
                            <TableCell>{order.prescribedBy}</TableCell>
                            <TableCell>{order.orderDate}</TableCell>
                            <TableCell>
                              <Badge variant={getStatusColor(order.status)}>
                                {order.status}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <div className="flex items-center space-x-2">
                                {order.status === 'pending' && (
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => updateRxStatus(order.id, 'filled')}
                                  >
                                    Fill
                                  </Button>
                                )}
                                {order.status === 'filled' && (
                                  <Button
                                    size="sm"
                                    onClick={() => updateRxStatus(order.id, 'dispensed')}
                                  >
                                    Dispense
                                  </Button>
                                )}
                                <Button variant="ghost" size="sm">
                                  <FileText className="h-4 w-4" />
                                </Button>
                              </div>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Inventory Tab */}
              <TabsContent value="inventory">
                <Card>
                  <CardHeader>
                    <CardTitle>Medication Inventory</CardTitle>
                    <CardDescription>Track and manage medication stock levels</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {lowStockMeds.length > 0 && (
                      <div className="mb-4 p-4 bg-orange-50 border border-orange-200 rounded-lg">
                        <div className="flex items-center space-x-2 text-orange-800">
                          <AlertCircle className="h-5 w-5" />
                          <p className="font-medium">
                            {lowStockMeds.length} medication(s) below reorder level
                          </p>
                        </div>
                      </div>
                    )}

                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Med ID</TableHead>
                          <TableHead>Medication Name</TableHead>
                          <TableHead>Category</TableHead>
                          <TableHead>Stock Level</TableHead>
                          <TableHead>Reorder Level</TableHead>
                          <TableHead>Unit</TableHead>
                          <TableHead>Price</TableHead>
                          <TableHead>Expiry Date</TableHead>
                          <TableHead>Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {medications.map((med) => (
                          <TableRow key={med.id}>
                            <TableCell className="font-medium">{med.id}</TableCell>
                            <TableCell>{med.name}</TableCell>
                            <TableCell>{med.category}</TableCell>
                            <TableCell>
                              <div className="flex items-center space-x-2">
                                <span className={med.stock <= med.reorderLevel ? 'text-red-600 font-semibold' : ''}>
                                  {med.stock}
                                </span>
                                {med.stock <= med.reorderLevel && (
                                  <Badge variant="destructive" className="text-xs">
                                    Low
                                  </Badge>
                                )}
                              </div>
                            </TableCell>
                            <TableCell>{med.reorderLevel}</TableCell>
                            <TableCell>{med.unit}</TableCell>
                            <TableCell>${med.price.toFixed(2)}</TableCell>
                            <TableCell>{med.expiryDate}</TableCell>
                            <TableCell>
                              <div className="flex items-center space-x-2">
                                <Button variant="ghost" size="sm">
                                  <Edit className="h-4 w-4" />
                                </Button>
                                {med.stock <= med.reorderLevel && (
                                  <Button size="sm" variant="outline">
                                    <Package className="h-4 w-4 mr-1" />
                                    Reorder
                                  </Button>
                                )}
                              </div>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </main>
      </div>

      {/* Lab Order Dialog */}
      <Dialog open={showLabDialog} onOpenChange={setShowLabDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Order Lab Test</DialogTitle>
            <DialogDescription>Fill in the lab test details</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleLabOrderSubmit}>
            <div className="space-y-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="labPatientId">Patient ID *</Label>
                  <Input
                    id="labPatientId"
                    value={labFormData.patientId}
                    onChange={(e) => setLabFormData({ ...labFormData, patientId: e.target.value })}
                    required
                    placeholder="P001"
                  />
                </div>
                <div>
                  <Label htmlFor="labPatientName">Patient Name *</Label>
                  <Input
                    id="labPatientName"
                    value={labFormData.patientName}
                    onChange={(e) => setLabFormData({ ...labFormData, patientName: e.target.value })}
                    required
                    placeholder="John Doe"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="testType">Test Type *</Label>
                <select
                  id="testType"
                  value={labFormData.testType}
                  onChange={(e) => setLabFormData({ ...labFormData, testType: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select test type</option>
                  <option value="Complete Blood Count (CBC)">Complete Blood Count (CBC)</option>
                  <option value="Lipid Panel">Lipid Panel</option>
                  <option value="Metabolic Panel">Metabolic Panel</option>
                  <option value="Urinalysis">Urinalysis</option>
                  <option value="Cardiac Enzymes">Cardiac Enzymes</option>
                  <option value="Thyroid Function">Thyroid Function</option>
                  <option value="HbA1c">HbA1c</option>
                </select>
              </div>

              <div>
                <Label htmlFor="orderedBy">Ordered By *</Label>
                <Input
                  id="orderedBy"
                  value={labFormData.orderedBy}
                  onChange={(e) => setLabFormData({ ...labFormData, orderedBy: e.target.value })}
                  required
                  placeholder="Dr. Name"
                />
              </div>

              <div>
                <Label htmlFor="priority">Priority *</Label>
                <select
                  id="priority"
                  value={labFormData.priority}
                  onChange={(e) => setLabFormData({ ...labFormData, priority: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="routine">Routine</option>
                  <option value="urgent">Urgent</option>
                  <option value="stat">STAT</option>
                </select>
              </div>

              <div>
                <Label htmlFor="labNotes">Notes</Label>
                <Textarea
                  id="labNotes"
                  value={labFormData.notes}
                  onChange={(e) => setLabFormData({ ...labFormData, notes: e.target.value })}
                  placeholder="Special instructions..."
                  rows={3}
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowLabDialog(false)}>
                Cancel
              </Button>
              <Button type="submit">Order Lab Test</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Prescription Dialog */}
      <Dialog open={showPharmacyDialog} onOpenChange={setShowPharmacyDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>New Prescription Order</DialogTitle>
            <DialogDescription>Fill in the prescription details</DialogDescription>
          </DialogHeader>
          <form onSubmit={handlePrescriptionSubmit}>
            <div className="space-y-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="rxPatientId">Patient ID *</Label>
                  <Input
                    id="rxPatientId"
                    value={rxFormData.patientId}
                    onChange={(e) => setRxFormData({ ...rxFormData, patientId: e.target.value })}
                    required
                    placeholder="P001"
                  />
                </div>
                <div>
                  <Label htmlFor="rxPatientName">Patient Name *</Label>
                  <Input
                    id="rxPatientName"
                    value={rxFormData.patientName}
                    onChange={(e) => setRxFormData({ ...rxFormData, patientName: e.target.value })}
                    required
                    placeholder="John Doe"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="medication">Medication *</Label>
                <select
                  id="medication"
                  value={rxFormData.medication}
                  onChange={(e) => setRxFormData({ ...rxFormData, medication: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select medication</option>
                  {medications.map((med) => (
                    <option key={med.id} value={med.name}>
                      {med.name} (Stock: {med.stock})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <Label htmlFor="dosage">Dosage Instructions *</Label>
                <Input
                  id="dosage"
                  value={rxFormData.dosage}
                  onChange={(e) => setRxFormData({ ...rxFormData, dosage: e.target.value })}
                  required
                  placeholder="e.g., 1 tablet twice daily"
                />
              </div>

              <div>
                <Label htmlFor="quantity">Quantity *</Label>
                <Input
                  id="quantity"
                  type="number"
                  min="1"
                  value={rxFormData.quantity}
                  onChange={(e) => setRxFormData({ ...rxFormData, quantity: parseInt(e.target.value) })}
                  required
                  placeholder="30"
                />
              </div>

              <div>
                <Label htmlFor="rxPrescribedBy">Prescribed By *</Label>
                <Input
                  id="rxPrescribedBy"
                  value={rxFormData.prescribedBy}
                  onChange={(e) => setRxFormData({ ...rxFormData, prescribedBy: e.target.value })}
                  required
                  placeholder="Dr. Name"
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowPharmacyDialog(false)}>
                Cancel
              </Button>
              <Button type="submit">Create Prescription</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
