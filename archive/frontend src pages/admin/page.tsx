'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { Loader2 } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

interface DashboardStats {
  total_patients: number;
  appointments_today: number;
  pending_appointments: number;
  monthly_revenue: number;
  revenue_growth: number;
  pending_lab_tests: number;
  urgent_lab_tests: number;
  patient_growth: number;
}

export default function AdminPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const [stats, setStats] = useState<DashboardStats>({
    total_patients: 0,
    appointments_today: 0,
    pending_appointments: 0,
    monthly_revenue: 0,
    revenue_growth: 0,
    pending_lab_tests: 0,
    urgent_lab_tests: 0,
    patient_growth: 0,
  });
  const [isLoadingStats, setIsLoadingStats] = useState(true);

  useEffect(() => {
    // Initialize auth from localStorage
    useAuthStore.getState().initAuth();
  }, []);

  useEffect(() => {
    // Redirect if not authenticated or not admin
    if (!isAuthenticated) {
      router.push('/loginPage');
    } else if (user && user.role !== 'admin') {
      router.push(`/${user.role}`);
    }
  }, [isAuthenticated, user, router]);

  useEffect(() => {
    if (isAuthenticated && user?.role === 'admin') {
      fetchDashboardStats();
    }
  }, [isAuthenticated, user]);

  const fetchDashboardStats = async () => {
    setIsLoadingStats(true);
    try {
      // Try to fetch from real API
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/api/analytics/dashboard`
      );
      setStats(response.data);
    } catch (error) {
      console.log('Using mock data - API not available');
      // Use mock data if API fails
      setStats({
        total_patients: 1234,
        appointments_today: 42,
        pending_appointments: 8,
        monthly_revenue: 245000,
        revenue_growth: 18,
        pending_lab_tests: 23,
        urgent_lab_tests: 5,
        patient_growth: 12,
      });
    } finally {
      setIsLoadingStats(false);
    }
  };

  if (!isAuthenticated || !user || user.role !== 'admin') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="p-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Admin Dashboard</h1>
        <p className="text-gray-600 mb-8">Welcome back, {user.username}!</p>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Patients */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Patients</p>
                {isLoadingStats ? (
                  <div className="h-10 w-20 bg-gray-200 animate-pulse rounded mt-2"></div>
                ) : (
                  <>
                    <p className="text-3xl font-bold text-gray-900 mt-2">
                      {stats.total_patients.toLocaleString()}
                    </p>
                    <p className="text-sm text-green-600 mt-2">
                      +{stats.patient_growth}% from last month
                    </p>
                  </>
                )}
              </div>
              <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
                <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
            </div>
          </div>

          {/* Appointments Today */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Appointments Today</p>
                {isLoadingStats ? (
                  <div className="h-10 w-16 bg-gray-200 animate-pulse rounded mt-2"></div>
                ) : (
                  <>
                    <p className="text-3xl font-bold text-gray-900 mt-2">
                      {stats.appointments_today}
                    </p>
                    <p className="text-sm text-blue-600 mt-2">
                      {stats.pending_appointments} pending approval
                    </p>
                  </>
                )}
              </div>
              <div className="h-12 w-12 bg-purple-100 rounded-full flex items-center justify-center">
                <svg className="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
          </div>

          {/* Revenue (Month) */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Revenue (Month)</p>
                {isLoadingStats ? (
                  <div className="h-10 w-24 bg-gray-200 animate-pulse rounded mt-2"></div>
                ) : (
                  <>
                    <p className="text-3xl font-bold text-gray-900 mt-2">
                      ${(stats.monthly_revenue / 1000).toFixed(0)}K
                    </p>
                    <p className="text-sm text-green-600 mt-2">
                      +{stats.revenue_growth}% from last month
                    </p>
                  </>
                )}
              </div>
              <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center">
                <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          {/* Pending Lab Tests */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Pending Lab Tests</p>
                {isLoadingStats ? (
                  <div className="h-10 w-16 bg-gray-200 animate-pulse rounded mt-2"></div>
                ) : (
                  <>
                    <p className="text-3xl font-bold text-gray-900 mt-2">
                      {stats.pending_lab_tests}
                    </p>
                    <p className="text-sm text-orange-600 mt-2">
                      {stats.urgent_lab_tests} urgent
                    </p>
                  </>
                )}
              </div>
              <div className="h-12 w-12 bg-orange-100 rounded-full flex items-center justify-center">
                <svg className="h-6 w-6 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => router.push('/admin/users')}
              className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-blue-300 transition-colors"
            >
              <div className="h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                <svg className="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                </svg>
              </div>
              <div className="text-left">
                <p className="font-medium text-gray-900">Add New User</p>
                <p className="text-sm text-gray-500">Create doctor/staff account</p>
              </div>
            </button>

            <button
              onClick={() => router.push('/admin/analytics')}
              className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-purple-300 transition-colors"
            >
              <div className="h-10 w-10 bg-purple-100 rounded-full flex items-center justify-center mr-3">
                <svg className="h-5 w-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div className="text-left">
                <p className="font-medium text-gray-900">View Analytics</p>
                <p className="text-sm text-gray-500">Detailed reports & charts</p>
              </div>
            </button>

            <button
              onClick={() => router.push('/admin/settings')}
              className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-green-300 transition-colors"
            >
              <div className="h-10 w-10 bg-green-100 rounded-full flex items-center justify-center mr-3">
                <svg className="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <div className="text-left">
                <p className="font-medium text-gray-900">System Settings</p>
                <p className="text-sm text-gray-500">Configure hospital system</p>
              </div>
            </button>
          </div>
        </div>

        {/* Recent Activity Feed */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h2>
          <div className="space-y-4">
            {[
              {
                type: 'appointment',
                icon: '📅',
                color: 'bg-blue-100 text-blue-600',
                title: 'New Appointment Scheduled',
                description: 'Dr. Sarah Johnson with patient John Doe',
                time: '5 minutes ago',
              },
              {
                type: 'lab',
                icon: '🧪',
                color: 'bg-purple-100 text-purple-600',
                title: 'Lab Results Ready',
                description: 'Blood test results for patient ID #1234',
                time: '12 minutes ago',
              },
              {
                type: 'billing',
                icon: '💰',
                color: 'bg-green-100 text-green-600',
                title: 'Payment Received',
                description: '$450.00 from patient Mary Smith',
                time: '25 minutes ago',
              },
              {
                type: 'user',
                icon: '👤',
                color: 'bg-orange-100 text-orange-600',
                title: 'New User Created',
                description: 'Staff member Mike Brown added to system',
                time: '1 hour ago',
              },
              {
                type: 'approval',
                icon: '✅',
                color: 'bg-green-100 text-green-600',
                title: 'Prescription Approved',
                description: 'Dr. John Smith approved medication for patient',
                time: '2 hours ago',
              },
              {
                type: 'emergency',
                icon: '🚨',
                color: 'bg-red-100 text-red-600',
                title: 'Emergency Check-in',
                description: 'Patient admitted to emergency department',
                time: '3 hours ago',
              },
            ].map((activity, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 hover:bg-gray-50 rounded-lg transition-colors">
                <div className={`h-10 w-10 ${activity.color} rounded-full flex items-center justify-center flex-shrink-0 text-xl`}>
                  {activity.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">{activity.title}</p>
                  <p className="text-sm text-gray-600 truncate">{activity.description}</p>
                  <p className="text-xs text-gray-400 mt-1">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 pt-4 border-t border-gray-200">
            <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">
              View All Activity →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
