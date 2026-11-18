'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
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
  DollarSign,
  FileText,
  CreditCard,
  Download,
  Plus,
  Search,
  CheckCircle,
  Clock,
  AlertCircle,
  Send,
  Printer,
  Trash2,
} from 'lucide-react';
import { toast } from 'sonner';

interface Invoice {
  id: string;
  patientName: string;
  patientId: string;
  date: string;
  dueDate: string;
  amount: number;
  paid: number;
  status: 'paid' | 'partial' | 'pending' | 'overdue';
  items: {
    description: string;
    quantity: number;
    price: number;
  }[];
}

export default function BillingManagement() {
  const [invoices, setInvoices] = useState<Invoice[]>([
    {
      id: 'INV001',
      patientName: 'Emily Davis',
      patientId: 'P001',
      date: '2024-10-15',
      dueDate: '2024-10-30',
      amount: 450.00,
      paid: 450.00,
      status: 'paid',
      items: [
        { description: 'Consultation Fee', quantity: 1, price: 150.00 },
        { description: 'Lab Tests', quantity: 1, price: 200.00 },
        { description: 'Medications', quantity: 1, price: 100.00 },
      ],
    },
    {
      id: 'INV002',
      patientName: 'James Wilson',
      patientId: 'P002',
      date: '2024-10-16',
      dueDate: '2024-10-31',
      amount: 800.00,
      paid: 400.00,
      status: 'partial',
      items: [
        { description: 'Surgery Consultation', quantity: 1, price: 500.00 },
        { description: 'Pre-op Tests', quantity: 1, price: 300.00 },
      ],
    },
    {
      id: 'INV003',
      patientName: 'Sarah Miller',
      patientId: 'P003',
      date: '2024-10-17',
      dueDate: '2024-11-01',
      amount: 325.00,
      paid: 0,
      status: 'pending',
      items: [
        { description: 'Annual Checkup', quantity: 1, price: 200.00 },
        { description: 'Blood Work', quantity: 1, price: 125.00 },
      ],
    },
    {
      id: 'INV004',
      patientName: 'Michael Brown',
      patientId: 'P004',
      date: '2024-09-20',
      dueDate: '2024-10-05',
      amount: 550.00,
      paid: 0,
      status: 'overdue',
      items: [
        { description: 'Emergency Visit', quantity: 1, price: 350.00 },
        { description: 'X-Ray', quantity: 1, price: 200.00 },
      ],
    },
  ]);

  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showPaymentDialog, setShowPaymentDialog] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null);
  const [paymentAmount, setPaymentAmount] = useState('');

  const [formData, setFormData] = useState({
    patientId: '',
    patientName: '',
    items: [{ description: '', quantity: 1, price: 0 }],
    dueDate: '',
  });

  const handleAddItem = () => {
    setFormData({
      ...formData,
      items: [...formData.items, { description: '', quantity: 1, price: 0 }],
    });
  };

  const handleItemChange = (index: number, field: string, value: any) => {
    const newItems = [...formData.items];
    newItems[index] = { ...newItems[index], [field]: value };
    setFormData({ ...formData, items: newItems });
  };

  const handleRemoveItem = (index: number) => {
    const newItems = formData.items.filter((_, i) => i !== index);
    setFormData({ ...formData, items: newItems });
  };

  const calculateTotal = () => {
    return formData.items.reduce((sum, item) => sum + (item.quantity * item.price), 0);
  };

  const handleCreateInvoice = (e: React.FormEvent) => {
    e.preventDefault();
    const today = new Date().toISOString().split('T')[0];
    const newInvoice: Invoice = {
      id: `INV${(invoices.length + 1).toString().padStart(3, '0')}`,
      patientName: formData.patientName,
      patientId: formData.patientId,
      date: today,
      dueDate: formData.dueDate,
      amount: calculateTotal(),
      paid: 0,
      status: 'pending',
      items: formData.items,
    };
    setInvoices([...invoices, newInvoice]);
    toast.success('Invoice created successfully!');
    setShowCreateDialog(false);
    setFormData({
      patientId: '',
      patientName: '',
      items: [{ description: '', quantity: 1, price: 0 }],
      dueDate: '',
    });
  };

  const handleProcessPayment = () => {
    if (!selectedInvoice) return;
    const amount = parseFloat(paymentAmount);
    const newPaid = selectedInvoice.paid + amount;
    let newStatus: Invoice['status'];
    
    if (newPaid >= selectedInvoice.amount) {
      newStatus = 'paid';
    } else if (newPaid > 0) {
      newStatus = 'partial';
    } else {
      newStatus = 'pending';
    }

    setInvoices(invoices.map(inv =>
      inv.id === selectedInvoice.id
        ? { ...inv, paid: newPaid, status: newStatus }
        : inv
    ));
    
    toast.success(`Payment of $${amount.toFixed(2)} processed successfully!`);
    setShowPaymentDialog(false);
    setSelectedInvoice(null);
    setPaymentAmount('');
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid':
        return 'default';
      case 'partial':
        return 'secondary';
      case 'pending':
        return 'outline';
      case 'overdue':
        return 'destructive';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'paid':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'partial':
        return <Clock className="h-4 w-4 text-blue-600" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-orange-600" />;
      case 'overdue':
        return <AlertCircle className="h-4 w-4 text-red-600" />;
      default:
        return null;
    }
  };

  const filteredInvoices = invoices.filter((inv) => {
    const matchesSearch = `${inv.patientName} ${inv.patientId} ${inv.id}`
      .toLowerCase()
      .includes(searchQuery.toLowerCase());
    const matchesStatus = filterStatus === 'all' || inv.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const totalRevenue = invoices.reduce((sum, inv) => sum + inv.paid, 0);
  const pendingAmount = invoices.reduce((sum, inv) => sum + (inv.amount - inv.paid), 0);

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
                  <h1 className="text-3xl font-bold text-gray-900 mb-2">Billing Management</h1>
                  <p className="text-gray-600">Create invoices and process payments</p>
                </div>
                <Button
                  onClick={() => setShowCreateDialog(true)}
                  className="flex items-center space-x-2"
                >
                  <Plus className="h-4 w-4" />
                  <span>Create Invoice</span>
                </Button>
              </div>
            </div>

            {/* Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Total Revenue
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">${totalRevenue.toFixed(2)}</p>
                    <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center">
                      <DollarSign className="h-6 w-6 text-green-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Pending Payments
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">${pendingAmount.toFixed(2)}</p>
                    <div className="h-12 w-12 bg-orange-100 rounded-full flex items-center justify-center">
                      <Clock className="h-6 w-6 text-orange-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Total Invoices
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">{invoices.length}</p>
                    <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <FileText className="h-6 w-6 text-blue-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Overdue
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">
                      {invoices.filter(i => i.status === 'overdue').length}
                    </p>
                    <div className="h-12 w-12 bg-red-100 rounded-full flex items-center justify-center">
                      <AlertCircle className="h-6 w-6 text-red-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Filters */}
            <Card className="mb-6">
              <CardContent className="pt-6">
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="flex-1 relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      type="text"
                      placeholder="Search by patient, invoice ID..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  <select
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="all">All Status</option>
                    <option value="paid">Paid</option>
                    <option value="partial">Partial</option>
                    <option value="pending">Pending</option>
                    <option value="overdue">Overdue</option>
                  </select>
                </div>
              </CardContent>
            </Card>

            {/* Invoices Table */}
            <Card>
              <CardHeader>
                <CardTitle>All Invoices</CardTitle>
                <CardDescription>Manage patient invoices and payments</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Invoice ID</TableHead>
                      <TableHead>Patient</TableHead>
                      <TableHead>Date</TableHead>
                      <TableHead>Due Date</TableHead>
                      <TableHead>Amount</TableHead>
                      <TableHead>Paid</TableHead>
                      <TableHead>Balance</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredInvoices.map((invoice) => (
                      <TableRow key={invoice.id}>
                        <TableCell className="font-medium">{invoice.id}</TableCell>
                        <TableCell>
                          <div>
                            <p className="font-medium">{invoice.patientName}</p>
                            <p className="text-sm text-gray-500">{invoice.patientId}</p>
                          </div>
                        </TableCell>
                        <TableCell>{invoice.date}</TableCell>
                        <TableCell>{invoice.dueDate}</TableCell>
                        <TableCell>${invoice.amount.toFixed(2)}</TableCell>
                        <TableCell className="text-green-600">
                          ${invoice.paid.toFixed(2)}
                        </TableCell>
                        <TableCell className="text-red-600">
                          ${(invoice.amount - invoice.paid).toFixed(2)}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center space-x-2">
                            {getStatusIcon(invoice.status)}
                            <Badge variant={getStatusColor(invoice.status)}>
                              {invoice.status}
                            </Badge>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center space-x-2">
                            {invoice.status !== 'paid' && (
                              <Button
                                size="sm"
                                onClick={() => {
                                  setSelectedInvoice(invoice);
                                  setShowPaymentDialog(true);
                                }}
                              >
                                <CreditCard className="h-4 w-4 mr-1" />
                                Pay
                              </Button>
                            )}
                            <Button variant="ghost" size="sm">
                              <Printer className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <Download className="h-4 w-4" />
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

      {/* Create Invoice Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create New Invoice</DialogTitle>
            <DialogDescription>Fill in the invoice details and items</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleCreateInvoice}>
            <div className="space-y-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="patientId">Patient ID *</Label>
                  <Input
                    id="patientId"
                    value={formData.patientId}
                    onChange={(e) => setFormData({ ...formData, patientId: e.target.value })}
                    required
                    placeholder="P001"
                  />
                </div>
                <div>
                  <Label htmlFor="patientName">Patient Name *</Label>
                  <Input
                    id="patientName"
                    value={formData.patientName}
                    onChange={(e) => setFormData({ ...formData, patientName: e.target.value })}
                    required
                    placeholder="John Doe"
                  />
                </div>
                <div className="col-span-2">
                  <Label htmlFor="dueDate">Due Date *</Label>
                  <Input
                    id="dueDate"
                    type="date"
                    value={formData.dueDate}
                    onChange={(e) => setFormData({ ...formData, dueDate: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className="border-t pt-4">
                <div className="flex items-center justify-between mb-4">
                  <Label>Invoice Items</Label>
                  <Button type="button" variant="outline" size="sm" onClick={handleAddItem}>
                    <Plus className="h-4 w-4 mr-1" />
                    Add Item
                  </Button>
                </div>

                <div className="space-y-3">
                  {formData.items.map((item, index) => (
                    <div key={index} className="grid grid-cols-12 gap-2 items-end">
                      <div className="col-span-5">
                        <Label>Description</Label>
                        <Input
                          value={item.description}
                          onChange={(e) => handleItemChange(index, 'description', e.target.value)}
                          required
                          placeholder="Service/Item description"
                        />
                      </div>
                      <div className="col-span-2">
                        <Label>Qty</Label>
                        <Input
                          type="number"
                          min="1"
                          value={item.quantity}
                          onChange={(e) => handleItemChange(index, 'quantity', parseInt(e.target.value))}
                          required
                        />
                      </div>
                      <div className="col-span-3">
                        <Label>Price</Label>
                        <Input
                          type="number"
                          min="0"
                          step="0.01"
                          value={item.price}
                          onChange={(e) => handleItemChange(index, 'price', parseFloat(e.target.value))}
                          required
                        />
                      </div>
                      <div className="col-span-2">
                        {formData.items.length > 1 && (
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRemoveItem(index)}
                          >
                            <Trash2 className="h-4 w-4 text-red-600" />
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-4 pt-4 border-t">
                  <div className="flex justify-between items-center">
                    <span className="font-semibold">Total Amount:</span>
                    <span className="text-2xl font-bold">${calculateTotal().toFixed(2)}</span>
                  </div>
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowCreateDialog(false)}>
                Cancel
              </Button>
              <Button type="submit">Create Invoice</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Payment Dialog */}
      <Dialog open={showPaymentDialog} onOpenChange={setShowPaymentDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Process Payment</DialogTitle>
            <DialogDescription>
              Enter the payment amount for {selectedInvoice?.patientName}
            </DialogDescription>
          </DialogHeader>
          {selectedInvoice && (
            <div className="space-y-4 py-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="flex justify-between mb-2">
                  <span className="text-gray-600">Invoice Total:</span>
                  <span className="font-semibold">${selectedInvoice.amount.toFixed(2)}</span>
                </div>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-600">Already Paid:</span>
                  <span className="font-semibold text-green-600">
                    ${selectedInvoice.paid.toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between border-t pt-2">
                  <span className="font-semibold">Remaining Balance:</span>
                  <span className="font-semibold text-red-600">
                    ${(selectedInvoice.amount - selectedInvoice.paid).toFixed(2)}
                  </span>
                </div>
              </div>

              <div>
                <Label htmlFor="paymentAmount">Payment Amount *</Label>
                <Input
                  id="paymentAmount"
                  type="number"
                  min="0"
                  step="0.01"
                  max={selectedInvoice.amount - selectedInvoice.paid}
                  value={paymentAmount}
                  onChange={(e) => setPaymentAmount(e.target.value)}
                  placeholder="0.00"
                />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPaymentDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleProcessPayment}>
              Process Payment
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
