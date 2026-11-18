'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, Users, Calendar, Activity } from 'lucide-react';
import axios from 'axios';

// Mock data for charts
const patientGrowthData = [
  { month: 'Jan', patients: 850, newPatients: 120 },
  { month: 'Feb', patients: 920, newPatients: 150 },
  { month: 'Mar', patients: 1050, newPatients: 180 },
  { month: 'Apr', patients: 1150, newPatients: 140 },
  { month: 'May', patients: 1280, newPatients: 200 },
  { month: 'Jun', patients: 1420, newPatients: 220 },
  { month: 'Jul', patients: 1580, newPatients: 240 },
  { month: 'Aug', patients: 1720, newPatients: 210 },
  { month: 'Sep', patients: 1850, newPatients: 190 },
  { month: 'Oct', patients: 2000, newPatients: 230 },
];

const revenueData = [
  { month: 'Jan', revenue: 185000, expenses: 120000 },
  { month: 'Feb', revenue: 195000, expenses: 125000 },
  { month: 'Mar', revenue: 220000, expenses: 130000 },
  { month: 'Apr', revenue: 210000, expenses: 135000 },
  { month: 'May', revenue: 245000, expenses: 140000 },
  { month: 'Jun', revenue: 268000, expenses: 145000 },
  { month: 'Jul', revenue: 285000, expenses: 150000 },
  { month: 'Aug', revenue: 295000, expenses: 155000 },
  { month: 'Sep', revenue: 310000, expenses: 160000 },
  { month: 'Oct', revenue: 325000, expenses: 165000 },
];

const appointmentDistribution = [
  { name: 'General Checkup', value: 420, color: '#3B82F6' },
  { name: 'Specialist Consultation', value: 280, color: '#8B5CF6' },
  { name: 'Follow-up', value: 180, color: '#10B981' },
  { name: 'Emergency', value: 95, color: '#EF4444' },
  { name: 'Lab Tests', value: 220, color: '#F59E0B' },
  { name: 'Vaccination', value: 130, color: '#EC4899' },
];

const departmentPerformance = [
  { department: 'Cardiology', patients: 320, revenue: 85000, satisfaction: 4.8 },
  { department: 'Orthopedics', patients: 280, revenue: 72000, satisfaction: 4.6 },
  { department: 'Pediatrics', patients: 450, revenue: 65000, satisfaction: 4.9 },
  { department: 'General Medicine', patients: 520, revenue: 58000, satisfaction: 4.5 },
  { department: 'Neurology', patients: 180, revenue: 95000, satisfaction: 4.7 },
  { department: 'Dermatology', patients: 250, revenue: 45000, satisfaction: 4.4 },
];

const weeklyAppointments = [
  { day: 'Mon', scheduled: 45, completed: 42, cancelled: 3 },
  { day: 'Tue', scheduled: 52, completed: 48, cancelled: 4 },
  { day: 'Wed', scheduled: 48, completed: 45, cancelled: 3 },
  { day: 'Thu', scheduled: 55, completed: 51, cancelled: 4 },
  { day: 'Fri', scheduled: 58, completed: 54, cancelled: 4 },
  { day: 'Sat', scheduled: 35, completed: 33, cancelled: 2 },
  { day: 'Sun', scheduled: 20, completed: 18, cancelled: 2 },
];

