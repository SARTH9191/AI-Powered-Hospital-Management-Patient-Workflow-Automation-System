'use client';

import { useAuth } from '@/hooks/useAuth';
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';
import { AIChatInterface } from '@/components/chat';
import { Bot } from 'lucide-react';

export default function PatientDashboardNew() {
  const { user } = useAuth();
  const patientId = user?.username || 'patient001';

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <Navbar />
      <div className="flex">
        <Sidebar role="patient" />
        <main className="flex-1 ml-64 mt-16">
          <div className="p-6 md:p-8 lg:p-12 max-w-7xl mx-auto">
            {/* Beautiful Header Section */}
            <div className="mb-8 text-center">
              <div className="flex justify-center mb-4">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full blur-xl opacity-50 animate-pulse"></div>
                  <div className="relative bg-gradient-to-br from-blue-500 to-purple-600 p-4 rounded-full shadow-2xl">
                    <Bot className="h-12 w-12 text-white" />
                  </div>
                </div>
              </div>
              
              {/* <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-3">
                Your AI Healthcare Assistant
              </h1> */}
              
              {/* <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Welcome back, <span className="font-semibold text-blue-600">{user?.name || user?.username || 'Patient'}</span>! 
                Chat with your personal AI assistant for appointments, health queries, and medical support.
              </p> */}
            </div>

            {/* Main Chat Interface - Full Width & Beautiful */}
            <div className="max-w-6xl mx-auto">
                <div className="relative max-w-4xl mx-auto">
                {/* Decorative gradient border */}
                <div className="absolute -inset-1 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 rounded-2xl opacity-20 blur-xl"></div>
                
                {/* Chat Container */}
                <div className="relative bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden">
                  <AIChatInterface 
                  userId={patientId}
                  userRole="patient"
                  height="calc(100vh - 200px)"
                  className="w-full"
                  />
                </div>
                </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
