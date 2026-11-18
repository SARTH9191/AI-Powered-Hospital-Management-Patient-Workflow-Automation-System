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
  DialogFooter,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';
import {
  DollarSign,
  Search,
  Calendar,
  Download,
  CreditCard,
  FileText,
  CheckCircle,
  AlertCircle,
  Clock,
} from 'lucide-react';

interface Invoice {
  id: string;
  invoiceNumber: string;
  date: string;
  dueDate: string;
  amount: number;
  amountPaid: number;
  status: 'paid' | 'partial' | 'pending' | 'overdue';
  description: string;
  items: {
    description: string;
    quantity: number;
    unitPrice: number;
    total: number;
  }[];
}

export default function PatientBilling() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null);
  const [showPaymentDialog, setShowPaymentDialog] = useState(false);
  const [showInvoiceDialog, setShowInvoiceDialog] = useState(false);
  const [paymentAmount, setPaymentAmount] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('');

  const [invoices] = useState<Invoice[]>([
    {
      id: 'INV001',
      invoiceNumber: 'INV-2024-001',
      date: '2024-10-15',
      dueDate: '2024-10-30',
      amount: 450.0,
      amountPaid: 450.0,
      status: 'paid',
      description: 'Cardiology Consultation & ECG',
      items: [
        { description: 'Cardiology Consultation', quantity: 1, unitPrice: 200.0, total: 200.0 },
        { description: 'ECG Test', quantity: 1, unitPrice: 150.0, total: 150.0 },
        { description: 'Lab Work', quantity: 1, unitPrice: 100.0, total: 100.0 },
      ],
    },
    {
      id: 'INV002',
      invoiceNumber: 'INV-2024-002',
      date: '2024-10-01',
      dueDate: '2024-10-15',
      amount: 280.0,
      amountPaid: 280.0,
      status: 'paid',
      description: 'Blood Work & Lab Tests',
      items: [
        { description: 'Complete Blood Count', quantity: 1, unitPrice: 80.0, total: 80.0 },
        { description: 'Lipid Panel', quantity: 1, unitPrice: 120.0, total: 120.0 },
        { description: 'Thyroid Panel', quantity: 1, unitPrice: 80.0, total: 80.0 },
      ],
    },
    {
      id: 'INV003',
      invoiceNumber: 'INV-2024-003',
      date: '2024-09-20',
      dueDate: '2024-10-05',
      amount: 320.0,
      amountPaid: 320.0,
      status: 'paid',
      description: 'Dental Cleaning',
      items: [
        { description: 'Dental Cleaning', quantity: 1, unitPrice: 150.0, total: 150.0 },
        { description: 'X-Ray', quantity: 1, unitPrice: 100.0, total: 100.0 },
        { description: 'Fluoride Treatment', quantity: 1, unitPrice: 70.0, total: 70.0 },
      ],
    },
  ]);

  const handleViewInvoice = (invoice: Invoice) => {
    setSelectedInvoice(invoice);
    setShowInvoiceDialog(true);
  };

  const handlePayInvoice = (invoice: Invoice) => {
    setSelectedInvoice(invoice);
    setPaymentAmount((invoice.amount - invoice.amountPaid).toFixed(2));
    setShowPaymentDialog(true);
  };

  const handleSubmitPayment = () => {
    // TODO: Process payment
    console.log('Payment submitted:', {
      invoice: selectedInvoice?.invoiceNumber,
      amount: paymentAmount,
      method: paymentMethod,
    });
    setShowPaymentDialog(false);
    setPaymentAmount('');
    setPaymentMethod('');
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
        return 'outline';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'paid':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-blue-600" />;
      case 'overdue':
        return <AlertCircle className="h-4 w-4 text-red-600" />;
      default:
        return <Clock className="h-4 w-4 text-gray-600" />;
    }
  };

  const filteredInvoices = invoices.filter((invoice) =>
    `${invoice.invoiceNumber} ${invoice.description}`.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const totalBalance = invoices.reduce((sum, inv) => sum + (inv.amount - inv.amountPaid), 0);
  const totalPaid = invoices.reduce((sum, inv) => sum + inv.amountPaid, 0);
  const pendingInvoices = invoices.filter(inv => inv.status === 'pending' || inv.status === 'overdue');
  const paidInvoices = invoices.filter(inv => inv.status === 'paid');

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar role="patient" />
        <main className="flex-1 ml-64 mt-16">
          <div className="p-8">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Billing & Payments</h1>
              <p className="text-gray-600">Manage your invoices and payment history</p>
            </div>

            {/* Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <Card className={totalBalance > 0 ? 'border-red-200' : ''}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Outstanding Balance
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className={`text-3xl font-bold ${totalBalance > 0 ? 'text-red-600' : 'text-gray-900'}`}>
                      ${totalBalance.toFixed(2)}
                    </p>
                    <div className={`h-12 w-12 ${totalBalance > 0 ? 'bg-red-100' : 'bg-green-100'} rounded-full flex items-center justify-center`}>
                      <DollarSign className={`h-6 w-6 ${totalBalance > 0 ? 'text-red-600' : 'text-green-600'}`} />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Total Paid
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">${totalPaid.toFixed(2)}</p>
                    <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center">
                      <CheckCircle className="h-6 w-6 text-green-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Pending Invoices
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">{pendingInvoices.length}</p>
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
            </div>

            {/* Outstanding Balance Alert */}
            {totalBalance > 0 && (
              <Card className="mb-6 border-red-200 bg-red-50">
                <CardContent className="pt-6">
                  <div className="flex items-start space-x-3">
                    <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
                    <div className="flex-1">
                      <h3 className="font-semibold text-red-900 mb-1">Payment Required</h3>
                      <p className="text-sm text-red-700 mb-3">
                        You have an outstanding balance of ${totalBalance.toFixed(2)}
                      </p>
                      <Button size="sm" onClick={() => pendingInvoices[0] && handlePayInvoice(pendingInvoices[0])}>
                        <CreditCard className="h-4 w-4 mr-1" />
                        Make Payment
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Search */}
            <Card className="mb-6">
              <CardContent className="pt-6">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    type="text"
                    placeholder="Search invoices..."
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
                <TabsTrigger value="all">All ({filteredInvoices.length})</TabsTrigger>
                <TabsTrigger value="pending">Pending ({pendingInvoices.length})</TabsTrigger>
                <TabsTrigger value="paid">Paid ({paidInvoices.length})</TabsTrigger>
              </TabsList>

              <TabsContent value="all">
                <div className="space-y-4">
                  {filteredInvoices.map((invoice) => (
                    <Card key={invoice.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="pt-6">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-3 mb-2">
                              <Badge variant={getStatusColor(invoice.status)}>
                                {invoice.status}
                              </Badge>
                              <span className="text-sm font-medium text-gray-600">
                                {invoice.invoiceNumber}
                              </span>
                            </div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">
                              {invoice.description}
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm text-gray-600 mb-3">
                              <div className="flex items-center space-x-1">
                                <Calendar className="h-4 w-4" />
                                <span>Date: {invoice.date}</span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <Calendar className="h-4 w-4" />
                                <span>Due: {invoice.dueDate}</span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <DollarSign className="h-4 w-4" />
                                <span>Amount: ${invoice.amount.toFixed(2)}</span>
                              </div>
                            </div>

                            {invoice.status !== 'paid' && (
                              <div className="p-3 bg-orange-50 rounded-lg">
                                <p className="text-sm font-medium text-orange-900">
                                  Balance Due: ${(invoice.amount - invoice.amountPaid).toFixed(2)}
                                </p>
                              </div>
                            )}

                            {invoice.status === 'paid' && (
                              <div className="p-3 bg-green-50 rounded-lg">
                                <div className="flex items-center space-x-2">
                                  <CheckCircle className="h-4 w-4 text-green-600" />
                                  <p className="text-sm font-medium text-green-900">
                                    Paid in Full - ${invoice.amountPaid.toFixed(2)}
                                  </p>
                                </div>
                              </div>
                            )}
                          </div>

                          <div className="flex flex-col space-y-2 ml-4">
                            <Button
                              size="sm"
                              onClick={() => handleViewInvoice(invoice)}
                            >
                              View Invoice
                            </Button>
                            {invoice.status !== 'paid' && (
                              <Button
                                size="sm"
                                variant="default"
                                className="bg-green-600 hover:bg-green-700"
                                onClick={() => handlePayInvoice(invoice)}
                              >
                                <CreditCard className="h-4 w-4 mr-1" />
                                Pay Now
                              </Button>
                            )}
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

              <TabsContent value="pending">
                <div className="space-y-4">
                  {pendingInvoices.map((invoice) => (
                    <Card key={invoice.id} className="border-orange-200">
                      <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <Badge variant={getStatusColor(invoice.status)} className="mb-2">
                              {invoice.status}
                            </Badge>
                            <h3 className="text-lg font-semibold mb-1">{invoice.description}</h3>
                            <p className="text-sm text-gray-600">Due: {invoice.dueDate}</p>
                            <p className="text-lg font-bold text-orange-600 mt-2">
                              ${(invoice.amount - invoice.amountPaid).toFixed(2)}
                            </p>
                          </div>
                          <Button onClick={() => handlePayInvoice(invoice)}>
                            <CreditCard className="h-4 w-4 mr-1" />
                            Pay Now
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="paid">
                <div className="space-y-4">
                  {paidInvoices.map((invoice) => (
                    <Card key={invoice.id}>
                      <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <Badge variant="default" className="mb-2">Paid</Badge>
                            <h3 className="text-lg font-semibold mb-1">{invoice.description}</h3>
                            <p className="text-sm text-gray-600">Paid on: {invoice.date}</p>
                            <p className="text-lg font-bold text-green-600 mt-2">
                              ${invoice.amountPaid.toFixed(2)}
                            </p>
                          </div>
                          <div className="flex flex-col space-y-2">
                            <Button size="sm" variant="outline" onClick={() => handleViewInvoice(invoice)}>
                              View Invoice
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
            </Tabs>
          </div>
        </main>
      </div>

      {/* Invoice Details Dialog */}
      <Dialog open={showInvoiceDialog} onOpenChange={setShowInvoiceDialog}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>Invoice Details</DialogTitle>
            <DialogDescription>
              {selectedInvoice?.invoiceNumber} - {selectedInvoice?.date}
            </DialogDescription>
          </DialogHeader>
          {selectedInvoice && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium text-gray-600">Invoice Number</Label>
                  <p className="text-sm mt-1">{selectedInvoice.invoiceNumber}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-600">Status</Label>
                  <Badge variant={getStatusColor(selectedInvoice.status)} className="mt-1">
                    {selectedInvoice.status}
                  </Badge>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-600">Invoice Date</Label>
                  <p className="text-sm mt-1">{selectedInvoice.date}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-600">Due Date</Label>
                  <p className="text-sm mt-1">{selectedInvoice.dueDate}</p>
                </div>
              </div>

              <div className="border rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Description</th>
                      <th className="px-4 py-2 text-center text-sm font-medium text-gray-700">Qty</th>
                      <th className="px-4 py-2 text-right text-sm font-medium text-gray-700">Unit Price</th>
                      <th className="px-4 py-2 text-right text-sm font-medium text-gray-700">Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedInvoice.items.map((item, index) => (
                      <tr key={index} className="border-t">
                        <td className="px-4 py-3 text-sm">{item.description}</td>
                        <td className="px-4 py-3 text-sm text-center">{item.quantity}</td>
                        <td className="px-4 py-3 text-sm text-right">${item.unitPrice.toFixed(2)}</td>
                        <td className="px-4 py-3 text-sm font-medium text-right">${item.total.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot className="border-t bg-gray-50">
                    <tr>
                      <td colSpan={3} className="px-4 py-3 text-sm font-bold text-right">Total Amount:</td>
                      <td className="px-4 py-3 text-sm font-bold text-right">${selectedInvoice.amount.toFixed(2)}</td>
                    </tr>
                    <tr>
                      <td colSpan={3} className="px-4 py-3 text-sm font-bold text-right">Amount Paid:</td>
                      <td className="px-4 py-3 text-sm font-bold text-right text-green-600">
                        -${selectedInvoice.amountPaid.toFixed(2)}
                      </td>
                    </tr>
                    <tr className="bg-gray-100">
                      <td colSpan={3} className="px-4 py-3 text-sm font-bold text-right">Balance Due:</td>
                      <td className="px-4 py-3 text-lg font-bold text-right text-orange-600">
                        ${(selectedInvoice.amount - selectedInvoice.amountPaid).toFixed(2)}
                      </td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowInvoiceDialog(false)}>
              Close
            </Button>
            <Button>
              <Download className="h-4 w-4 mr-2" />
              Download PDF
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Payment Dialog */}
      <Dialog open={showPaymentDialog} onOpenChange={setShowPaymentDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Make Payment</DialogTitle>
            <DialogDescription>
              Pay invoice {selectedInvoice?.invoiceNumber}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Invoice</Label>
              <p className="text-sm mt-1">{selectedInvoice?.invoiceNumber} - {selectedInvoice?.description}</p>
            </div>
            <div>
              <Label>Balance Due</Label>
              <p className="text-2xl font-bold text-orange-600 mt-1">
                ${selectedInvoice && (selectedInvoice.amount - selectedInvoice.amountPaid).toFixed(2)}
              </p>
            </div>
            <div>
              <Label htmlFor="paymentAmount">Payment Amount</Label>
              <Input
                id="paymentAmount"
                type="number"
                step="0.01"
                value={paymentAmount}
                onChange={(e) => setPaymentAmount(e.target.value)}
                placeholder="0.00"
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="paymentMethod">Payment Method</Label>
              <Select value={paymentMethod} onValueChange={setPaymentMethod}>
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Select payment method" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="credit_card">Credit Card</SelectItem>
                  <SelectItem value="debit_card">Debit Card</SelectItem>
                  <SelectItem value="bank_transfer">Bank Transfer</SelectItem>
                  <SelectItem value="insurance">Insurance</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPaymentDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleSubmitPayment} disabled={!paymentAmount || !paymentMethod}>
              <CreditCard className="h-4 w-4 mr-2" />
              Submit Payment
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
