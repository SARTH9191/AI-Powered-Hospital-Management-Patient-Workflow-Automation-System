'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';

export default function Home() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated, isLoading, setToken } = useAuthStore();

  useEffect(() => {
    // Check if token is in URL (from OAuth callback)
    const token = searchParams.get('token');
    const error = searchParams.get('error');
    
    if (error) {
      console.error('OAuth error:', error);
      alert(`Login failed: ${error}`);
      router.push('/loginPage');
      return;
    }
    
    if (token) {
      console.log('✅ OAuth token received, storing...');
      // Store token and redirect to dashboard
      setToken(token);
      router.push('/patient/dashboard');
      return;
    }
    
    // Normal flow - check if already authenticated
    if (!isLoading) {
      // Only redirect to dashboard if authenticated, otherwise to login
      if (isAuthenticated) {
        router.push('/patient/dashboard');
      } else {
        router.push('/loginPage');
      }
    }
  }, [isAuthenticated, isLoading, router, searchParams, setToken]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <Loader2 className="h-8 w-8 animate-spin mx-auto text-blue-600" />
        <p className="mt-4 text-gray-600">Redirecting...</p>
      </div>
    </div>
  );
}
