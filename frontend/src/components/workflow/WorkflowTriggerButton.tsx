"use client";

import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from "@/components/ui/button";
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogFooter, 
  DialogHeader, 
  DialogTitle 
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Play, Loader2 } from "lucide-react";
import { apiClient } from '@/lib/api-client';
import { useToast } from "@/hooks/use-toast";

interface WorkflowStartData {
  patient_id?: number;
  name: string;
  age: number;
  gender: string;
  phone: string;
  email: string;
  symptoms: string;
  existing_conditions?: string;
  allergies?: string;
  current_medications?: string;
  insurance_provider?: string;
  insurance_id?: string;
  emergency_contact?: string;
  emergency_phone?: string;
}

interface WorkflowTriggerButtonProps {
  patientData?: Partial<WorkflowStartData>;
  variant?: "default" | "outline" | "ghost";
  size?: "default" | "sm" | "lg";
  onSuccess?: (workflowId: string) => void;
}

export function WorkflowTriggerButton({ 
  patientData,
  variant = "default",
  size = "default",
  onSuccess
}: WorkflowTriggerButtonProps) {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [showDialog, setShowDialog] = useState(false);
  const [formData, setFormData] = useState<WorkflowStartData>({
    name: patientData?.name || "",
    age: patientData?.age || 0,
    gender: patientData?.gender || "",
    phone: patientData?.phone || "",
    email: patientData?.email || "",
    symptoms: patientData?.symptoms || "",
    existing_conditions: patientData?.existing_conditions || "",
    allergies: patientData?.allergies || "",
    current_medications: patientData?.current_medications || "",
    insurance_provider: patientData?.insurance_provider || "",
    insurance_id: patientData?.insurance_id || "",
    emergency_contact: patientData?.emergency_contact || "",
    emergency_phone: patientData?.emergency_phone || "",
    patient_id: patientData?.patient_id
  });

  const startWorkflowMutation = useMutation({
    mutationFn: async (data: WorkflowStartData) => {
      const response = await apiClient.post('/api/workflow/start', data);
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['workflow-state'] });
      queryClient.invalidateQueries({ queryKey: ['patients'] });
      toast({
        title: "✅ AI Workflow Started!",
        description: `The AI agent is now processing ${formData.name}'s journey through 11 workflow stages.`,
        variant: "default"
      });
      setShowDialog(false);
      if (onSuccess) {
        onSuccess(data.workflow_id);
      }
    },
    onError: (error: any) => {
      toast({
        title: "Failed to Start Workflow",
        description: error.message || "An error occurred while starting the workflow",
        variant: "destructive"
      });
    }
  });

  const handleInputChange = (field: keyof WorkflowStartData, value: string | number) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = () => {
    // Validation
    if (!formData.name || !formData.age || !formData.gender || !formData.phone || !formData.symptoms) {
      toast({
        title: "Missing Required Fields",
        description: "Please fill in all required fields (Name, Age, Gender, Phone, Symptoms)",
        variant: "destructive"
      });
      return;
    }

    startWorkflowMutation.mutate(formData);
  };

  return (
    <>
      <Button
        variant={variant}
        size={size}
        onClick={() => setShowDialog(true)}
        className="gap-2"
      >
        <Play className="h-4 w-4" />
        Start AI Workflow
      </Button>

      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>🤖 Start AI-Powered Patient Workflow</DialogTitle>
            <DialogDescription>
              The AI agent will automatically process this patient through 11 intelligent stages: 
              Registration → Document Processing → Medical History → Test Determination → 
              Lab Coordination → Results Analysis → Admission Planning → Admission Process → 
              Treatment Monitoring → Discharge → Follow-up
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6 py-4">
            {/* Basic Information */}
            <div className="space-y-4">
              <h3 className="font-semibold text-lg border-b pb-2">Basic Information</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="name">Full Name *</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    placeholder="John Doe"
                  />
                </div>
                <div>
                  <Label htmlFor="age">Age *</Label>
                  <Input
                    id="age"
                    type="number"
                    value={formData.age || ""}
                    onChange={(e) => handleInputChange('age', parseInt(e.target.value) || 0)}
                    placeholder="30"
                  />
                </div>
                <div>
                  <Label htmlFor="gender">Gender *</Label>
                  <Select 
                    value={formData.gender} 
                    onValueChange={(value) => handleInputChange('gender', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select gender" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Male">Male</SelectItem>
                      <SelectItem value="Female">Female</SelectItem>
                      <SelectItem value="Other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="phone">Phone Number *</Label>
                  <Input
                    id="phone"
                    value={formData.phone}
                    onChange={(e) => handleInputChange('phone', e.target.value)}
                    placeholder="+1234567890"
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  placeholder="john.doe@example.com"
                />
              </div>
            </div>

            {/* Medical Information */}
            <div className="space-y-4">
              <h3 className="font-semibold text-lg border-b pb-2">Medical Information</h3>
              <div>
                <Label htmlFor="symptoms">Symptoms / Reason for Visit *</Label>
                <Textarea
                  id="symptoms"
                  value={formData.symptoms}
                  onChange={(e) => handleInputChange('symptoms', e.target.value)}
                  placeholder="Describe the patient's symptoms or reason for visit..."
                  rows={3}
                />
              </div>
              <div>
                <Label htmlFor="existing_conditions">Existing Medical Conditions</Label>
                <Textarea
                  id="existing_conditions"
                  value={formData.existing_conditions}
                  onChange={(e) => handleInputChange('existing_conditions', e.target.value)}
                  placeholder="Diabetes, Hypertension, etc."
                  rows={2}
                />
              </div>
              <div>
                <Label htmlFor="allergies">Known Allergies</Label>
                <Input
                  id="allergies"
                  value={formData.allergies}
                  onChange={(e) => handleInputChange('allergies', e.target.value)}
                  placeholder="Penicillin, Peanuts, etc."
                />
              </div>
              <div>
                <Label htmlFor="current_medications">Current Medications</Label>
                <Textarea
                  id="current_medications"
                  value={formData.current_medications}
                  onChange={(e) => handleInputChange('current_medications', e.target.value)}
                  placeholder="List current medications..."
                  rows={2}
                />
              </div>
            </div>

            {/* Insurance & Emergency Contact */}
            <div className="space-y-4">
              <h3 className="font-semibold text-lg border-b pb-2">Insurance & Emergency Contact</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="insurance_provider">Insurance Provider</Label>
                  <Input
                    id="insurance_provider"
                    value={formData.insurance_provider}
                    onChange={(e) => handleInputChange('insurance_provider', e.target.value)}
                    placeholder="Blue Cross, Aetna, etc."
                  />
                </div>
                <div>
                  <Label htmlFor="insurance_id">Insurance ID</Label>
                  <Input
                    id="insurance_id"
                    value={formData.insurance_id}
                    onChange={(e) => handleInputChange('insurance_id', e.target.value)}
                    placeholder="Insurance ID number"
                  />
                </div>
                <div>
                  <Label htmlFor="emergency_contact">Emergency Contact Name</Label>
                  <Input
                    id="emergency_contact"
                    value={formData.emergency_contact}
                    onChange={(e) => handleInputChange('emergency_contact', e.target.value)}
                    placeholder="Jane Doe"
                  />
                </div>
                <div>
                  <Label htmlFor="emergency_phone">Emergency Contact Phone</Label>
                  <Input
                    id="emergency_phone"
                    value={formData.emergency_phone}
                    onChange={(e) => handleInputChange('emergency_phone', e.target.value)}
                    placeholder="+1234567890"
                  />
                </div>
              </div>
            </div>

            {/* Info Box */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-semibold text-blue-900 mb-2">🤖 What happens next?</h4>
              <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
                <li>AI agent will register the patient and create medical records</li>
                <li>AI will analyze symptoms and determine required tests</li>
                <li>Lab coordination will be automated with smart scheduling</li>
                <li>Results will be analyzed with AI recommendations</li>
                <li>You'll receive approval requests at critical decision points</li>
                <li>Full workflow state visible in real-time dashboard</li>
              </ul>
            </div>
          </div>

          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => setShowDialog(false)}
              disabled={startWorkflowMutation.isPending}
            >
              Cancel
            </Button>
            <Button 
              onClick={handleSubmit}
              disabled={startWorkflowMutation.isPending}
              className="gap-2"
            >
              {startWorkflowMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Starting AI Workflow...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4" />
                  Start AI Workflow
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
