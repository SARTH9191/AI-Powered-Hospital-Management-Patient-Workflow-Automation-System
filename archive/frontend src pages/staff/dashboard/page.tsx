'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@/hooks/useAuth';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';
import {
  Calendar,
  Users,
  ClipboardCheck,
  Clock,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  UserCheck,
  FileText,
  Phone,
  ArrowRight,
  Activity,
  MessageSquare,
} from 'lucide-react';
import Link from 'next/link';
import axios from 'axios';
// 🤖 AI WORKFLOW COMPONENTS - Connect to 113-Tool Backend!
import { 
  ApprovalQueueCard, 
  WorkflowTriggerButton, 
  AgentMonitorCard 
} from '@/components/workflow';

interface DashboardStats {
  todays_appointments: number;
  pending_check_ins: number;
  total_patients_today: number;
  completed_check_ins: number;
  upcoming_appointments: number;
  total_staff_members: number;
}

interface Appointment {
  appointment_id: string;
  patient_name: string;
  patient_id: string;
  appointment_time: string;
  doctor_name: string;
  type: string;
  status: string;
  checked_in: boolean;
}

interface Task {
  task_id: string;
  title: string;
  priority: string;
  status: string;
  due_time: string;
}

export default function StaffDashboard() {
  const { user } = useAuth();
  const staffId = 'staff001'; // TODO: Get from authenticated user

  // Fetch dashboard stats
  const { data: statsData, isLoading: statsLoading } = useQuery({
    queryKey: ['staff-stats', staffId],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `http://localhost:8000/api/staff/${staffId}/stats`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data?.data || {
        todays_appointments: 0,
        pending_check_ins: 0,
        total_patients_today: 0,
        completed_check_ins: 0,
        upcoming_appointments: 0,
        total_staff_members: 0,
      };
    },
    enabled: !!staffId,
  });

  // Fetch today's appointments
  const { data: appointmentsData, isLoading: appointmentsLoading } = useQuery({
    queryKey: ['staff-appointments-today', staffId],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `http://localhost:8000/api/appointments`,
        {
          params: {
            date: new Date().toISOString().split('T')[0],
          },
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data?.data?.appointments || [];
    },
    enabled: !!staffId,
  });

  // Fetch pending tasks
  const { data: tasksData, isLoading: tasksLoading } = useQuery({
    queryKey: ['staff-tasks', staffId],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `http://localhost:8000/api/staff/${staffId}/tasks`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data?.data?.tasks || [];
    },
    enabled: !!staffId,
  });

  const stats = statsData || {
    todays_appointments: 0,
    pending_check_ins: 0,
    total_patients_today: 0,
    completed_check_ins: 0,
    upcoming_appointments: 0,
    total_staff_members: 0,
  };

  const todayAppointments = (appointmentsData || []).slice(0, 10);
  const tasks = (tasksData || []).slice(0, 5);

  const formatTime = (timeString: string) => {
    return new Date(`2000-01-01T${timeString}`).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'default';
      case 'confirmed':
      case 'scheduled':
        return 'secondary';
      case 'in_progress':
        return 'outline';
      case 'cancelled':
        return 'destructive';
      default:
        return 'outline';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high':
      case 'urgent':
        return 'destructive';
      case 'medium':
        return 'secondary';
      case 'low':
        return 'outline';
      default:
        return 'outline';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar role="staff" />
        <main className="flex-1 ml-64 mt-16">
          <div className="p-8">
            {/* Header with AI Workflow Trigger */}
            <div className="mb-8 flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                  Welcome back, {user?.username || 'Staff'}
                </h1>
                <p className="text-gray-600">Here's today's overview and pending tasks</p>
              </div>
              {/* 🤖 AI Workflow Trigger Button */}
              <WorkflowTriggerButton 
                size="lg" 
                onSuccess={(workflowId) => console.log('Workflow started:', workflowId)} 
              />
            </div>

            {/* Stats Grid */}
            {statsLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                {[1, 2, 3, 4].map((i) => (
                  <Card key={i}>
                    <CardHeader className="pb-2">
                      <Skeleton className="h-4 w-24" />
                    </CardHeader>
                    <CardContent>
                      <Skeleton className="h-8 w-16" />
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                  <Link href="/staff/appointments">
                    <CardHeader className="pb-2">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-sm font-medium text-gray-600">
                          Today's Appointments
                        </CardTitle>
                        <div className="h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
                          <Calendar className="h-5 w-5 text-blue-600" />
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-baseline space-x-2">
                        <p className="text-3xl font-bold text-gray-900">
                          {stats.todays_appointments}
                        </p>
                        <p className="text-sm text-gray-500">scheduled</p>
                      </div>
                    </CardContent>
                  </Link>
                </Card>

                <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                  <Link href="/staff/check-in">
                    <CardHeader className="pb-2">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-sm font-medium text-gray-600">
                          Pending Check-ins
                        </CardTitle>
                        <div className="h-10 w-10 bg-orange-100 rounded-full flex items-center justify-center">
                          <UserCheck className="h-5 w-5 text-orange-600" />
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-baseline space-x-2">
                        <p className="text-3xl font-bold text-gray-900">
                          {stats.pending_check_ins}
                        </p>
                        <p className="text-sm text-gray-500">waiting</p>
                      </div>
                    </CardContent>
                  </Link>
                </Card>

                <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                  <Link href="/staff/patients">
                    <CardHeader className="pb-2">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-sm font-medium text-gray-600">
                          Total Patients Today
                        </CardTitle>
                        <div className="h-10 w-10 bg-green-100 rounded-full flex items-center justify-center">
                          <Users className="h-5 w-5 text-green-600" />
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-baseline space-x-2">
                        <p className="text-3xl font-bold text-gray-900">
                          {stats.total_patients_today}
                        </p>
                        <p className="text-sm text-gray-500">patients</p>
                      </div>
                    </CardContent>
                  </Link>
                </Card>

                <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                  <Link href="/staff/appointments">
                    <CardHeader className="pb-2">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-sm font-medium text-gray-600">
                          Completed Check-ins
                        </CardTitle>
                        <div className="h-10 w-10 bg-purple-100 rounded-full flex items-center justify-center">
                          <CheckCircle className="h-5 w-5 text-purple-600" />
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-baseline space-x-2">
                        <p className="text-3xl font-bold text-gray-900">
                          {stats.completed_check_ins}
                        </p>
                        <p className="text-sm text-gray-500">done</p>
                      </div>
                    </CardContent>
                  </Link>
                </Card>
              </div>
            )}

            {/* Secondary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Quick Stats</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
                          <Clock className="h-5 w-5 text-blue-600" />
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Upcoming Appointments</p>
                          <p className="text-2xl font-bold text-gray-900">{stats.upcoming_appointments}</p>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="h-10 w-10 bg-purple-100 rounded-full flex items-center justify-center">
                          <Activity className="h-5 w-5 text-purple-600" />
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Check-in Rate</p>
                          <p className="text-2xl font-bold text-gray-900">
                            {stats.todays_appointments > 0
                              ? Math.round((stats.completed_check_ins / stats.todays_appointments) * 100)
                              : 0}%
                          </p>
                        </div>
                      </div>
                      <Badge variant="secondary">
                        <TrendingUp className="h-3 w-3 mr-1" />
                        Active
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Quick Actions</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-3">
                    <Link href="/staff/chat">
                      <Button variant="outline" className="w-full justify-start hover:bg-purple-50">
                        <MessageSquare className="h-4 w-4 mr-2 text-purple-600" />
                        AI Chat
                      </Button>
                    </Link>
                    <Link href="/staff/check-in">
                      <Button variant="outline" className="w-full justify-start">
                        <UserCheck className="h-4 w-4 mr-2" />
                        Patient Check-in
                      </Button>
                    </Link>
                    <Link href="/staff/appointments">
                      <Button variant="outline" className="w-full justify-start">
                        <Calendar className="h-4 w-4 mr-2" />
                        View Schedule
                      </Button>
                    </Link>
                    <Link href="/staff/patients">
                      <Button variant="outline" className="w-full justify-start">
                        <Users className="h-4 w-4 mr-2" />
                        Patient Records
                      </Button>
                    </Link>
                    <Link href="/staff/billing">
                      <Button variant="outline" className="w-full justify-start">
                        <FileText className="h-4 w-4 mr-2" />
                        Billing
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* 🤖 AI WORKFLOW SECTION - HITL Approval Queue */}
            <div className="mb-8">
              <ApprovalQueueCard maxItems={5} autoRefresh={true} showStats={true} />
            </div>

            {/* 🤖 AI PROACTIVE AGENT MONITOR */}
            <div className="mb-8">
              <AgentMonitorCard autoRefresh={true} showStats={true} maxAlerts={5} />
            </div>

            {/* Today's Schedule & Tasks */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Appointments Needing Check-in */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Pending Check-ins</CardTitle>
                    <Link href="/staff/check-in">
                      <Button variant="ghost" size="sm">
                        View All
                        <ArrowRight className="h-4 w-4 ml-2" />
                      </Button>
                    </Link>
                  </div>
                  <CardDescription>
                    Patients waiting to be checked in
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {appointmentsLoading ? (
                    <div className="space-y-3">
                      {[1, 2, 3].map((i) => (
                        <Skeleton key={i} className="h-16 w-full" />
                      ))}
                    </div>
                  ) : todayAppointments.filter((a: Appointment) => !a.checked_in && a.status !== 'cancelled').length === 0 ? (
                    <div className="text-center py-8">
                      <CheckCircle className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                      <p className="text-gray-600">All patients checked in!</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {todayAppointments
                        .filter((a: Appointment) => !a.checked_in && a.status !== 'cancelled')
                        .slice(0, 5)
                        .map((appointment: Appointment) => (
                          <div
                            key={appointment.appointment_id}
                            className="flex items-center justify-between p-3 bg-orange-50 border border-orange-200 rounded-lg hover:bg-orange-100 transition-colors"
                          >
                            <div className="flex items-center space-x-3">
                              <div className="h-10 w-10 bg-orange-600 rounded-full flex items-center justify-center">
                                <span className="text-white font-semibold text-sm">
                                  {appointment.patient_name?.charAt(0) || 'P'}
                                </span>
                              </div>
                              <div>
                                <p className="font-medium text-gray-900">
                                  {appointment.patient_name}
                                </p>
                                <div className="flex items-center space-x-2 text-sm text-gray-600">
                                  <Clock className="h-3 w-3" />
                                  <span>{formatTime(appointment.appointment_time)}</span>
                                  <span>•</span>
                                  <span>Dr. {appointment.doctor_name}</span>
                                </div>
                              </div>
                            </div>
                            <Link href={`/staff/check-in?appointment=${appointment.appointment_id}`}>
                              <Button size="sm">
                                <UserCheck className="h-4 w-4 mr-2" />
                                Check In
                              </Button>
                            </Link>
                          </div>
                        ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Upcoming Appointments */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Next Appointments</CardTitle>
                    <Link href="/staff/appointments">
                      <Button variant="ghost" size="sm">
                        View All
                        <ArrowRight className="h-4 w-4 ml-2" />
                      </Button>
                    </Link>
                  </div>
                  <CardDescription>
                    Upcoming appointments in the next hour
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {appointmentsLoading ? (
                    <div className="space-y-3">
                      {[1, 2, 3].map((i) => (
                        <Skeleton key={i} className="h-16 w-full" />
                      ))}
                    </div>
                  ) : todayAppointments.length === 0 ? (
                    <div className="text-center py-8">
                      <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                      <p className="text-gray-600">No upcoming appointments</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {todayAppointments.slice(0, 5).map((appointment: Appointment) => (
                        <div
                          key={appointment.appointment_id}
                          className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                        >
                          <div className="flex items-center space-x-3">
                            <div className="h-10 w-10 bg-blue-600 rounded-full flex items-center justify-center">
                              <span className="text-white font-semibold text-sm">
                                {appointment.patient_name?.charAt(0) || 'P'}
                              </span>
                            </div>
                            <div>
                              <p className="font-medium text-gray-900">
                                {appointment.patient_name}
                              </p>
                              <div className="flex items-center space-x-2 text-sm text-gray-600">
                                <Clock className="h-3 w-3" />
                                <span>{formatTime(appointment.appointment_time)}</span>
                                <span>•</span>
                                <span className="capitalize">{appointment.type}</span>
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            {appointment.checked_in ? (
                              <Badge variant="default">
                                <CheckCircle className="h-3 w-3 mr-1" />
                                Checked In
                              </Badge>
                            ) : (
                              <Badge variant="outline">
                                Waiting
                              </Badge>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
