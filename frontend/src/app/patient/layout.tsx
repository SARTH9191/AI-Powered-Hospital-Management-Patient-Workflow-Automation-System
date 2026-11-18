'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';

export default function PatientLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/loginPage');
    } else if (user?.role !== 'patient') {
      router.push('/loginPage');
    }
  }, [isAuthenticated, user, router]);

  if (!isAuthenticated || user?.role !== 'patient') {
    return null;
  }

  return <>{children}</>;
}
