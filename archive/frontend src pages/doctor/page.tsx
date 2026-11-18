'use client';

import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '@/store/authStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Calendar,
  Users,
  ClipboardCheck,
  TestTube,
  Pill,
  Clock,
  TrendingUp,
  AlertCircle,
  MessageSquare,
} from 'lucide-react';
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';
import axios from 'axios';
import Link from 'next/link';

interface DoctorStats {
  totalPatients: number;
  appointmentsToday: number;
  pendingApprovals: number;
  urgentCases: number;
}

export default function DoctorPage() {
  const { user } = useAuthStore();

  // Fetch real pending approvals from backend
  const { data: approvalsData, isLoading: approvalsLoading } = useQuery({
    queryKey: ['doctor-approvals'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(
        'http://localhost:8000/api/workflow/approvals/pending',
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data?.data || { pending_approvals: [], count: 0 };
    },
  });

  // Fetch doctor's appointments
  const { data: appointmentsData, isLoading: appointmentsLoading } = useQuery({
    queryKey: ['doctor-appointments', user?.username],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const doctorId = user?.username || 'doctor';
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
  });

  const pendingApprovals = approvalsData?.pending_approvals || [];
  const upcomingAppointments = appointmentsData || [];
  const isLoading = approvalsLoading || appointmentsLoading;

  // Calculate stats from real data
  const stats = {
    totalPatients: 0, // TODO: Add endpoint for total patients
    appointmentsToday: upcomingAppointments.length,
    pendingApprovals: pendingApprovals.length,
    urgentCases: pendingApprovals.filter((a: any) => a.priority === 'high' || a.urgency === 'critical').length,
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
                Welcome back, Dr. {user?.username || 'Doctor'}!
              </h1>
              <p className="text-gray-600">Here's your schedule and pending tasks for today</p>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">My Patients</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div>
                      {isLoading ? (
                        <div className="h-8 w-16 bg-gray-200 animate-pulse rounded"></div>
                      ) : (
                        <>
                          <p className="text-3xl font-bold text-gray-900">{stats.totalPatients}</p>
                          <p className="text-xs text-gray-500 mt-1">Active patients</p>
                        </>
                      )}
                    </div>
                    <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <Users className="h-6 w-6 text-blue-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Appointments Today
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div>
                      {isLoading ? (
                        <div className="h-8 w-12 bg-gray-200 animate-pulse rounded"></div>
                      ) : (
                        <>
                          <p className="text-3xl font-bold text-gray-900">{stats.appointmentsToday}</p>
                          <p className="text-xs text-gray-500 mt-1">3 completed</p>
                        </>
                      )}
                    </div>
                    <div className="h-12 w-12 bg-purple-100 rounded-full flex items-center justify-center">
                      <Calendar className="h-6 w-6 text-purple-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Pending Approvals
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div>
                      {isLoading ? (
                        <div className="h-8 w-12 bg-gray-200 animate-pulse rounded"></div>
                      ) : (
                        <>
                          <p className="text-3xl font-bold text-gray-900">{stats.pendingApprovals}</p>
                          <p className="text-xs text-orange-600 mt-1">2 urgent</p>
                        </>
                      )}
                    </div>
                    <div className="h-12 w-12 bg-orange-100 rounded-full flex items-center justify-center">
                      <ClipboardCheck className="h-6 w-6 text-orange-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Urgent Cases</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div>
                      {isLoading ? (
                        <div className="h-8 w-12 bg-gray-200 animate-pulse rounded"></div>
                      ) : (
                        <>
                          <p className="text-3xl font-bold text-gray-900">{stats.urgentCases}</p>
                          <p className="text-xs text-red-600 mt-1">Requires attention</p>
                        </>
                      )}
                    </div>
                    <div className="h-12 w-12 bg-red-100 rounded-full flex items-center justify-center">
                      <AlertCircle className="h-6 w-6 text-red-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Grid Layout for Appointments and Approvals */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              {/* Today's Appointments */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span className="flex items-center">
                      <Calendar className="h-5 w-5 mr-2" />
                      Today's Appointments
                    </span>
                    <Badge variant="secondary">{upcomingAppointments.length} total</Badge>
                  </CardTitle>
                  <CardDescription>Your schedule for today</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {upcomingAppointments.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        <Calendar className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                        <p>No appointments scheduled for today</p>
                      </div>
                    ) : (
                      upcomingAppointments.slice(0, 5).map((appointment: any, index: number) => (
                        <div
                          key={appointment.appointment_id || index}
                          className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                        >
                          <div className="flex items-center space-x-3">
                            <div className="flex flex-col items-center justify-center h-12 w-16 bg-blue-50 rounded">
                              <Clock className="h-4 w-4 text-blue-600 mb-1" />
                              <span className="text-xs font-medium text-blue-600">
                                {new Date(appointment.appointment_time).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true }).split(' ')[0]}
                              </span>
                              <span className="text-xs text-blue-500">
                                {new Date(appointment.appointment_time).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true }).split(' ')[1]}
                              </span>
                            </div>
                            <div>
                              <p className="font-medium text-gray-900">{appointment.patient_name}</p>
                              <p className="text-sm text-gray-500">{appointment.type || 'Consultation'}</p>
                            </div>
                          </div>
                          <Badge
                            variant={appointment.status === 'confirmed' ? 'default' : 'secondary'}
                          >
                            {appointment.status}
                          </Badge>
                        </div>
                      ))
                    )}
                  </div>
                  {upcomingAppointments.length > 0 && (
                    <Button variant="outline" className="w-full mt-4">
                      View Full Schedule
                    </Button>
                  )}
                </CardContent>
              </Card>

              {/* Pending Approvals */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span className="flex items-center">
                      <ClipboardCheck className="h-5 w-5 mr-2" />
                      Pending Approvals
                    </span>
                    <Badge variant="destructive">{stats.pendingApprovals} pending</Badge>
                  </CardTitle>
                  <CardDescription>Items requiring your approval</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {pendingApprovals.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        <ClipboardCheck className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                        <p>All caught up! No pending approvals.</p>
                      </div>
                    ) : (
                      pendingApprovals.map((approval: any, index: number) => (
                        <div
                          key={approval.approval_id || index}
                          className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                        >
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center space-x-2">
                              <Badge variant="outline" className="text-xs">
                                {approval.approval_type || 'Lab Test'}
                              </Badge>
                              {(approval.priority === 'high' || approval.urgency === 'critical') && (
                                <Badge variant="destructive" className="text-xs">
                                  Urgent
                                </Badge>
                              )}
                            </div>
                            <span className="text-xs text-gray-400">
                              {new Date(approval.created_at || Date.now()).toLocaleTimeString()}
                            </span>
                          </div>
                          <p className="font-medium text-gray-900 mb-1">{approval.patient_name || 'Patient'}</p>
                          <p className="text-sm text-gray-600 mb-3">
                            {approval.description || approval.tests?.join(', ') || 'Approval required'}
                          </p>
                          <div className="flex space-x-2">
                            <Button size="sm" variant="default" className="flex-1">
                              Approve
                            </Button>
                            <Button size="sm" variant="outline" className="flex-1">
                              Reject
                            </Button>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                  {pendingApprovals.length > 0 && (
                    <Button variant="outline" className="w-full mt-4">
                      View All Approvals
                    </Button>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>Common tasks and shortcuts</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                  <Link href="/doctor/chat">
                    <Button variant="outline" className="w-full h-20 flex flex-col items-center justify-center hover:bg-blue-50">
                      <MessageSquare className="h-6 w-6 mb-2 text-blue-600" />
                      <span className="text-sm font-medium">AI Chat</span>
                    </Button>
                  </Link>
                  <Button variant="outline" className="h-20 flex flex-col items-center justify-center">
                    <Users className="h-6 w-6 mb-2 text-blue-600" />
                    <span className="text-sm">View Patients</span>
                  </Button>
                  <Button variant="outline" className="h-20 flex flex-col items-center justify-center">
                    <Pill className="h-6 w-6 mb-2 text-purple-600" />
                    <span className="text-sm">Prescriptions</span>
                  </Button>
                  <Button variant="outline" className="h-20 flex flex-col items-center justify-center">
                    <TestTube className="h-6 w-6 mb-2 text-green-600" />
                    <span className="text-sm">Lab Results</span>
                  </Button>
                  <Button variant="outline" className="h-20 flex flex-col items-center justify-center">
                    <Calendar className="h-6 w-6 mb-2 text-orange-600" />
                    <span className="text-sm">Schedule</span>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}
