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
  FileText,
  MessageSquare,
  Clock,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Activity,
  Stethoscope,
  ClipboardList,
  ArrowRight,
} from 'lucide-react';
import Link from 'next/link';
import axios from 'axios';

interface DashboardStats {
  today_appointments: number;
  pending_consultations: number;
  unread_messages: number;
  pending_lab_reviews: number;
  total_patients: number;
  consultations_this_week: number;
}

interface Appointment {
  appointment_id: string;
  patient_name: string;
  appointment_time: string;
  type: string;
  status: string;
}

interface Task {
  task_id: string;
  title: string;
  priority: string;
  due_date: string;
  status: string;
}

export default function DoctorDashboard() {
  const { user } = useAuth();
  const doctorId = 'doctor001'; // TODO: Get from authenticated user

  // Fetch dashboard stats
  const { data: statsData, isLoading: statsLoading } = useQuery({
    queryKey: ['doctor-stats', doctorId],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `http://localhost:8000/api/doctors/${doctorId}/stats`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data?.data || {
        today_appointments: 0,
        pending_consultations: 0,
        unread_messages: 0,
        pending_lab_reviews: 0,
        total_patients: 0,
        consultations_this_week: 0,
      };
    },
    enabled: !!doctorId,
  });

  // Fetch today's appointments
  const { data: appointmentsData, isLoading: appointmentsLoading } = useQuery({
    queryKey: ['doctor-appointments-today', doctorId],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `http://localhost:8000/api/appointments/doctor/${doctorId}`,
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
    enabled: !!doctorId,
  });

  // Fetch pending tasks
  const { data: tasksData, isLoading: tasksLoading } = useQuery({
    queryKey: ['doctor-tasks', doctorId],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `http://localhost:8000/api/doctors/${doctorId}/tasks`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data?.data?.tasks || [];
    },
    enabled: !!doctorId,
  });

  const stats = statsData || {
    today_appointments: 0,
    pending_consultations: 0,
    unread_messages: 0,
    pending_lab_reviews: 0,
    total_patients: 0,
    consultations_this_week: 0,
  };

  const todayAppointments = appointmentsData || [];
  const tasks = tasksData || [];

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
      case 'confirmed':
        return 'default';
      case 'scheduled':
      case 'in_progress':
        return 'secondary';
      case 'pending':
        return 'outline';
      case 'urgent':
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
        <Sidebar role="doctor" />
        <main className="flex-1 ml-64 mt-16">
          <div className="p-8">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Welcome back, Dr. {user?.username || 'Doctor'}
              </h1>
              <p className="text-gray-600">Here's what's happening with your patients today</p>
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
                  <Link href="/doctor/schedule">
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
                          {stats.today_appointments}
                        </p>
                        <p className="text-sm text-gray-500">scheduled</p>
                      </div>
                    </CardContent>
                  </Link>
                </Card>

                <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                  <Link href="/doctor/consultations">
                    <CardHeader className="pb-2">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-sm font-medium text-gray-600">
                          Pending Consultations
                        </CardTitle>
                        <div className="h-10 w-10 bg-purple-100 rounded-full flex items-center justify-center">
                          <Stethoscope className="h-5 w-5 text-purple-600" />
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-baseline space-x-2">
                        <p className="text-3xl font-bold text-gray-900">
                          {stats.pending_consultations}
                        </p>
                        <p className="text-sm text-gray-500">to review</p>
                      </div>
                    </CardContent>
                  </Link>
                </Card>

                <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                  <Link href="/doctor/messages">
                    <CardHeader className="pb-2">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-sm font-medium text-gray-600">
                          Unread Messages
                        </CardTitle>
                        <div className="h-10 w-10 bg-green-100 rounded-full flex items-center justify-center">
                          <MessageSquare className="h-5 w-5 text-green-600" />
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-baseline space-x-2">
                        <p className="text-3xl font-bold text-gray-900">
                          {stats.unread_messages}
                        </p>
                        <p className="text-sm text-gray-500">new</p>
                      </div>
                    </CardContent>
                  </Link>
                </Card>

                <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                  <Link href="/doctor/lab-results">
                    <CardHeader className="pb-2">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-sm font-medium text-gray-600">
                          Lab Reviews Pending
                        </CardTitle>
                        <div className="h-10 w-10 bg-orange-100 rounded-full flex items-center justify-center">
                          <FileText className="h-5 w-5 text-orange-600" />
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-baseline space-x-2">
                        <p className="text-3xl font-bold text-gray-900">
                          {stats.pending_lab_reviews}
                        </p>
                        <p className="text-sm text-gray-500">results</p>
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
                  <CardTitle className="text-lg">Your Statistics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
                          <Users className="h-5 w-5 text-blue-600" />
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Total Patients</p>
                          <p className="text-2xl font-bold text-gray-900">{stats.total_patients}</p>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="h-10 w-10 bg-purple-100 rounded-full flex items-center justify-center">
                          <Activity className="h-5 w-5 text-purple-600" />
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">This Week's Consultations</p>
                          <p className="text-2xl font-bold text-gray-900">
                            {stats.consultations_this_week}
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
                    <Link href="/doctor/consultations">
                      <Button variant="outline" className="w-full justify-start">
                        <Stethoscope className="h-4 w-4 mr-2" />
                        New Consultation
                      </Button>
                    </Link>
                    <Link href="/doctor/prescriptions">
                      <Button variant="outline" className="w-full justify-start">
                        <FileText className="h-4 w-4 mr-2" />
                        Write Prescription
                      </Button>
                    </Link>
                    <Link href="/doctor/lab-results">
                      <Button variant="outline" className="w-full justify-start">
                        <ClipboardList className="h-4 w-4 mr-2" />
                        Order Lab Test
                      </Button>
                    </Link>
                    <Link href="/doctor/patients">
                      <Button variant="outline" className="w-full justify-start">
                        <Users className="h-4 w-4 mr-2" />
                        View Patients
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Today's Schedule */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Today's Schedule</CardTitle>
                    <Link href="/doctor/schedule">
                      <Button variant="ghost" size="sm">
                        View All
                        <ArrowRight className="h-4 w-4 ml-2" />
                      </Button>
                    </Link>
                  </div>
                  <CardDescription>
                    {todayAppointments.length} appointments scheduled for today
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
                      <p className="text-gray-600">No appointments scheduled for today</p>
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
                          <Badge variant={getStatusColor(appointment.status)}>
                            {appointment.status}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Pending Tasks */}
              <Card>
                <CardHeader>
                  <CardTitle>Pending Tasks</CardTitle>
                  <CardDescription>
                    {tasks.filter((t: Task) => t.status !== 'completed').length} tasks require
                    your attention
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {tasksLoading ? (
                    <div className="space-y-3">
                      {[1, 2, 3].map((i) => (
                        <Skeleton key={i} className="h-16 w-full" />
                      ))}
                    </div>
                  ) : tasks.length === 0 ? (
                    <div className="text-center py-8">
                      <CheckCircle className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                      <p className="text-gray-600">All tasks completed!</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {tasks
                        .filter((t: Task) => t.status !== 'completed')
                        .slice(0, 5)
                        .map((task: Task) => (
                          <div
                            key={task.task_id}
                            className="flex items-start justify-between p-3 bg-gray-50 rounded-lg"
                          >
                            <div className="flex-1">
                              <div className="flex items-center space-x-2 mb-1">
                                <p className="font-medium text-gray-900">{task.title}</p>
                                <Badge variant={getPriorityColor(task.priority)} className="text-xs">
                                  {task.priority}
                                </Badge>
                              </div>
                              <p className="text-sm text-gray-600">
                                Due: {new Date(task.due_date).toLocaleDateString()}
                              </p>
                            </div>
                            {task.priority === 'high' || task.priority === 'urgent' ? (
                              <AlertCircle className="h-5 w-5 text-red-500" />
                            ) : null}
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
