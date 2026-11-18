"use client";

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { CheckCircle2, Circle, Clock, AlertCircle } from "lucide-react";
import { apiClient } from '@/lib/api-client';

interface WorkflowStage {
  stage_name: string;
  status: 'completed' | 'in_progress' | 'pending' | 'failed';
  started_at?: string;
  completed_at?: string;
  notes?: string;
}

interface WorkflowState {
  patient_id: number;
  patient_name: string;
  current_stage: string;
  workflow_status: 'active' | 'completed' | 'paused' | 'failed';
  stages: WorkflowStage[];
  started_at: string;
  updated_at: string;
}

interface WorkflowProgressWidgetProps {
  patientId: number;
  showDetails?: boolean;
}

const WORKFLOW_STAGES = [
  { name: "Registration", description: "Patient registration & data collection" },
  { name: "Document Upload", description: "Upload required medical documents" },
  { name: "Medical History", description: "Collect medical history & allergies" },
  { name: "Doctor Approval", description: "Doctor approval & lab test recommendation" },
  { name: "Lab Coordination", description: "Schedule and coordinate lab tests" },
  { name: "Results Analysis", description: "Analyze test results automatically" },
  { name: "Admission Planning", description: "Plan hospital admission if needed" },
  { name: "Treatment & Monitoring", description: "Monitor treatment progress with real-time updates" },
  { name: "Discharge Planning", description: "Process discharge & billing" },
  { name: "Medication Management", description: "Manage discharge medications with safety checks" },
  { name: "Follow-up Care", description: "Schedule follow-up appointments" },
  { name: "Journey Completion", description: "Complete healthcare journey with WhatsApp congratulations" }
];

export function WorkflowProgressWidget({ patientId, showDetails = true }: WorkflowProgressWidgetProps) {
  const { data: workflowState, isLoading, error } = useQuery<WorkflowState>({
    queryKey: ['workflow-state', patientId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/workflow/state/${patientId}`);
      return response.data;
    },
    refetchInterval: 5000, // Refresh every 5 seconds for real-time updates
    enabled: !!patientId
  });

  const getStageStatus = (stageName: string): WorkflowStage['status'] => {
    if (!workflowState?.stages) return 'pending';
    const stage = workflowState.stages.find(s => s.stage_name === stageName);
    return stage?.status || 'pending';
  };

  const getStageIcon = (status: WorkflowStage['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'in_progress':
        return <Clock className="h-5 w-5 text-blue-500 animate-pulse" />;
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Circle className="h-5 w-5 text-gray-300" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { color: string; text: string }> = {
      active: { color: "bg-blue-500", text: "In Progress" },
      completed: { color: "bg-green-500", text: "Completed" },
      paused: { color: "bg-yellow-500", text: "Paused" },
      failed: { color: "bg-red-500", text: "Failed" }
    };
    
    const variant = variants[status] || variants.active;
    return (
      <Badge className={`${variant.color} text-white`}>
        {variant.text}
      </Badge>
    );
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-64 mt-2" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3, 4, 5].map(i => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-red-500">Workflow Not Found</CardTitle>
          <CardDescription>
            No active workflow found for this patient. Start a new workflow to begin.
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  if (!workflowState) {
    return null;
  }

  const completedStages = workflowState.stages?.filter(s => s.status === 'completed').length || 0;
  const totalStages = WORKFLOW_STAGES.length;
  const progressPercentage = (completedStages / totalStages) * 100;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Patient Workflow Progress</CardTitle>
            <CardDescription>
              {workflowState.patient_name} - Current Stage: {workflowState.current_stage}
            </CardDescription>
          </div>
          {getStatusBadge(workflowState.workflow_status)}
        </div>
        
        {/* Progress Bar */}
        <div className="mt-4">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>{completedStages} of {totalStages} stages completed</span>
            <span>{Math.round(progressPercentage)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div 
              className="bg-blue-500 h-2.5 rounded-full transition-all duration-500"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        </div>
      </CardHeader>

      {showDetails && (
        <CardContent>
          <div className="space-y-3">
            {WORKFLOW_STAGES.map((stage, index) => {
              const status = getStageStatus(stage.name);
              const stageData = workflowState.stages?.find(s => s.stage_name === stage.name);
              
              return (
                <div
                  key={stage.name}
                  className={`flex items-start space-x-3 p-3 rounded-lg transition-colors ${
                    status === 'in_progress' ? 'bg-blue-50 border border-blue-200' :
                    status === 'completed' ? 'bg-green-50' :
                    status === 'failed' ? 'bg-red-50' :
                    'bg-gray-50'
                  }`}
                >
                  {/* Stage Icon */}
                  <div className="flex-shrink-0 mt-0.5">
                    {getStageIcon(status)}
                  </div>

                  {/* Stage Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="font-medium text-gray-900">
                        {index + 1}. {stage.name}
                      </p>
                      {status === 'in_progress' && (
                        <Badge variant="outline" className="ml-2">
                          Current
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mt-0.5">
                      {stage.description}
                    </p>
                    
                    {/* Stage Notes */}
                    {stageData?.notes && (
                      <p className="text-xs text-gray-500 mt-1 italic">
                        Note: {stageData.notes}
                      </p>
                    )}

                    {/* Timestamps */}
                    {stageData?.completed_at && (
                      <p className="text-xs text-gray-400 mt-1">
                        Completed: {new Date(stageData.completed_at).toLocaleString()}
                      </p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Workflow Metadata */}
          <div className="mt-6 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Started:</p>
                <p className="font-medium">{new Date(workflowState.started_at).toLocaleString()}</p>
              </div>
              <div>
                <p className="text-gray-600">Last Updated:</p>
                <p className="font-medium">{new Date(workflowState.updated_at).toLocaleString()}</p>
              </div>
            </div>
          </div>
        </CardContent>
      )}
    </Card>
  );
}
