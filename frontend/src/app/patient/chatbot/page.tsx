'use client';

import { useState, useRef, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/hooks/useAuth';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';
import {
  Send,
  Bot,
  User,
  Calendar,
  Pill,
  TestTube,
  FileText,
  Clock,
  Loader2,
  MessageSquare,
  Sparkles,
  Heart,
  Activity,
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

interface Message {
  message_id: string;
  conversation_id: string;
  user_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: any;
}

interface QuickAction {
  id: string;
  label: string;
  prompt: string;
  icon: React.ReactNode;
  color: string;
}

export default function PatientChatbot() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const patientId = 'patient001'; // TODO: Get from authenticated user
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  // Quick actions
  const quickActions: QuickAction[] = [
    {
      id: 'appointments',
      label: 'Book Appointment',
      prompt: 'I would like to book an appointment',
      icon: <Calendar className="h-4 w-4" />,
      color: 'bg-blue-100 text-blue-700 hover:bg-blue-200',
    },
    {
      id: 'medications',
      label: 'Refill Medication',
      prompt: 'I need to refill my medication',
      icon: <Pill className="h-4 w-4" />,
      color: 'bg-purple-100 text-purple-700 hover:bg-purple-200',
    },
    {
      id: 'lab-results',
      label: 'Check Lab Results',
      prompt: 'Can you show me my latest lab results?',
      icon: <TestTube className="h-4 w-4" />,
      color: 'bg-green-100 text-green-700 hover:bg-green-200',
    },
    {
      id: 'symptoms',
      label: 'Report Symptoms',
      prompt: 'I need to report some symptoms',
      icon: <Activity className="h-4 w-4" />,
      color: 'bg-red-100 text-red-700 hover:bg-red-200',
    },
  ];

  // Fetch chat history
  const { data: messagesData, isLoading } = useQuery({
    queryKey: ['chat-messages', patientId],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `http://localhost:8000/api/agent/chat/history/${patientId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data?.data?.messages || [];
    },
    enabled: !!patientId,
  });

  const messages = messagesData || [];

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: async (message: string) => {
      const token = localStorage.getItem('access_token');
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      setIsTyping(true);
      const response = await axios.post(
        'http://localhost:8000/api/workflow/chat/message',
        {
          message: message,
          user_id: user.username || patientId,
          user_role: user.role || 'patient',
          workflow_id: messages[0]?.conversation_id || undefined,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chat-messages'] });
      setInputMessage('');
      setIsTyping(false);
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to send message');
      setIsTyping(false);
    },
  });

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSendMessage = () => {
    if (!inputMessage.trim()) {
      toast.error('Please enter a message');
      return;
    }
    sendMessageMutation.mutate(inputMessage);
  };

  const handleQuickAction = (prompt: string) => {
    setInputMessage(prompt);
    sendMessageMutation.mutate(prompt);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

    if (diffInHours < 1) {
      const diffInMinutes = Math.floor(diffInHours * 60);
      return diffInMinutes === 0 ? 'Just now' : `${diffInMinutes}m ago`;
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}h ago`;
    } else {
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar role="patient" />
        <main className="flex-1 ml-64 mt-16">
          <div className="h-[calc(100vh-4rem)] flex flex-col">
            {/* Header */}
            <div className="p-6 bg-white border-b">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900 mb-2">Medical Assistant</h1>
                  <p className="text-gray-600">Chat with your AI health assistant for instant help</p>
                </div>
                <div className="flex items-center space-x-2 px-4 py-2 bg-green-100 rounded-full">
                  <div className="h-2 w-2 bg-green-600 rounded-full animate-pulse"></div>
                  <span className="text-sm font-medium text-green-700">AI Online</span>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="p-6 bg-white border-b">
              <div className="flex items-center space-x-2 mb-3">
                <Sparkles className="h-5 w-5 text-purple-600" />
                <h2 className="text-sm font-semibold text-gray-700">Quick Actions</h2>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {quickActions.map((action) => (
                  <Button
                    key={action.id}
                    variant="outline"
                    className={`justify-start ${action.color} border-none`}
                    onClick={() => handleQuickAction(action.prompt)}
                    disabled={sendMessageMutation.isPending}
                  >
                    {action.icon}
                    <span className="ml-2 text-sm font-medium">{action.label}</span>
                  </Button>
                ))}
              </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 p-6 bg-gradient-to-b from-gray-50 to-white overflow-y-auto">
              {isLoading ? (
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="flex items-start space-x-3">
                      <Skeleton className="h-10 w-10 rounded-full" />
                      <div className="flex-1 space-y-2">
                        <Skeleton className="h-4 w-3/4" />
                        <Skeleton className="h-4 w-1/2" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center">
                  <div className="mb-6 p-6 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full">
                    <Bot className="h-16 w-16 text-blue-600" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">
                    Welcome to Your Medical Assistant!
                  </h3>
                  <p className="text-gray-600 mb-6 max-w-md">
                    I'm here to help you with appointments, medications, lab results, and general health questions.
                    Start a conversation below or use a quick action above.
                  </p>
                  <div className="flex items-center space-x-2 text-sm text-gray-500">
                    <Heart className="h-4 w-4 text-red-500" />
                    <span>Available 24/7 for your healthcare needs</span>
                  </div>
                </div>
              ) : (
                <div className="space-y-6 max-w-4xl mx-auto">
                  {messages.map((message: Message) => (
                    <div
                      key={message.message_id}
                      className={`flex items-start space-x-3 ${
                        message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                      }`}
                    >
                      {/* Avatar */}
                      <Avatar className={`h-10 w-10 ${message.role === 'user' ? 'bg-blue-600' : 'bg-purple-600'}`}>
                        <AvatarFallback>
                          {message.role === 'user' ? (
                            <User className="h-5 w-5 text-white" />
                          ) : (
                            <Bot className="h-5 w-5 text-white" />
                          )}
                        </AvatarFallback>
                      </Avatar>

                      {/* Message Content */}
                      <div className={`flex-1 ${message.role === 'user' ? 'flex justify-end' : ''}`}>
                        <div
                          className={`inline-block max-w-[80%] rounded-2xl px-4 py-3 ${
                            message.role === 'user'
                              ? 'bg-blue-600 text-white'
                              : 'bg-white border border-gray-200 text-gray-900 shadow-sm'
                          }`}
                        >
                          <div className="flex items-center space-x-2 mb-1">
                            <span className="text-xs font-semibold">
                              {message.role === 'user' ? 'You' : 'Medical Assistant'}
                            </span>
                            <span
                              className={`text-xs ${
                                message.role === 'user' ? 'text-blue-200' : 'text-gray-500'
                              }`}
                            >
                              {formatTimestamp(message.timestamp)}
                            </span>
                          </div>
                          <p className="text-sm leading-relaxed whitespace-pre-wrap">
                            {message.content}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}

                  {/* Typing Indicator */}
                  {isTyping && (
                    <div className="flex items-start space-x-3">
                      <Avatar className="h-10 w-10 bg-purple-600">
                        <AvatarFallback>
                          <Bot className="h-5 w-5 text-white" />
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <div className="inline-block bg-white border border-gray-200 rounded-2xl px-4 py-3 shadow-sm">
                          <div className="flex items-center space-x-2">
                            <div className="flex space-x-1">
                              <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce"></div>
                              <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                              <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
                            </div>
                            <span className="text-xs text-gray-500">AI is typing...</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </div>
              )}
            </div>

            {/* Input Area */}
            <div className="p-6 bg-white border-t">
              <div className="max-w-4xl mx-auto">
                <div className="flex items-end space-x-3">
                  <div className="flex-1">
                    <Input
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Type your message here... (Press Enter to send)"
                      disabled={sendMessageMutation.isPending}
                      className="resize-none h-12 text-base"
                    />
                  </div>
                  <Button
                    onClick={handleSendMessage}
                    disabled={sendMessageMutation.isPending || !inputMessage.trim()}
                    size="lg"
                    className="h-12 px-6"
                  >
                    {sendMessageMutation.isPending ? (
                      <>
                        <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                        Sending...
                      </>
                    ) : (
                      <>
                        <Send className="h-5 w-5 mr-2" />
                        Send
                      </>
                    )}
                  </Button>
                </div>

                {/* Info Text */}
                <div className="mt-3 flex items-center justify-center space-x-2 text-xs text-gray-500">
                  <MessageSquare className="h-3 w-3" />
                  <span>
                    This AI assistant can help with appointments, prescriptions, lab results, and health questions
                  </span>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
