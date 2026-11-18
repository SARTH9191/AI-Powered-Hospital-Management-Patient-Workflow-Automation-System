'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';

export default function StaffLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/loginPage');
    } else if (user?.role !== 'staff') {
      router.push('/loginPage');
    }
  }, [isAuthenticated, user, router]);

  if (!isAuthenticated || user?.role !== 'staff') {
    return null;
  }

  return <>{children}</>;
}
