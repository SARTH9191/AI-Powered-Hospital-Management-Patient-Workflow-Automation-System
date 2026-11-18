"use client";

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogFooter, 
  DialogHeader, 
  DialogTitle 
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { CheckCircle2, XCircle, AlertCircle, Clock, Eye } from "lucide-react";
import { apiClient } from '@/lib/api-client';
import { useToast } from "@/hooks/use-toast";

interface ApprovalRequest {
  id: number;
  request_type: string;
  description: string;
  requested_by: string;
  requested_at: string;
  priority: 'Low' | 'Normal' | 'High' | 'Critical';
  status: 'pending' | 'approved' | 'rejected';
  patient_id?: number;
  patient_name?: string;
  action_details: {
    action: string;
    reasoning: string;
    estimated_cost?: number;
    alternative_options?: string[];
  };
  metadata?: Record<string, any>;
}

interface ApprovalQueueCardProps {
  maxItems?: number;
  autoRefresh?: boolean;
  showStats?: boolean;
}

export function ApprovalQueueCard({ 
  maxItems = 5, 
  autoRefresh = true,
  showStats = true 
}: ApprovalQueueCardProps) {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [selectedApproval, setSelectedApproval] = useState<ApprovalRequest | null>(null);
  const [showDetailsDialog, setShowDetailsDialog] = useState(false);
  const [showApproveDialog, setShowApproveDialog] = useState(false);
  const [showRejectDialog, setShowRejectDialog] = useState(false);
  const [rejectionReason, setRejectionReason] = useState("");

  // Fetch pending approvals
  const { data: approvals, isLoading } = useQuery<ApprovalRequest[]>({
    queryKey: ['approvals', 'pending'],
    queryFn: async () => {
      const response = await apiClient.get('/api/approvals/pending');
      return response.data.slice(0, maxItems);
    },
    refetchInterval: autoRefresh ? 10000 : false // Refresh every 10 seconds
  });

  // Approve mutation
  const approveMutation = useMutation({
    mutationFn: async (approvalId: number) => {
      const response = await apiClient.post(`/api/approvals/process`, {
        approval_id: approvalId,
        action: 'approve',
        notes: 'Approved by staff'
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['approvals'] });
      toast({
        title: "Approval Confirmed",
        description: "The request has been approved and will be executed.",
        variant: "default"
      });
      setShowApproveDialog(false);
      setSelectedApproval(null);
    },
    onError: (error: any) => {
      toast({
        title: "Approval Failed",
        description: error.message || "Failed to approve request",
        variant: "destructive"
      });
    }
  });

  // Reject mutation
  const rejectMutation = useMutation({
    mutationFn: async ({ approvalId, reason }: { approvalId: number; reason: string }) => {
      const response = await apiClient.post(`/api/approvals/process`, {
        approval_id: approvalId,
        action: 'reject',
        notes: reason
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['approvals'] });
      toast({
        title: "Request Rejected",
        description: "The request has been rejected.",
        variant: "default"
      });
      setShowRejectDialog(false);
      setSelectedApproval(null);
      setRejectionReason("");
    },
    onError: (error: any) => {
      toast({
        title: "Rejection Failed",
        description: error.message || "Failed to reject request",
        variant: "destructive"
      });
    }
  });

  const getPriorityBadge = (priority: string) => {
    const variants: Record<string, string> = {
      Low: "bg-gray-500",
      Normal: "bg-blue-500",
      High: "bg-orange-500",
      Critical: "bg-red-500 animate-pulse"
    };
    return <Badge className={`${variants[priority] || variants.Normal} text-white`}>{priority}</Badge>;
  };

  const handleViewDetails = (approval: ApprovalRequest) => {
    setSelectedApproval(approval);
    setShowDetailsDialog(true);
  };

  const handleApprove = (approval: ApprovalRequest) => {
    setSelectedApproval(approval);
    setShowApproveDialog(true);
  };

  const handleReject = (approval: ApprovalRequest) => {
    setSelectedApproval(approval);
    setShowRejectDialog(true);
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-64 mt-2" />
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3].map(i => (
              <Skeleton key={i} className="h-24 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const pendingCount = approvals?.length || 0;
  const criticalCount = approvals?.filter(a => a.priority === 'Critical').length || 0;

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <AlertCircle className="h-5 w-5 text-orange-500" />
                AI Approval Queue
              </CardTitle>
              <CardDescription>
                Review and approve AI-generated requests
              </CardDescription>
            </div>
            {pendingCount > 0 && (
              <Badge className="bg-orange-500 text-white text-lg px-3 py-1">
                {pendingCount}
              </Badge>
            )}
          </div>

          {showStats && pendingCount > 0 && (
            <div className="flex gap-4 mt-4 text-sm">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-gray-500" />
                <span className="text-gray-600">{pendingCount} Pending</span>
              </div>
              {criticalCount > 0 && (
                <div className="flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 text-red-500" />
                  <span className="text-red-600 font-medium">{criticalCount} Critical</span>
                </div>
              )}
            </div>
          )}
        </CardHeader>

        <CardContent>
          {pendingCount === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <CheckCircle2 className="h-12 w-12 mx-auto mb-2 text-green-500" />
              <p>All caught up! No pending approvals.</p>
            </div>
          ) : (
            <ScrollArea className="h-[400px] pr-4">
              <div className="space-y-3">
                {approvals?.map((approval) => (
                  <div
                    key={approval.id}
                    className={`border rounded-lg p-4 transition-all hover:shadow-md ${
                      approval.priority === 'Critical' ? 'border-red-300 bg-red-50' :
                      approval.priority === 'High' ? 'border-orange-300 bg-orange-50' :
                      'border-gray-200'
                    }`}
                  >
                    {/* Header */}
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-semibold text-gray-900">
                            {approval.request_type}
                          </h4>
                          {getPriorityBadge(approval.priority)}
                        </div>
                        {approval.patient_name && (
                          <p className="text-sm text-gray-600">
                            Patient: {approval.patient_name} (ID: {approval.patient_id})
                          </p>
                        )}
                      </div>
                    </div>

                    {/* Description */}
                    <p className="text-sm text-gray-700 mb-3">
                      {approval.description}
                    </p>

                    {/* AI Reasoning Preview */}
                    <div className="bg-blue-50 border border-blue-200 rounded p-2 mb-3">
                      <p className="text-xs font-medium text-blue-900 mb-1">AI Reasoning:</p>
                      <p className="text-xs text-blue-800">
                        {approval.action_details.reasoning.substring(0, 150)}
                        {approval.action_details.reasoning.length > 150 && '...'}
                      </p>
                    </div>

                    {/* Cost if applicable */}
                    {approval.action_details.estimated_cost && (
                      <p className="text-sm font-medium text-gray-900 mb-3">
                        Estimated Cost: ${approval.action_details.estimated_cost.toFixed(2)}
                      </p>
                    )}

                    {/* Metadata */}
                    <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                      <span>Requested by: {approval.requested_by}</span>
                      <span>{new Date(approval.requested_at).toLocaleString()}</span>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleViewDetails(approval)}
                        className="flex-1"
                      >
                        <Eye className="h-4 w-4 mr-1" />
                        Details
                      </Button>
                      <Button
                        size="sm"
                        variant="default"
                        onClick={() => handleApprove(approval)}
                        className="flex-1 bg-green-500 hover:bg-green-600"
                      >
                        <CheckCircle2 className="h-4 w-4 mr-1" />
                        Approve
                      </Button>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => handleReject(approval)}
                        className="flex-1"
                      >
                        <XCircle className="h-4 w-4 mr-1" />
                        Reject
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          )}
        </CardContent>
      </Card>

      {/* Details Dialog */}
      <Dialog open={showDetailsDialog} onOpenChange={setShowDetailsDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Approval Request Details</DialogTitle>
            <DialogDescription>
              Review the complete details of this AI-generated request
            </DialogDescription>
          </DialogHeader>
          {selectedApproval && (
            <div className="space-y-4">
              <div>
                <h4 className="font-semibold mb-2">Request Type</h4>
                <p>{selectedApproval.request_type}</p>
              </div>
              <div>
                <h4 className="font-semibold mb-2">Description</h4>
                <p>{selectedApproval.description}</p>
              </div>
              <div>
                <h4 className="font-semibold mb-2">AI Reasoning</h4>
                <p className="text-sm bg-blue-50 p-3 rounded">
                  {selectedApproval.action_details.reasoning}
                </p>
              </div>
              {selectedApproval.action_details.alternative_options && (
                <div>
                  <h4 className="font-semibold mb-2">Alternative Options</h4>
                  <ul className="list-disc list-inside text-sm space-y-1">
                    {selectedApproval.action_details.alternative_options.map((option, i) => (
                      <li key={i}>{option}</li>
                    ))}
                  </ul>
                </div>
              )}
              {selectedApproval.action_details.estimated_cost && (
                <div>
                  <h4 className="font-semibold mb-2">Estimated Cost</h4>
                  <p className="text-lg font-bold">
                    ${selectedApproval.action_details.estimated_cost.toFixed(2)}
                  </p>
                </div>
              )}
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDetailsDialog(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Approve Confirmation Dialog */}
      <Dialog open={showApproveDialog} onOpenChange={setShowApproveDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirm Approval</DialogTitle>
            <DialogDescription>
              Are you sure you want to approve this request? The AI agent will execute this action immediately.
            </DialogDescription>
          </DialogHeader>
          {selectedApproval && (
            <div className="py-4">
              <p className="font-medium">{selectedApproval.request_type}</p>
              <p className="text-sm text-gray-600 mt-1">{selectedApproval.description}</p>
              {selectedApproval.action_details.estimated_cost && (
                <p className="text-lg font-bold mt-2">
                  Cost: ${selectedApproval.action_details.estimated_cost.toFixed(2)}
                </p>
              )}
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowApproveDialog(false)}>
              Cancel
            </Button>
            <Button
              className="bg-green-500 hover:bg-green-600"
              onClick={() => selectedApproval && approveMutation.mutate(selectedApproval.id)}
              disabled={approveMutation.isPending}
            >
              {approveMutation.isPending ? "Approving..." : "Confirm Approval"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Reject Confirmation Dialog */}
      <Dialog open={showRejectDialog} onOpenChange={setShowRejectDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reject Request</DialogTitle>
            <DialogDescription>
              Please provide a reason for rejecting this request.
            </DialogDescription>
          </DialogHeader>
          {selectedApproval && (
            <div className="space-y-4">
              <div>
                <p className="font-medium">{selectedApproval.request_type}</p>
                <p className="text-sm text-gray-600 mt-1">{selectedApproval.description}</p>
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Rejection Reason</label>
                <Textarea
                  placeholder="Enter reason for rejection..."
                  value={rejectionReason}
                  onChange={(e) => setRejectionReason(e.target.value)}
                  rows={4}
                />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowRejectDialog(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => selectedApproval && rejectMutation.mutate({
                approvalId: selectedApproval.id,
                reason: rejectionReason
              })}
              disabled={rejectMutation.isPending || !rejectionReason.trim()}
            >
              {rejectMutation.isPending ? "Rejecting..." : "Confirm Rejection"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
