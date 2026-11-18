'use client';

import { ReactNode } from 'react';
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';

export default function AdminLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar role="admin" />
        <main className="flex-1 ml-64">
          {children}
        </main>
      </div>
    </div>
  );
}
