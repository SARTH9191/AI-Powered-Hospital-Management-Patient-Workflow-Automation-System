'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Hospital, Chrome } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuthStore } from '@/store/authStore';

export default function LoginPage() {
  const router = useRouter();
  const { setToken, setUser } = useAuthStore();

  // Check if user is already logged in
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    const storedToken = localStorage.getItem('access_token');
    
    if (storedUser && storedToken) {
      try {
        const user = JSON.parse(storedUser);
        setUser(user);
        setToken(storedToken);
        router.push('/patient/dashboard');
      } catch (error) {
        console.error('Error parsing stored user:', error);
        localStorage.removeItem('user');
        localStorage.removeItem('access_token');
      }
    }
  }, [router, setUser, setToken]);

  // Handle Google OAuth login
  const handleGoogleLogin = () => {
    // Redirect to backend Google OAuth
    window.location.href = 'http://localhost:8000/login';
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-4">
      <Card className="w-full max-w-lg shadow-2xl border-0">
        <CardHeader className="text-center space-y-6 pb-8">
          <div className="flex justify-center">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full blur-xl opacity-50"></div>
              <div className="relative h-20 w-20 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center shadow-lg">
                <Hospital className="h-10 w-10 text-white" />
              </div>
            </div>
          </div>
          <div>
            <CardTitle className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              City Hospital AI
            </CardTitle>
            <CardDescription className="text-lg text-gray-600 mt-2">
              Your Personal Healthcare Assistant
            </CardDescription>
          </div>
        </CardHeader>

        <CardContent className="space-y-6 pb-8">
          {/* Google OAuth Button - Primary */}
          <Button 
            onClick={handleGoogleLogin}
            className="w-full h-14 text-lg bg-white hover:bg-gray-50 text-gray-800 border-2 border-gray-200 shadow-md hover:shadow-lg transition-all"
            size="lg"
          >
            <div className="flex items-center justify-center gap-3">
              <Chrome className="h-6 w-6 text-blue-600" />
              <span className="font-semibold">Continue with Google</span>
            </div>
          </Button>

          {/* Features */}
          <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-6 space-y-4">
            <h3 className="font-semibold text-gray-800 text-center mb-4">
              🏥 Complete Healthcare Journey
            </h3>
            <div className="grid grid-cols-2 gap-4 text-sm text-gray-700">
              <div className="flex items-center gap-2">
                <span className="text-green-600">✅</span>
                <span>Patient Registration</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-600">✅</span>
                <span>Medical History</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-600">✅</span>
                <span>Lab Test Scheduling</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-600">✅</span>
                <span>Doctor Consultation</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-600">✅</span>
                <span>Treatment Monitoring</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-600">✅</span>
                <span>Follow-up Care</span>
              </div>
            </div>
          </div>

          {/* Security Note */}
          <div className="text-center text-sm text-gray-500 space-y-1">
            <p className="flex items-center justify-center gap-2">
              <span className="text-blue-600">🔒</span>
              Secure Google Authentication
            </p>
            <p className="flex items-center justify-center gap-2">
              <span className="text-purple-600">🤖</span>
              AI-Powered Medical Assistance
            </p>
            <p className="flex items-center justify-center gap-2">
              <span className="text-green-600">💾</span>
              Your Medical History Saved Securely
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
