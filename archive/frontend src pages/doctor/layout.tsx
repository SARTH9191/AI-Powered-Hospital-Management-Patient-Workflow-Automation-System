'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { Loader2 } from 'lucide-react';

export default function DoctorLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();

  useEffect(() => {
    useAuthStore.getState().initAuth();
  }, []);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/loginPage');
    } else if (user && user.role !== 'doctor') {
      router.push(`/${user.role}`);
    }
  }, [isAuthenticated, user, router]);

  if (!isAuthenticated || !user || user.role !== 'doctor') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return <>{children}</>;
}