export default function AnalyticsPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState('month');

  useEffect(() => {
    // Simulate loading
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 500);
  }, [selectedPeriod]);

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Analytics & Reports</h1>
        <p className="text-gray-600">Comprehensive insights into hospital operations</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Total Revenue</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-gray-900">$325K</p>
                <p className="text-xs text-green-600 flex items-center mt-1">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +12.5% from last month
                </p>
              </div>
              <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center">
                <DollarSign className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">New Patients</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-gray-900">230</p>
                <p className="text-xs text-green-600 flex items-center mt-1">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +18.2% from last month
                </p>
              </div>
              <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
                <Users className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Appointments</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-gray-900">1,325</p>
                <p className="text-xs text-green-600 flex items-center mt-1">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +8.3% from last month
                </p>
              </div>
              <div className="h-12 w-12 bg-purple-100 rounded-full flex items-center justify-center">
                <Calendar className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Patient Satisfaction</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-gray-900">4.7/5.0</p>
                <p className="text-xs text-green-600 flex items-center mt-1">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +0.3 from last month
                </p>
              </div>
              <div className="h-12 w-12 bg-orange-100 rounded-full flex items-center justify-center">
                <Activity className="h-6 w-6 text-orange-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Tabs */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="revenue">Revenue</TabsTrigger>
          <TabsTrigger value="patients">Patients</TabsTrigger>
          <TabsTrigger value="departments">Departments</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Patient Growth Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Patient Growth Trend</CardTitle>
                <CardDescription>Total and new patients over the last 10 months</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={patientGrowthData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="patients"
                      stackId="1"
                      stroke="#3B82F6"
                      fill="#3B82F6"
                      fillOpacity={0.6}
                      name="Total Patients"
                    />
                    <Area
                      type="monotone"
                      dataKey="newPatients"
                      stackId="2"
                      stroke="#10B981"
                      fill="#10B981"
                      fillOpacity={0.6}
                      name="New Patients"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Appointment Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Appointment Types Distribution</CardTitle>
                <CardDescription>Breakdown of appointments by category</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={appointmentDistribution}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }: any) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {appointmentDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Weekly Appointments */}
          <Card>
            <CardHeader>
              <CardTitle>Weekly Appointment Status</CardTitle>
              <CardDescription>Scheduled, completed, and cancelled appointments this week</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={weeklyAppointments}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="scheduled" fill="#3B82F6" name="Scheduled" />
                  <Bar dataKey="completed" fill="#10B981" name="Completed" />
                  <Bar dataKey="cancelled" fill="#EF4444" name="Cancelled" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Revenue Tab */}
        <TabsContent value="revenue" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Revenue vs Expenses</CardTitle>
              <CardDescription>Monthly financial performance over the last 10 months</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={revenueData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="revenue"
                    stroke="#10B981"
                    strokeWidth={3}
                    name="Revenue"
                  />
                  <Line
                    type="monotone"
                    dataKey="expenses"
                    stroke="#EF4444"
                    strokeWidth={3}
                    name="Expenses"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Avg. Revenue per Patient</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold text-gray-900">$162</p>
                <p className="text-sm text-green-600 mt-1">+5.2% from last month</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Profit Margin</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold text-gray-900">49.2%</p>
                <p className="text-sm text-green-600 mt-1">+2.1% from last month</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Outstanding Bills</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold text-gray-900">$45K</p>
                <p className="text-sm text-red-600 mt-1">+8.5% from last month</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Patients Tab */}
        <TabsContent value="patients" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Patient Growth Analysis</CardTitle>
              <CardDescription>Detailed view of patient acquisition and retention</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={patientGrowthData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="patients"
                    stroke="#3B82F6"
                    strokeWidth={3}
                    name="Total Patients"
                  />
                  <Line
                    type="monotone"
                    dataKey="newPatients"
                    stroke="#10B981"
                    strokeWidth={3}
                    name="New Patients"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Total Patients</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold text-gray-900">2,000</p>
                <p className="text-sm text-gray-600 mt-1">Active patients</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">New This Month</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold text-gray-900">230</p>
                <p className="text-sm text-green-600 mt-1">+18.2% growth</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Retention Rate</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold text-gray-900">92.5%</p>
                <p className="text-sm text-green-600 mt-1">+1.2% from last month</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Avg. Visits/Patient</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold text-gray-900">3.8</p>
                <p className="text-sm text-gray-600 mt-1">This month</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Departments Tab */}
        <TabsContent value="departments" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Department Performance</CardTitle>
              <CardDescription>Patient volume and revenue by department</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={departmentPerformance} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="department" type="category" width={120} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="patients" fill="#3B82F6" name="Patients" />
                  <Bar dataKey="revenue" fill="#10B981" name="Revenue ($)" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {departmentPerformance.slice(0, 3).map((dept) => (
              <Card key={dept.department}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">{dept.department}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Patients:</span>
                    <span className="text-sm font-bold">{dept.patients}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Revenue:</span>
                    <span className="text-sm font-bold">${(dept.revenue / 1000).toFixed(0)}K</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Satisfaction:</span>
                    <span className="text-sm font-bold text-green-600">{dept.satisfaction} ⭐</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
