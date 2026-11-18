"use client";

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter
} from "@/components/ui/dialog";
import { 
  Activity,
  PlayCircle,
  PauseCircle,
  AlertTriangle,
  CheckCircle2,
  TrendingUp,
  Clock,
  Bell,
  Eye
} from "lucide-react";
import { apiClient } from '@/lib/api-client';
import { useToast } from "@/hooks/use-toast";

interface AgentStatus {
  is_running: boolean;
  started_at?: string;
  last_check?: string;
  monitoring_tasks: {
    name: string;
    enabled: boolean;
    interval: string;
    last_run?: string;
    next_run?: string;
  }[];
}

interface AgentStats {
  total_checks: number;
  actions_taken: number;
  approvals_requested: number;
  alerts_sent: number;
  uptime_hours: number;
}

interface AgentAlert {
  id: number;
  alert_type: string;
  severity: 'info' | 'warning' | 'critical';
  message: string;
  created_at: string;
  resolved: boolean;
  patient_id?: number;
  patient_name?: string;
}

interface AgentMonitorCardProps {
  autoRefresh?: boolean;
  showStats?: boolean;
  maxAlerts?: number;
}

export function AgentMonitorCard({ 
  autoRefresh = true,
  showStats = true,
  maxAlerts = 5
}: AgentMonitorCardProps) {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [selectedAlert, setSelectedAlert] = useState<AgentAlert | null>(null);
  const [showAlertDialog, setShowAlertDialog] = useState(false);

  // Fetch agent status
  const { data: status, isLoading: statusLoading } = useQuery<AgentStatus>({
    queryKey: ['agent-status'],
    queryFn: async () => {
      const response = await apiClient.get('/api/agent/status');
      return response.data;
    },
    refetchInterval: autoRefresh ? 10000 : false
  });

  // Fetch agent stats
  const { data: stats, isLoading: statsLoading } = useQuery<AgentStats>({
    queryKey: ['agent-stats'],
    queryFn: async () => {
      const response = await apiClient.get('/api/agent/stats');
      return response.data;
    },
    refetchInterval: autoRefresh ? 30000 : false,
    enabled: showStats
  });

  // Fetch recent alerts
  const { data: alerts, isLoading: alertsLoading } = useQuery<AgentAlert[]>({
    queryKey: ['agent-alerts'],
    queryFn: async () => {
      const response = await apiClient.get('/api/agent/alerts', {
        params: { limit: maxAlerts }
      });
      return response.data;
    },
    refetchInterval: autoRefresh ? 15000 : false
  });

  // Start agent mutation
  const startAgentMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post('/api/agent/start');
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agent-status'] });
      toast({
        title: "🤖 Proactive Agent Started",
        description: "The AI agent is now monitoring your hospital operations in the background.",
        variant: "default"
      });
    },
    onError: (error: any) => {
      toast({
        title: "Failed to Start Agent",
        description: error.message || "An error occurred",
        variant: "destructive"
      });
    }
  });

  // Stop agent mutation
  const stopAgentMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post('/api/agent/stop');
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agent-status'] });
      toast({
        title: "Proactive Agent Stopped",
        description: "The AI agent has been stopped.",
        variant: "default"
      });
    },
    onError: (error: any) => {
      toast({
        title: "Failed to Stop Agent",
        description: error.message || "An error occurred",
        variant: "destructive"
      });
    }
  });

  const getSeverityBadge = (severity: string) => {
    const variants: Record<string, { bg: string; text: string; icon: any }> = {
      info: { bg: "bg-blue-500", text: "Info", icon: Bell },
      warning: { bg: "bg-orange-500", text: "Warning", icon: AlertTriangle },
      critical: { bg: "bg-red-500 animate-pulse", text: "Critical", icon: AlertTriangle }
    };
    const variant = variants[severity] || variants.info;
    const Icon = variant.icon;
    
    return (
      <Badge className={`${variant.bg} text-white gap-1`}>
        <Icon className="h-3 w-3" />
        {variant.text}
      </Badge>
    );
  };

  const handleViewAlert = (alert: AgentAlert) => {
    setSelectedAlert(alert);
    setShowAlertDialog(true);
  };

  if (statusLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-64 mt-2" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-32 w-full" />
        </CardContent>
      </Card>
    );
  }

  const isRunning = status?.is_running || false;
  const criticalAlerts = alerts?.filter(a => a.severity === 'critical' && !a.resolved).length || 0;

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity className={`h-5 w-5 ${isRunning ? 'text-green-500 animate-pulse' : 'text-gray-400'}`} />
              <div>
                <CardTitle>🤖 Proactive AI Agent</CardTitle>
                <CardDescription>
                  Background monitoring and autonomous actions
                </CardDescription>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {criticalAlerts > 0 && (
                <Badge className="bg-red-500 text-white">
                  {criticalAlerts} Critical
                </Badge>
              )}
              <Badge className={isRunning ? "bg-green-500 text-white" : "bg-gray-400 text-white"}>
                {isRunning ? "Running" : "Stopped"}
              </Badge>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Control Button */}
          <div>
            {isRunning ? (
              <Button
                variant="destructive"
                className="w-full gap-2"
                onClick={() => stopAgentMutation.mutate()}
                disabled={stopAgentMutation.isPending}
              >
                <PauseCircle className="h-4 w-4" />
                {stopAgentMutation.isPending ? "Stopping..." : "Stop Agent"}
              </Button>
            ) : (
              <Button
                className="w-full gap-2 bg-green-500 hover:bg-green-600"
                onClick={() => startAgentMutation.mutate()}
                disabled={startAgentMutation.isPending}
              >
                <PlayCircle className="h-4 w-4" />
                {startAgentMutation.isPending ? "Starting..." : "Start Agent"}
              </Button>
            )}
          </div>

          {/* Stats Grid */}
          {showStats && stats && (
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-blue-50 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Total Checks</p>
                    <p className="text-2xl font-bold text-blue-600">{stats.total_checks}</p>
                  </div>
                  <CheckCircle2 className="h-8 w-8 text-blue-500" />
                </div>
              </div>
              <div className="bg-green-50 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Actions Taken</p>
                    <p className="text-2xl font-bold text-green-600">{stats.actions_taken}</p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-green-500" />
                </div>
              </div>
              <div className="bg-orange-50 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Approvals Requested</p>
                    <p className="text-2xl font-bold text-orange-600">{stats.approvals_requested}</p>
                  </div>
                  <AlertTriangle className="h-8 w-8 text-orange-500" />
                </div>
              </div>
              <div className="bg-purple-50 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Alerts Sent</p>
                    <p className="text-2xl font-bold text-purple-600">{stats.alerts_sent}</p>
                  </div>
                  <Bell className="h-8 w-8 text-purple-500" />
                </div>
              </div>
            </div>
          )}

          {/* Monitoring Tasks */}
          {status?.monitoring_tasks && (
            <div>
              <h4 className="font-semibold mb-3 flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Monitoring Tasks
              </h4>
              <div className="space-y-2">
                {status.monitoring_tasks.map((task, index) => (
                  <div
                    key={index}
                    className={`flex items-center justify-between p-2 rounded border ${
                      task.enabled ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'
                    }`}
                  >
                    <div className="flex-1">
                      <p className="font-medium text-sm">{task.name}</p>
                      <p className="text-xs text-gray-600">Every {task.interval}</p>
                    </div>
                    <Badge variant={task.enabled ? "default" : "secondary"} className="text-xs">
                      {task.enabled ? "Active" : "Disabled"}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recent Alerts */}
          <div>
            <h4 className="font-semibold mb-3 flex items-center gap-2">
              <Bell className="h-4 w-4" />
              Recent Alerts
            </h4>
            {alertsLoading ? (
              <div className="space-y-2">
                {[1, 2, 3].map(i => <Skeleton key={i} className="h-16 w-full" />)}
              </div>
            ) : alerts && alerts.length > 0 ? (
              <ScrollArea className="h-[300px]">
                <div className="space-y-2 pr-4">
                  {alerts.map((alert) => (
                    <div
                      key={alert.id}
                      className={`border rounded-lg p-3 ${
                        alert.severity === 'critical' ? 'border-red-300 bg-red-50' :
                        alert.severity === 'warning' ? 'border-orange-300 bg-orange-50' :
                        'border-blue-300 bg-blue-50'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <p className="font-medium text-sm">{alert.alert_type}</p>
                            {getSeverityBadge(alert.severity)}
                          </div>
                          {alert.patient_name && (
                            <p className="text-xs text-gray-600">
                              Patient: {alert.patient_name} (ID: {alert.patient_id})
                            </p>
                          )}
                        </div>
                      </div>
                      <p className="text-sm text-gray-700 mb-2">{alert.message}</p>
                      <div className="flex items-center justify-between">
                        <p className="text-xs text-gray-500">
                          {new Date(alert.created_at).toLocaleString()}
                        </p>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleViewAlert(alert)}
                          className="h-7 text-xs"
                        >
                          <Eye className="h-3 w-3 mr-1" />
                          Details
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            ) : (
              <div className="text-center py-6 text-gray-500 bg-gray-50 rounded-lg">
                <Bell className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                <p className="text-sm">No recent alerts</p>
              </div>
            )}
          </div>

          {/* Agent Info */}
          {isRunning && status?.started_at && (
            <div className="text-xs text-gray-500 border-t pt-3">
              <p>Agent started: {new Date(status.started_at).toLocaleString()}</p>
              {status.last_check && (
                <p>Last check: {new Date(status.last_check).toLocaleString()}</p>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Alert Details Dialog */}
      <Dialog open={showAlertDialog} onOpenChange={setShowAlertDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Alert Details</DialogTitle>
            <DialogDescription>
              Complete information about this alert
            </DialogDescription>
          </DialogHeader>
          {selectedAlert && (
            <div className="space-y-4">
              <div>
                <h4 className="font-semibold mb-1">Type</h4>
                <p>{selectedAlert.alert_type}</p>
              </div>
              <div>
                <h4 className="font-semibold mb-1">Severity</h4>
                {getSeverityBadge(selectedAlert.severity)}
              </div>
              {selectedAlert.patient_name && (
                <div>
                  <h4 className="font-semibold mb-1">Patient</h4>
                  <p>{selectedAlert.patient_name} (ID: {selectedAlert.patient_id})</p>
                </div>
              )}
              <div>
                <h4 className="font-semibold mb-1">Message</h4>
                <p className="text-sm bg-gray-50 p-3 rounded">{selectedAlert.message}</p>
              </div>
              <div>
                <h4 className="font-semibold mb-1">Created At</h4>
                <p className="text-sm">{new Date(selectedAlert.created_at).toLocaleString()}</p>
              </div>
              <div>
                <h4 className="font-semibold mb-1">Status</h4>
                <Badge variant={selectedAlert.resolved ? "default" : "destructive"}>
                  {selectedAlert.resolved ? "Resolved" : "Active"}
                </Badge>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button onClick={() => setShowAlertDialog(false)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
