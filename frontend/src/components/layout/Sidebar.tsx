'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Users,
  Calendar,
  FileText,
  DollarSign,
  Activity,
  Settings,
  BarChart3,
  CheckSquare,
  Bot,
  Stethoscope,
  TestTube,
  Pill,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuthStore } from '@/store/authStore';

interface SidebarProps {
  role?: 'admin' | 'doctor' | 'staff' | 'patient';
}

export default function Sidebar({ role: propRole }: SidebarProps) {
  const pathname = usePathname();
  const { user } = useAuthStore();
  
  // Use prop role if provided, otherwise get from store
  const role = propRole || user?.role || 'admin';

  // Define navigation items based on role
  const getNavItems = () => {
    if (role === 'admin') {
      return [
        { icon: LayoutDashboard, label: 'Dashboard', href: '/admin' },
        { icon: Users, label: 'User Management', href: '/admin/users' },
        { icon: BarChart3, label: 'Analytics', href: '/admin/analytics' },
        { icon: Activity, label: 'AI Agent Monitor', href: '/admin/agent' },
        { icon: CheckSquare, label: 'Approvals', href: '/admin/approvals' },
        { icon: Calendar, label: 'Appointments', href: '/admin/appointments' },
        { icon: TestTube, label: 'Lab Tests', href: '/admin/labs' },
        { icon: Pill, label: 'Pharmacy', href: '/admin/pharmacy' },
        { icon: FileText, label: 'Reports', href: '/admin/reports' },
        { icon: Settings, label: 'Settings', href: '/admin/settings' },
      ];
    } else if (role === 'doctor') {
      return [
        { icon: LayoutDashboard, label: 'Dashboard', href: '/doctor' },
        { icon: Users, label: 'My Patients', href: '/doctor/patients' },
        { icon: Calendar, label: 'Appointments', href: '/doctor/appointments' },
        { icon: CheckSquare, label: 'Approvals', href: '/doctor/approvals' },
        { icon: TestTube, label: 'Lab Results', href: '/doctor/labs' },
        { icon: Pill, label: 'Prescriptions', href: '/doctor/prescriptions' },
        { icon: FileText, label: 'Medical Records', href: '/doctor/records' },
      ];
    } else if (role === 'staff') {
      return [
        { icon: LayoutDashboard, label: 'Dashboard', href: '/staff' },
        { icon: Users, label: 'Patient Registration', href: '/staff/registration' },
        { icon: Calendar, label: 'Scheduling', href: '/staff/scheduling' },
        { icon: DollarSign, label: 'Billing', href: '/staff/billing' },
        { icon: TestTube, label: 'Lab & Pharmacy', href: '/staff/lab-pharmacy' },
      ];
    } else {
      // Patient
      return [
        { icon: LayoutDashboard, label: 'Dashboard', href: '/patient' },
        { icon: Calendar, label: 'My Appointments', href: '/patient/appointments' },
        { icon: Stethoscope, label: 'Health Records', href: '/patient/records' },
        { icon: TestTube, label: 'Lab Results', href: '/patient/labs' },
        { icon: Pill, label: 'Medications', href: '/patient/medications' },
        { icon: DollarSign, label: 'Billing', href: '/patient/billing' },
        { icon: Bot, label: 'AI Assistant', href: '/patient/chatbot' },
      ];
    }
  };

  const navItems = getNavItems();

  return (
    <aside className="fixed left-0 top-16 h-[calc(100vh-4rem)] w-64 bg-white border-r border-gray-200 overflow-y-auto">
      <nav className="p-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors',
                isActive
                  ? 'bg-blue-50 text-blue-600 font-medium'
                  : 'text-gray-700 hover:bg-gray-100'
              )}
            >
              <Icon className="h-5 w-5" />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 bg-white">
        <div className="flex items-center space-x-2 text-xs text-gray-500">
          <Bot className="h-4 w-4" />
          <span>AI Agent Active</span>
          <span className="ml-auto h-2 w-2 bg-green-500 rounded-full"></span>
        </div>
      </div>
    </aside>
  );
}
