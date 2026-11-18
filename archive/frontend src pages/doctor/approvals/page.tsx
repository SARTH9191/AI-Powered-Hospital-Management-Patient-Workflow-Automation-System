'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
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
  ClipboardCheck,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  Pill,
  TestTube,
  FileText,
  Edit,
} from 'lucide-react';
import { toast } from 'sonner';
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';

interface Approval {
  id: string;
  type: 'prescription' | 'lab_test' | 'procedure' | 'referral';
  patient: string;
  patientId: string;
  item: string;
  details: string;
  priority: 'normal' | 'urgent' | 'emergency';
  requestedBy: string;
  requestedAt: string;
  estimatedCost?: number;
}

export default function ApprovalsPage() {
  const [pendingApprovals, setPendingApprovals] = useState<Approval[]>([]);
  const [approvedItems, setApprovedItems] = useState<Approval[]>([]);
  const [rejectedItems, setRejectedItems] = useState<Approval[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingApproval, setEditingApproval] = useState<Approval | null>(null);
  const [editForm, setEditForm] = useState({
    item: '',
    details: '',
    estimatedCost: 0,
  });

  useEffect(() => {
    // Mock data - replace with real API call
    const mockPending: Approval[] = [
      {
        id: '1',
        type: 'prescription',
        patient: 'Emily Davis',
        patientId: 'P1234',
        item: 'Amoxicillin 500mg',
        details: '14 days supply, 3 times daily with meals',
        priority: 'normal',
        requestedBy: 'System',
        requestedAt: '2024-10-18T09:15:00',
        estimatedCost: 45,
      },
      {
        id: '2',
        type: 'lab_test',
        patient: 'James Wilson',
        patientId: 'P1235',
        item: 'Complete Blood Count (CBC)',
        details: 'Follow-up test for anemia treatment',
        priority: 'urgent',
        requestedBy: 'Dr. Smith',
        requestedAt: '2024-10-18T08:30:00',
        estimatedCost: 85,
      },
      {
        id: '3',
        type: 'procedure',
        patient: 'Patricia Martinez',
        patientId: 'P1236',
        item: 'Chest X-Ray',
        details: 'Suspected pneumonia, requires immediate attention',
        priority: 'emergency',
        requestedBy: 'ER Team',
        requestedAt: '2024-10-18T07:45:00',
        estimatedCost: 250,
      },
      {
        id: '4',
        type: 'prescription',
        patient: 'David Anderson',
        patientId: 'P1237',
        item: 'Ibuprofen 400mg',
        details: '7 days supply for pain management',
        priority: 'normal',
        requestedBy: 'System',
        requestedAt: '2024-10-18T06:20:00',
        estimatedCost: 25,
      },
      {
        id: '5',
        type: 'referral',
        patient: 'Linda Taylor',
        patientId: 'P1238',
        item: 'Cardiologist Referral',
        details: 'Abnormal ECG results, needs specialist consultation',
        priority: 'urgent',
        requestedBy: 'Dr. Johnson',
        requestedAt: '2024-10-18T05:00:00',
        estimatedCost: 350,
      },
    ];

    setTimeout(() => {
      setPendingApprovals(mockPending);
      setIsLoading(false);
    }, 500);
  }, []);

  const handleEdit = (approval: Approval) => {
    setEditingApproval(approval);
    setEditForm({
      item: approval.item,
      details: approval.details,
      estimatedCost: approval.estimatedCost || 0,
    });
    setIsEditDialogOpen(true);
  };

  const handleSaveAndApprove = () => {
    if (!editingApproval) return;

    const updatedApproval = {
      ...editingApproval,
      item: editForm.item,
      details: editForm.details,
      estimatedCost: editForm.estimatedCost,
      requestedAt: new Date().toISOString(),
    };

    setPendingApprovals(pendingApprovals.filter((a) => a.id !== editingApproval.id));
    setApprovedItems([...approvedItems, updatedApproval]);
    
    toast.success(`Modified and approved: ${editForm.item}`, {
      description: `Changes saved for ${editingApproval.patient}`,
    });

    setIsEditDialogOpen(false);
    setEditingApproval(null);
  };

  const handleApprove = (approval: Approval) => {
    setPendingApprovals(pendingApprovals.filter((a) => a.id !== approval.id));
    setApprovedItems([...approvedItems, { ...approval, requestedAt: new Date().toISOString() }]);
    toast.success(`${approval.item} approved for ${approval.patient}`);
  };

  const handleReject = (approval: Approval) => {
    setPendingApprovals(pendingApprovals.filter((a) => a.id !== approval.id));
    setRejectedItems([...rejectedItems, { ...approval, requestedAt: new Date().toISOString() }]);
    toast.error(`${approval.item} rejected for ${approval.patient}`);
  };

  const getTypeIcon = (type: Approval['type']) => {
    switch (type) {
      case 'prescription':
        return <Pill className="h-5 w-5 text-purple-600" />;
      case 'lab_test':
        return <TestTube className="h-5 w-5 text-blue-600" />;
      case 'procedure':
        return <FileText className="h-5 w-5 text-green-600" />;
      case 'referral':
        return <ClipboardCheck className="h-5 w-5 text-orange-600" />;
    }
  };

  const getPriorityBadge = (priority: Approval['priority']) => {
    switch (priority) {
      case 'normal':
        return <Badge variant="secondary">Normal</Badge>;
      case 'urgent':
        return <Badge variant="default" className="bg-orange-500">Urgent</Badge>;
      case 'emergency':
        return <Badge variant="destructive">Emergency</Badge>;
    }
  };

  const getTimeAgo = (dateString: string) => {
    const now = new Date();
    const date = new Date(dateString);
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));

    if (diffInMinutes < 60) return `${diffInMinutes} minutes ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)} hours ago`;
    return `${Math.floor(diffInMinutes / 1440)} days ago`;
  };

  const ApprovalCard = ({ approval, showActions = true }: { approval: Approval; showActions?: boolean }) => (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="pt-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-start space-x-3">
            <div className="h-10 w-10 bg-gray-100 rounded-full flex items-center justify-center">
              {getTypeIcon(approval.type)}
            </div>
            <div>
              <div className="flex items-center space-x-2 mb-1">
                <Badge variant="outline" className="text-xs capitalize">
                  {approval.type.replace('_', ' ')}
                </Badge>
                {getPriorityBadge(approval.priority)}
              </div>
              <h3 className="font-semibold text-gray-900 text-lg">{approval.item}</h3>
            </div>
          </div>
          {approval.estimatedCost && (
            <div className="text-right">
              <p className="text-sm text-gray-500">Est. Cost</p>
              <p className="text-lg font-bold text-gray-900">${approval.estimatedCost}</p>
            </div>
          )}
        </div>

        <div className="space-y-2 mb-4">
          <div className="flex items-center space-x-2">
            <Avatar className="h-6 w-6">
              <AvatarFallback className="text-xs bg-blue-100 text-blue-600">
                {approval.patient.split(' ').map((n) => n[0]).join('')}
              </AvatarFallback>
            </Avatar>
            <div>
              <p className="text-sm font-medium text-gray-900">{approval.patient}</p>
              <p className="text-xs text-gray-500">Patient ID: {approval.patientId}</p>
            </div>
          </div>

          <p className="text-sm text-gray-600 pl-8">{approval.details}</p>

          <div className="flex items-center space-x-4 text-xs text-gray-500 pl-8">
            <span className="flex items-center">
              <Clock className="h-3 w-3 mr-1" />
              {getTimeAgo(approval.requestedAt)}
            </span>
            <span>Requested by: {approval.requestedBy}</span>
          </div>
        </div>

        {showActions && (
          <div className="space-y-2">
            <Button
              onClick={() => handleEdit(approval)}
              className="w-full"
              variant="secondary"
            >
              <Edit className="h-4 w-4 mr-2" />
              Edit & Approve
            </Button>
            <div className="flex space-x-2">
              <Button
                onClick={() => handleApprove(approval)}
                className="flex-1"
                variant="default"
              >
                <CheckCircle className="h-4 w-4 mr-2" />
                Approve
              </Button>
              <Button
                onClick={() => handleReject(approval)}
                className="flex-1"
                variant="outline"
              >
                <XCircle className="h-4 w-4 mr-2" />
                Reject
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar role="doctor" />
        <main className="flex-1 ml-64 mt-16">
          <div className="p-8">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Approval Queue</h1>
              <p className="text-gray-600">Review and approve pending medical requests</p>
            </div>

            {/* Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Pending Approvals
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">{pendingApprovals.length}</p>
                    <div className="h-12 w-12 bg-orange-100 rounded-full flex items-center justify-center">
                      <Clock className="h-6 w-6 text-orange-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Approved Today
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">{approvedItems.length}</p>
                    <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center">
                      <CheckCircle className="h-6 w-6 text-green-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Emergency Cases
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <p className="text-3xl font-bold text-gray-900">
                      {pendingApprovals.filter((a) => a.priority === 'emergency').length}
                    </p>
                    <div className="h-12 w-12 bg-red-100 rounded-full flex items-center justify-center">
                      <AlertTriangle className="h-6 w-6 text-red-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Tabs */}
            <Tabs defaultValue="pending" className="space-y-6">
              <TabsList>
                <TabsTrigger value="pending">
                  Pending ({pendingApprovals.length})
                </TabsTrigger>
                <TabsTrigger value="approved">
                  Approved ({approvedItems.length})
                </TabsTrigger>
                <TabsTrigger value="rejected">
                  Rejected ({rejectedItems.length})
                </TabsTrigger>
              </TabsList>

              <TabsContent value="pending" className="space-y-4">
                {isLoading ? (
                  <Card>
                    <CardContent className="py-8 text-center text-gray-500">
                      Loading approvals...
                    </CardContent>
                  </Card>
                ) : pendingApprovals.length === 0 ? (
                  <Card>
                    <CardContent className="py-8 text-center text-gray-500">
                      No pending approvals. Great job! 🎉
                    </CardContent>
                  </Card>
                ) : (
                  pendingApprovals.map((approval) => (
                    <ApprovalCard key={approval.id} approval={approval} />
                  ))
                )}
              </TabsContent>

              <TabsContent value="approved" className="space-y-4">
                {approvedItems.length === 0 ? (
                  <Card>
                    <CardContent className="py-8 text-center text-gray-500">
                      No approved items yet.
                    </CardContent>
                  </Card>
                ) : (
                  approvedItems.map((approval) => (
                    <ApprovalCard key={approval.id} approval={approval} showActions={false} />
                  ))
                )}
              </TabsContent>

              <TabsContent value="rejected" className="space-y-4">
                {rejectedItems.length === 0 ? (
                  <Card>
                    <CardContent className="py-8 text-center text-gray-500">
                      No rejected items.
                    </CardContent>
                  </Card>
                ) : (
                  rejectedItems.map((approval) => (
                    <ApprovalCard key={approval.id} approval={approval} showActions={false} />
                  ))
                )}
              </TabsContent>
            </Tabs>

            {/* Edit Dialog */}
            <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
              <DialogContent className="max-w-md">
                <DialogHeader>
                  <DialogTitle>Edit & Approve Request</DialogTitle>
                  <DialogDescription>
                    Modify the request details before approving for {editingApproval?.patient}
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="edit-item">Item/Medication Name</Label>
                    <Input
                      id="edit-item"
                      value={editForm.item}
                      onChange={(e) => setEditForm({ ...editForm, item: e.target.value })}
                      placeholder="e.g., Amoxicillin 500mg"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="edit-details">Details/Instructions</Label>
                    <Textarea
                      id="edit-details"
                      value={editForm.details}
                      onChange={(e) => setEditForm({ ...editForm, details: e.target.value })}
                      placeholder="e.g., 14 days supply, 3 times daily with meals"
                      rows={4}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="edit-cost">Estimated Cost ($)</Label>
                    <Input
                      id="edit-cost"
                      type="number"
                      value={editForm.estimatedCost}
                      onChange={(e) => setEditForm({ ...editForm, estimatedCost: Number(e.target.value) })}
                      placeholder="0"
                    />
                  </div>
                  <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <p className="text-sm text-yellow-800">
                      <strong>Note:</strong> Modifications will be saved and the request will be approved with updated details.
                    </p>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleSaveAndApprove} className="bg-green-600 hover:bg-green-700">
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Save & Approve
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </main>
      </div>
    </div>
  );
}
