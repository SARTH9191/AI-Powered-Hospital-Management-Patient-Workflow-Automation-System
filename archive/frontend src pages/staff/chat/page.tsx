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
  DollarSign,
  FileText,
  Clock,
  Loader2,
  MessageSquare,
  Sparkles,
  Activity,
  UserCheck,
  Phone,
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

export default function StaffChat() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const staffId = user?.username || 'staff';
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  // Staff-specific quick actions
  const quickActions: QuickAction[] = [
    {
      id: 'check-in',
      label: 'Patient Check-In',
      prompt: 'Show me today\'s pending check-ins',
      icon: <UserCheck className="h-4 w-4" />,
      color: 'bg-green-100 text-green-700 hover:bg-green-200',
    },
    {
      id: 'payment-request',
      label: 'Payment Request',
      prompt: 'I need to send a payment request',
      icon: <DollarSign className="h-4 w-4" />,
      color: 'bg-blue-100 text-blue-700 hover:bg-blue-200',
    },
    {
      id: 'schedule',
      label: 'Schedule Appointment',
      prompt: 'Schedule an appointment for a patient',
      icon: <Calendar className="h-4 w-4" />,
      color: 'bg-purple-100 text-purple-700 hover:bg-purple-200',
    },
    {
      id: 'documents',
      label: 'Upload Documents',
      prompt: 'I need to upload patient documents',
      icon: <FileText className="h-4 w-4" />,
      color: 'bg-orange-100 text-orange-700 hover:bg-orange-200',
    },
  ];

  // Chat messages (local state - history endpoint doesn't exist yet)
  const [messages, setMessages] = useState<Message[]>([]);
  const isLoading = false;

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
          user_id: user.username || staffId,
          user_role: 'staff',
          // Staff should NEVER send workflow_id - they get quick answers only
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data;
    },
    onSuccess: (data) => {
      // Add user message
      const userMsg: Message = {
        message_id: Date.now().toString(),
        conversation_id: 'staff-' + staffId,
        user_id: staffId,
        role: 'user',
        content: inputMessage,
        timestamp: new Date().toISOString(),
      };
      
      // Add AI response
      const aiMsg: Message = {
        message_id: (Date.now() + 1).toString(),
        conversation_id: 'staff-' + staffId,
        user_id: 'assistant',
        role: 'assistant',
        content: data.response || 'I processed your request.',
        timestamp: new Date().toISOString(),
      };
      
      setMessages(prev => [...prev, userMsg, aiMsg]);
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

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar role="staff" />
      <div className="flex-1 flex flex-col">
        <Navbar />
        <main className="flex-1 overflow-hidden p-6">
          <div className="max-w-6xl mx-auto h-full flex flex-col">
            {/* Header */}
            <div className="mb-6">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
                    <MessageSquare className="h-8 w-8 text-purple-600" />
                    Staff AI Assistant
                  </h1>
                  <p className="text-gray-600 mt-1">
                    Manage check-ins, appointments, billing, and administrative tasks
                  </p>
                </div>
                <Badge variant="outline" className="flex items-center gap-2">
                  <Activity className="h-4 w-4 animate-pulse text-green-600" />
                  Online
                </Badge>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="mb-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {quickActions.map((action) => (
                  <Button
                    key={action.id}
                    variant="outline"
                    className={`h-auto py-3 px-4 flex flex-col items-start gap-2 ${action.color}`}
                    onClick={() => handleQuickAction(action.prompt)}
                  >
                    <div className="flex items-center gap-2">
                      {action.icon}
                      <span className="font-medium text-sm">{action.label}</span>
                    </div>
                  </Button>
                ))}
              </div>
            </div>

            {/* Chat Area */}
            <Card className="flex-1 flex flex-col overflow-hidden">
              <CardHeader className="border-b bg-white">
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-purple-600" />
                  AI-Powered Staff Assistant
                </CardTitle>
                <CardDescription>
                  Ask me to check-in patients, send payment requests, schedule appointments, upload documents, and more
                </CardDescription>
              </CardHeader>
              <CardContent className="flex-1 overflow-y-auto p-6">
                {isLoading ? (
                  <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                      <Skeleton key={i} className="h-20 w-full" />
                    ))}
                  </div>
                ) : messages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-center">
                    <Bot className="h-16 w-16 text-gray-300 mb-4" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      Start a Conversation
                    </h3>
                    <p className="text-gray-600 max-w-md mb-6">
                      I can help you with patient check-ins, billing, scheduling, and administrative tasks. Try the quick actions above or type your request below.
                    </p>
                    <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 max-w-md">
                      <p className="text-sm text-purple-800 font-medium mb-2">
                        💡 Try asking:
                      </p>
                      <ul className="text-sm text-purple-700 space-y-1 text-left">
                        <li>• "Check in patient PAT2025001 for appointment"</li>
                        <li>• "Send payment request of ₹5000 to PAT2025001"</li>
                        <li>• "Show me today's pending check-ins"</li>
                        <li>• "Schedule appointment with Dr. Sharma tomorrow"</li>
                      </ul>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {messages.map((msg: Message, index: number) => (
                      <div
                        key={msg.message_id || index}
                        className={`flex gap-3 ${
                          msg.role === 'user' ? 'justify-end' : 'justify-start'
                        }`}
                      >
                        {msg.role === 'assistant' && (
                          <Avatar className="h-8 w-8 bg-gradient-to-br from-purple-500 to-pink-600">
                            <AvatarFallback>
                              <Bot className="h-5 w-5 text-white" />
                            </AvatarFallback>
                          </Avatar>
                        )}
                        <div
                          className={`max-w-[70%] rounded-lg px-4 py-3 ${
                            msg.role === 'user'
                              ? 'bg-purple-600 text-white'
                              : 'bg-white border border-gray-200'
                          }`}
                        >
                          <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                          <p
                            className={`text-xs mt-1 ${
                              msg.role === 'user' ? 'text-purple-100' : 'text-gray-500'
                            }`}
                          >
                            {new Date(msg.timestamp).toLocaleTimeString()}
                          </p>
                        </div>
                        {msg.role === 'user' && (
                          <Avatar className="h-8 w-8 bg-purple-600">
                            <AvatarFallback>
                              <User className="h-5 w-5 text-white" />
                            </AvatarFallback>
                          </Avatar>
                        )}
                      </div>
                    ))}
                    {isTyping && (
                      <div className="flex gap-3 justify-start">
                        <Avatar className="h-8 w-8 bg-gradient-to-br from-purple-500 to-pink-600">
                          <AvatarFallback>
                            <Bot className="h-5 w-5 text-white" />
                          </AvatarFallback>
                        </Avatar>
                        <div className="bg-white border border-gray-200 rounded-lg px-4 py-3">
                          <div className="flex gap-1">
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                            <div
                              className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                              style={{ animationDelay: '0.2s' }}
                            />
                            <div
                              className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                              style={{ animationDelay: '0.4s' }}
                            />
                          </div>
                        </div>
                      </div>
                    )}
                    <div ref={messagesEndRef} />
                  </div>
                )}
              </CardContent>

              {/* Input Area */}
              <div className="border-t bg-white p-4">
                <div className="flex gap-2">
                  <Input
                    placeholder="Type your request... (e.g., 'Send payment request of ₹5000 to PAT2025001')"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSendMessage();
                      }
                    }}
                    disabled={sendMessageMutation.isPending}
                    className="flex-1"
                  />
                  <Button
                    onClick={handleSendMessage}
                    disabled={sendMessageMutation.isPending || !inputMessage.trim()}
                    className="bg-purple-600 hover:bg-purple-700"
                  >
                    {sendMessageMutation.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Send className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}
