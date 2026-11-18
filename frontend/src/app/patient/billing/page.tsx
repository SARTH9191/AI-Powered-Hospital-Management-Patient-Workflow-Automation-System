'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/hooks/useAuth';
import { billingAPI, type Invoice, type InvoiceItem } from '@/lib/api/billing';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
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
  DollarSign,
  Download,
  Search,
  Calendar,
  CreditCard,
  CheckCircle,
  XCircle,
  Clock,
  AlertCircle,
  FileText,
  Loader2,
} from 'lucide-react';
import { toast } from 'sonner';

export default function PatientBilling() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const patientId = 'patient001'; // TODO: Get from authenticated user

  // Fetch invoices
  const { data: invoicesData, isLoading } = useQuery({
    queryKey: ['invoices', patientId],
    queryFn: () => billingAPI.getPatientInvoices(patientId),
    enabled: !!patientId,
  });

  const invoices = invoicesData || [];

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null);
  const [showDetailsDialog, setShowDetailsDialog] = useState(false);
  const [showPaymentDialog, setShowPaymentDialog] = useState(false);
  const [paymentAmount, setPaymentAmount] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('card');

  // Payment mutation
  const paymentMutation = useMutation({
    mutationFn: (data: { invoice_id: string; amount: number; payment_method: string }) =>
      billingAPI.recordPayment({
        invoice_id: data.invoice_id,
        amount: data.amount,
        payment_method: data.payment_method,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
      toast.success('Payment processed successfully!');
      setShowPaymentDialog(false);
      setSelectedInvoice(null);
      setPaymentAmount('');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to process payment');
    },
  });

  // Filter invoices based on search
  const filteredInvoices = invoices.filter((invoice: Invoice) =>
    invoice.invoice_id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Categorize invoices
  const pendingInvoices = filteredInvoices.filter((inv: Invoice) => 
    inv.status === 'pending' || inv.status === 'partially_paid' || inv.status === 'overdue'
  );
  const paidInvoices = filteredInvoices.filter((inv: Invoice) => inv.status === 'paid');
  const allInvoices = filteredInvoices;

  // Calculate total balance
  const totalBalance = pendingInvoices.reduce((sum: number, inv: Invoice) => sum + inv.balance, 0);

  // Helper functions
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'paid':
        return 'default';
      case 'pending':
        return 'secondary';
      case 'partially_paid':
        return 'outline';
      case 'overdue':
        return 'destructive';
      case 'cancelled':
        return 'outline';
      default:
        return 'outline';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'paid':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-600" />;
      case 'partially_paid':
        return <AlertCircle className="h-4 w-4 text-blue-600" />;
      case 'overdue':
        return <XCircle className="h-4 w-4 text-red-600" />;
      default:
        return null;
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

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const handleViewDetails = (invoice: Invoice) => {
    setSelectedInvoice(invoice);
    setShowDetailsDialog(true);
  };

  const handleMakePayment = (invoice: Invoice) => {
    setSelectedInvoice(invoice);
    setPaymentAmount(invoice.balance.toString());
    setShowPaymentDialog(true);
  };

  const handleConfirmPayment = () => {
    if (!selectedInvoice || !paymentAmount) {
      toast.error('Please enter a payment amount');
      return;
    }

    const amount = parseFloat(paymentAmount);
    if (isNaN(amount) || amount <= 0) {
      toast.error('Please enter a valid amount');
      return;
    }

    if (amount > selectedInvoice.balance) {
      toast.error('Payment amount cannot exceed balance');
      return;
    }

    paymentMutation.mutate({
      invoice_id: selectedInvoice.invoice_id,
      amount,
      payment_method: paymentMethod,
    });
  };

  const handleDownloadInvoice = (invoice: Invoice) => {
    toast.info('Invoice download feature coming soon!');
    // TODO: Implement PDF download
  };

  const isOverdue = (invoice: Invoice) => {
    const dueDate = new Date(invoice.due_date);
    const today = new Date();
    return invoice.balance > 0 && dueDate < today;
  };

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
              <p className="text-gray-600">View invoices and manage payments</p>
            </div>

            {/* Statistics */}
            {isLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                {[1, 2, 3].map((i) => (
                  <Card key={i}>
                    <CardHeader className="pb-2">
                      <Skeleton className="h-4 w-20" />
                    </CardHeader>
                    <CardContent>
                      <Skeleton className="h-8 w-24" />
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-gray-600">
                      Outstanding Balance
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <p className="text-3xl font-bold text-gray-900">{formatCurrency(totalBalance)}</p>
                      <div className="h-12 w-12 bg-orange-100 rounded-full flex items-center justify-center">
                        <DollarSign className="h-6 w-6 text-orange-600" />
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
                      <div className="h-12 w-12 bg-yellow-100 rounded-full flex items-center justify-center">
                        <Clock className="h-6 w-6 text-yellow-600" />
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-gray-600">
                      Paid Invoices
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <p className="text-3xl font-bold text-gray-900">{paidInvoices.length}</p>
                      <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center">
                        <CheckCircle className="h-6 w-6 text-green-600" />
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
                  placeholder="Search invoices..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Tabs */}
            <Tabs defaultValue="all" className="space-y-6">
              <TabsList>
                <TabsTrigger value="all">All Invoices ({allInvoices.length})</TabsTrigger>
                <TabsTrigger value="pending">Pending ({pendingInvoices.length})</TabsTrigger>
                <TabsTrigger value="paid">Paid ({paidInvoices.length})</TabsTrigger>
              </TabsList>

              {/* All Invoices */}
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
                ) : allInvoices.length === 0 ? (
                  <Card>
                    <CardContent className="p-12 text-center">
                      <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">No invoices found</p>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="space-y-4">
                    {allInvoices.map((invoice: Invoice) => (
                      <Card key={invoice.invoice_id}>
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3 mb-3">
                                <h3 className="text-lg font-semibold text-gray-900">
                                  Invoice #{invoice.invoice_id}
                                </h3>
                                <Badge variant={getStatusColor(invoice.status)}>
                                  <div className="flex items-center space-x-1">
                                    {getStatusIcon(invoice.status)}
                                    <span className="capitalize">{invoice.status.replace('_', ' ')}</span>
                                  </div>
                                </Badge>
                                {isOverdue(invoice) && (
                                  <Badge variant="destructive">Overdue</Badge>
                                )}
                              </div>

                              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-3">
                                <div>
                                  <p className="text-gray-600 font-medium">Invoice Date</p>
                                  <div className="flex items-center text-gray-900">
                                    <Calendar className="h-4 w-4 mr-1" />
                                    {formatDate(invoice.invoice_date)}
                                  </div>
                                </div>
                                <div>
                                  <p className="text-gray-600 font-medium">Due Date</p>
                                  <div className="flex items-center text-gray-900">
                                    <Calendar className="h-4 w-4 mr-1" />
                                    {formatDate(invoice.due_date)}
                                  </div>
                                </div>
                                <div>
                                  <p className="text-gray-600 font-medium">Total Amount</p>
                                  <p className="text-gray-900 font-semibold">
                                    {formatCurrency(invoice.total_amount)}
                                  </p>
                                </div>
                                <div>
                                  <p className="text-gray-600 font-medium">Balance Due</p>
                                  <p className={`font-semibold ${invoice.balance > 0 ? 'text-orange-600' : 'text-green-600'}`}>
                                    {formatCurrency(invoice.balance)}
                                  </p>
                                </div>
                              </div>

                              {invoice.items && invoice.items.length > 0 && (
                                <div className="p-3 bg-gray-50 rounded-lg">
                                  <p className="text-sm font-medium text-gray-700 mb-2">
                                    Items ({invoice.items.length})
                                  </p>
                                  <div className="space-y-1">
                                    {invoice.items.slice(0, 2).map((item, idx) => (
                                      <p key={idx} className="text-sm text-gray-600">
                                        • {item.description} - {formatCurrency(item.amount)}
                                      </p>
                                    ))}
                                    {invoice.items.length > 2 && (
                                      <p className="text-sm text-gray-500 italic">
                                        +{invoice.items.length - 2} more items
                                      </p>
                                    )}
                                  </div>
                                </div>
                              )}
                            </div>

                            <div className="flex flex-col space-y-2 ml-4">
                              <Button
                                size="sm"
                                onClick={() => handleViewDetails(invoice)}
                              >
                                <FileText className="h-4 w-4 mr-2" />
                                View Details
                              </Button>
                              {invoice.balance > 0 && (
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => handleMakePayment(invoice)}
                                  disabled={paymentMutation.isPending}
                                >
                                  <CreditCard className="h-4 w-4 mr-2" />
                                  Pay Now
                                </Button>
                              )}
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleDownloadInvoice(invoice)}
                              >
                                <Download className="h-4 w-4 mr-2" />
                                Download
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </TabsContent>

              {/* Pending Invoices */}
              <TabsContent value="pending">
                {pendingInvoices.length === 0 ? (
                  <Card>
                    <CardContent className="p-12 text-center">
                      <CheckCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">No pending invoices</p>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="space-y-4">
                    {pendingInvoices.map((invoice: Invoice) => (
                      <Card key={invoice.invoice_id}>
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3 mb-3">
                                <h3 className="text-lg font-semibold text-gray-900">
                                  Invoice #{invoice.invoice_id}
                                </h3>
                                <Badge variant={getStatusColor(invoice.status)}>
                                  {invoice.status.replace('_', ' ')}
                                </Badge>
                                {isOverdue(invoice) && (
                                  <Badge variant="destructive">Overdue</Badge>
                                )}
                              </div>

                              <div className="grid grid-cols-3 gap-4 text-sm">
                                <div>
                                  <p className="text-gray-600">Due Date</p>
                                  <p className="text-gray-900">{formatDate(invoice.due_date)}</p>
                                </div>
                                <div>
                                  <p className="text-gray-600">Total Amount</p>
                                  <p className="text-gray-900 font-semibold">
                                    {formatCurrency(invoice.total_amount)}
                                  </p>
                                </div>
                                <div>
                                  <p className="text-gray-600">Balance Due</p>
                                  <p className="text-orange-600 font-semibold">
                                    {formatCurrency(invoice.balance)}
                                  </p>
                                </div>
                              </div>
                            </div>

                            <div className="flex flex-col space-y-2 ml-4">
                              <Button
                                size="sm"
                                onClick={() => handleMakePayment(invoice)}
                                disabled={paymentMutation.isPending}
                              >
                                <CreditCard className="h-4 w-4 mr-2" />
                                Pay Now
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleViewDetails(invoice)}
                              >
                                Details
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </TabsContent>

              {/* Paid Invoices */}
              <TabsContent value="paid">
                {paidInvoices.length === 0 ? (
                  <Card>
                    <CardContent className="p-12 text-center">
                      <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">No paid invoices</p>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="space-y-4">
                    {paidInvoices.map((invoice: Invoice) => (
                      <Card key={invoice.invoice_id}>
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3 mb-3">
                                <h3 className="text-lg font-semibold text-gray-900">
                                  Invoice #{invoice.invoice_id}
                                </h3>
                                <Badge variant="default">
                                  <CheckCircle className="h-4 w-4 mr-1" />
                                  Paid
                                </Badge>
                              </div>

                              <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                  <p className="text-gray-600">Invoice Date</p>
                                  <p className="text-gray-900">{formatDate(invoice.invoice_date)}</p>
                                </div>
                                <div>
                                  <p className="text-gray-600">Amount Paid</p>
                                  <p className="text-green-600 font-semibold">
                                    {formatCurrency(invoice.total_amount)}
                                  </p>
                                </div>
                              </div>
                            </div>

                            <div className="flex flex-col space-y-2 ml-4">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleViewDetails(invoice)}
                              >
                                <FileText className="h-4 w-4 mr-2" />
                                View Details
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleDownloadInvoice(invoice)}
                              >
                                <Download className="h-4 w-4 mr-2" />
                                Download
                              </Button>
                            </div>
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

      {/* Invoice Details Dialog */}
      <Dialog open={showDetailsDialog} onOpenChange={setShowDetailsDialog}>
        <DialogContent className="sm:max-w-[700px]">
          <DialogHeader>
            <DialogTitle>Invoice Details</DialogTitle>
            <DialogDescription>
              Invoice #{selectedInvoice?.invoice_id}
            </DialogDescription>
          </DialogHeader>
          {selectedInvoice && (
            <div className="py-4">
              <div className="grid gap-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Invoice Date</p>
                    <p className="text-sm text-gray-900">{formatDate(selectedInvoice.invoice_date)}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">Due Date</p>
                    <p className="text-sm text-gray-900">{formatDate(selectedInvoice.due_date)}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">Status</p>
                    <Badge variant={getStatusColor(selectedInvoice.status)}>
                      {selectedInvoice.status.replace('_', ' ')}
                    </Badge>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">Patient</p>
                    <p className="text-sm text-gray-900">{selectedInvoice.patient_name || selectedInvoice.patient_id}</p>
                  </div>
                </div>

                <div className="border-t pt-4">
                  <h4 className="font-medium text-gray-900 mb-3">Invoice Items</h4>
                  <div className="space-y-2">
                    {selectedInvoice.items.map((item, idx) => (
                      <div key={idx} className="flex justify-between items-start p-3 bg-gray-50 rounded-lg">
                        <div className="flex-1">
                          <p className="text-sm font-medium text-gray-900">{item.description}</p>
                          <p className="text-xs text-gray-600">
                            Qty: {item.quantity} × {formatCurrency(item.unit_price)}
                          </p>
                        </div>
                        <p className="text-sm font-semibold text-gray-900">
                          {formatCurrency(item.amount)}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="border-t pt-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Subtotal</span>
                      <span className="text-gray-900">{formatCurrency(selectedInvoice.total_amount)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Amount Paid</span>
                      <span className="text-green-600">{formatCurrency(selectedInvoice.amount_paid)}</span>
                    </div>
                    <div className="flex justify-between text-base font-semibold pt-2 border-t">
                      <span>Balance Due</span>
                      <span className={selectedInvoice.balance > 0 ? 'text-orange-600' : 'text-green-600'}>
                        {formatCurrency(selectedInvoice.balance)}
                      </span>
                    </div>
                  </div>
                </div>

                {selectedInvoice.notes && (
                  <div className="border-t pt-4">
                    <p className="text-sm font-medium text-gray-600 mb-1">Notes</p>
                    <p className="text-sm text-gray-700">{selectedInvoice.notes}</p>
                  </div>
                )}
              </div>
            </div>
          )}
          <div className="flex justify-end space-x-2">
            <Button
              variant="outline"
              onClick={() => setShowDetailsDialog(false)}
            >
              Close
            </Button>
            {selectedInvoice && selectedInvoice.balance > 0 && (
              <Button onClick={() => {
                setShowDetailsDialog(false);
                handleMakePayment(selectedInvoice);
              }}>
                <CreditCard className="h-4 w-4 mr-2" />
                Make Payment
              </Button>
            )}
            {selectedInvoice && (
              <Button
                variant="outline"
                onClick={() => handleDownloadInvoice(selectedInvoice)}
              >
                <Download className="h-4 w-4 mr-2" />
                Download PDF
              </Button>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Payment Dialog */}
      <Dialog open={showPaymentDialog} onOpenChange={setShowPaymentDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Make Payment</DialogTitle>
            <DialogDescription>
              Pay invoice #{selectedInvoice?.invoice_id}
            </DialogDescription>
          </DialogHeader>
          {selectedInvoice && (
            <div className="py-4">
              <div className="space-y-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex justify-between mb-2">
                    <span className="text-sm text-gray-600">Total Amount</span>
                    <span className="text-sm font-semibold">{formatCurrency(selectedInvoice.total_amount)}</span>
                  </div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm text-gray-600">Amount Paid</span>
                    <span className="text-sm text-green-600">{formatCurrency(selectedInvoice.amount_paid)}</span>
                  </div>
                  <div className="flex justify-between pt-2 border-t">
                    <span className="font-medium">Balance Due</span>
                    <span className="font-semibold text-orange-600">{formatCurrency(selectedInvoice.balance)}</span>
                  </div>
                </div>

                <div>
                  <Label htmlFor="amount">Payment Amount</Label>
                  <Input
                    id="amount"
                    type="number"
                    value={paymentAmount}
                    onChange={(e) => setPaymentAmount(e.target.value)}
                    placeholder="0.00"
                    min="0"
                    max={selectedInvoice.balance}
                    step="0.01"
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label htmlFor="payment-method">Payment Method</Label>
                  <Select value={paymentMethod} onValueChange={setPaymentMethod}>
                    <SelectTrigger className="mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="card">Credit/Debit Card</SelectItem>
                      <SelectItem value="bank_transfer">Bank Transfer</SelectItem>
                      <SelectItem value="cash">Cash</SelectItem>
                      <SelectItem value="check">Check</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setShowPaymentDialog(false);
                setPaymentAmount('');
              }}
              disabled={paymentMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              onClick={handleConfirmPayment}
              disabled={paymentMutation.isPending}
            >
              {paymentMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <CreditCard className="mr-2 h-4 w-4" />
                  Pay {paymentAmount && formatCurrency(parseFloat(paymentAmount))}
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
