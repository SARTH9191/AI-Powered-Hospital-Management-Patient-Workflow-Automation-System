'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';
import {
  Users,
  Calendar,
  DollarSign,
  ClipboardList,
  CheckCircle,
  Clock,
  AlertCircle,
  TrendingUp,
  Phone,
  Mail,
  MapPin,
  FileText,
} from 'lucide-react';

interface Task {
  id: string;
  title: string;
  type: 'registration' | 'appointment' | 'billing' | 'lab' | 'pharmacy';
  priority: 'high' | 'medium' | 'low';
  status: 'pending' | 'in_progress' | 'completed';
  dueTime?: string;
  patient?: string;
}

interface RecentActivity {
  id: string;
  action: string;
  patient: string;
  time: string;
  type: 'registration' | 'appointment' | 'billing' | 'lab';
}

export default function StaffDashboard() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);

  // Redirect to dashboard page with workflow components
  useEffect(() => {
    router.push('/staff/dashboard');
  }, [router]);

  useEffect(() => {
    // Mock data - Replace with actual API call
    setTasks([
      {
        id: '1',
        title: 'Register new patient - Emily Johnson',
        type: 'registration',
        priority: 'high',
        status: 'pending',
        dueTime: '10:00 AM',
        patient: 'Emily Johnson',
      },
      {
        id: '2',
        title: 'Schedule follow-up appointment',
        type: 'appointment',
        priority: 'medium',
        status: 'pending',
        dueTime: '11:30 AM',
        patient: 'Michael Brown',
      },
      {
        id: '3',
        title: 'Process payment - Invoice #1234',
        type: 'billing',
        priority: 'high',
        status: 'in_progress',
        patient: 'Sarah Miller',
      },
      {
        id: '4',
        title: 'Order lab tests for routine checkup',
        type: 'lab',
        priority: 'medium',
        status: 'pending',
        dueTime: '2:00 PM',
        patient: 'James Wilson',
      },
      {
        id: '5',
        title: 'Refill prescription request',
        type: 'pharmacy',
        priority: 'low',
        status: 'pending',
        patient: 'Linda Taylor',
      },
    ]);

    setRecentActivity([
      {
        id: '1',
        action: 'Registered new patient',
        patient: 'Robert Johnson',
        time: '5 minutes ago',
        type: 'registration',
      },
      {
        id: '2',
        action: 'Scheduled appointment',
        patient: 'Mary Smith',
        time: '15 minutes ago',
        type: 'appointment',
      },
      {
        id: '3',
        action: 'Processed payment',
        patient: 'David Williams',
        time: '30 minutes ago',
        type: 'billing',
      },
      {
        id: '4',
        action: 'Ordered lab tests',
        patient: 'Jennifer Davis',
        time: '1 hour ago',
        type: 'lab',
      },
    ]);
  }, []);

  const stats = [
    {
      title: 'Today\'s Registrations',
      value: '8',
      change: '+2 from yesterday',
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      title: 'Scheduled Appointments',
      value: '24',
      change: '+5 pending',
      icon: Calendar,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
    {
      title: 'Pending Payments',
      value: '$3,450',
      change: '12 invoices',
      icon: DollarSign,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      title: 'Tasks Completed',
      value: '18/25',
      change: '72% completion',
      icon: ClipboardList,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
    },
  ];

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'destructive';
      case 'medium':
        return 'default';
      case 'low':
        return 'secondary';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'in_progress':
        return <Clock className="h-4 w-4 text-orange-600" />;
      case 'pending':
        return <AlertCircle className="h-4 w-4 text-gray-600" />;
      default:
        return null;
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'registration':
        return <Users className="h-4 w-4" />;
      case 'appointment':
        return <Calendar className="h-4 w-4" />;
      case 'billing':
        return <DollarSign className="h-4 w-4" />;
      case 'lab':
        return <FileText className="h-4 w-4" />;
      case 'pharmacy':
        return <FileText className="h-4 w-4" />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar role="staff" />
        <main className="flex-1 ml-64 mt-16">
          <div className="p-8">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Welcome back, {user?.username || 'Staff Member'}!
              </h1>
              <p className="text-gray-600">Here's your task list and recent activity for today</p>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {stats.map((stat, index) => (
                <Card key={index}>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-gray-600">
                      {stat.title}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
                        <p className="text-sm text-gray-500 mt-1">{stat.change}</p>
                      </div>
                      <div className={`h-12 w-12 ${stat.bgColor} rounded-full flex items-center justify-center`}>
                        <stat.icon className={`h-6 w-6 ${stat.color}`} />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Grid Layout for Tasks and Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              {/* Today's Tasks */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>Today's Tasks</CardTitle>
                      <CardDescription>Your pending and ongoing tasks</CardDescription>
                    </div>
                    <Badge variant="outline">{tasks.length} tasks</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {tasks.map((task) => (
                      <div
                        key={task.id}
                        className="flex items-start justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                      >
                        <div className="flex items-start space-x-3 flex-1">
                          <div className="mt-1">
                            {getStatusIcon(task.status)}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center space-x-2 mb-1">
                              {getTypeIcon(task.type)}
                              <p className="text-sm font-medium text-gray-900 truncate">
                                {task.title}
                              </p>
                            </div>
                            {task.patient && (
                              <p className="text-xs text-gray-500">Patient: {task.patient}</p>
                            )}
                            {task.dueTime && (
                              <p className="text-xs text-gray-500 mt-1">Due: {task.dueTime}</p>
                            )}
                          </div>
                        </div>
                        <Badge variant={getPriorityColor(task.priority)} className="ml-2">
                          {task.priority}
                        </Badge>
                      </div>
                    ))}
                  </div>
                  <Button className="w-full mt-4" variant="outline">
                    View All Tasks
                  </Button>
                </CardContent>
              </Card>

              {/* Recent Activity */}
              <Card>
                <CardHeader>
                  <CardTitle>Recent Activity</CardTitle>
                  <CardDescription>Your latest actions and updates</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {recentActivity.map((activity) => (
                      <div
                        key={activity.id}
                        className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg"
                      >
                        <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                          {getTypeIcon(activity.type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900">
                            {activity.action}
                          </p>
                          <p className="text-xs text-gray-500">
                            Patient: {activity.patient}
                          </p>
                          <p className="text-xs text-gray-400 mt-1">{activity.time}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                  <Button className="w-full mt-4" variant="outline">
                    View Activity Log
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>Common tasks you can perform quickly</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <Button className="h-auto py-4 flex flex-col items-center space-y-2" variant="outline">
                    <Users className="h-6 w-6 text-blue-600" />
                    <span>Register Patient</span>
                  </Button>
                  <Button className="h-auto py-4 flex flex-col items-center space-y-2" variant="outline">
                    <Calendar className="h-6 w-6 text-purple-600" />
                    <span>Schedule Appointment</span>
                  </Button>
                  <Button className="h-auto py-4 flex flex-col items-center space-y-2" variant="outline">
                    <DollarSign className="h-6 w-6 text-green-600" />
                    <span>Process Payment</span>
                  </Button>
                  <Button className="h-auto py-4 flex flex-col items-center space-y-2" variant="outline">
                    <FileText className="h-6 w-6 text-orange-600" />
                    <span>Order Lab Tests</span>
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
