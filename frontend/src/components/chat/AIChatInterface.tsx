"use client";

import React, { useState, useRef, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { Bot, User, Send, Loader2, CheckCircle, AlertCircle, Clock } from "lucide-react";
import { apiClient } from '@/lib/api-client';
import { useToast } from "@/hooks/use-toast";
import { format } from 'date-fns';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  status?: 'sending' | 'sent' | 'error';
  toolCalls?: Array<{
    tool: string;
    status: 'running' | 'completed' | 'failed';
    result?: string;
  }>;
}

interface Workflow {
  workflow_id: string;
  patient_id?: string;
  status: 'active' | 'completed' | 'failed';
  current_stage: string;
  created_at: string;
  messages: Message[];
}

interface AIChatInterfaceProps {
  userId?: string;
  userRole?: 'patient' | 'doctor' | 'staff' | 'admin';
  workflowId?: string;
  onWorkflowCreated?: (workflowId: string) => void;
  className?: string;
  height?: string;
}

export function AIChatInterface({ 
  userId, 
  userRole = 'patient',
  workflowId: initialWorkflowId,
  onWorkflowCreated,
  className = "",
  height = "600px"
}: AIChatInterfaceProps) {
  const [currentWorkflowId, setCurrentWorkflowId] = useState<string | null>(initialWorkflowId || null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isSessionRestored, setIsSessionRestored] = useState(false);
  const [inputMessage, setInputMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: getWelcomeMessage(userRole),
      timestamp: new Date().toISOString(),
      status: 'sent'
    }
  ]);
  
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // 🔄 SESSION PERSISTENCE: Initialize or restore session on mount
  useEffect(() => {
    const initializeSession = async () => {
      // Try to get existing session from localStorage
      let storedSessionId = localStorage.getItem('hospital_session_id');
      
      if (!storedSessionId) {
        // Generate new session ID
        storedSessionId = `session-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
        localStorage.setItem('hospital_session_id', storedSessionId);
        console.log('🆕 Created new session:', storedSessionId);
      } else {
        console.log('♻️ Restored existing session:', storedSessionId);
        
        // Try to restore workflow state from backend
        try {
          const response = await apiClient.get('/api/ai-chat/greeting', {
            params: { session_id: storedSessionId }
          });
          
          if (response.data && response.data.greeting) {
            // Update messages with greeting (which includes restored state info)
            setMessages([{
              id: '1',
              role: 'assistant',
              content: response.data.greeting,
              timestamp: new Date().toISOString(),
              status: 'sent'
            }]);
            
            // Update workflow info
            if (response.data.patient_id) {
              setCurrentWorkflowId(response.data.patient_id);
              setIsSessionRestored(true);
              onWorkflowCreated?.(response.data.patient_id);
              
              toast({
                title: "Session Restored",
                description: `Welcome back! Continuing from Stage ${response.data.current_stage}`,
              });
            }
            
            console.log('✅ Session restored from backend:', {
              stage: response.data.current_stage,
              patient_id: response.data.patient_id
            });
          }
        } catch (error) {
          console.log('ℹ️ No previous session to restore, starting fresh');
        }
      }
      
      setSessionId(storedSessionId);
    };
    
    initializeSession();
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Send chat message mutation (using NEW workflow chat agent API)
  const sendMessageMutation = useMutation({
    mutationFn: async (messageText: string) => {
      // Use the NEW WorkflowChatAgent API endpoint with session persistence
      const response = await apiClient.post('/api/ai-chat/chat', {
        message: messageText,
        session_id: sessionId || undefined  // 🔄 Include session ID for restoration
      });
      return response.data;
    },
    onSuccess: (data) => {
      // 🔄 Store session_id returned from backend (if different)
      if (data.session_id && data.session_id !== sessionId) {
        localStorage.setItem('hospital_session_id', data.session_id);
        setSessionId(data.session_id);
        console.log('💾 Updated session ID:', data.session_id);
      }
      
      // Store patient ID if received
      if (data.patient_id && !currentWorkflowId) {
        setCurrentWorkflowId(data.patient_id);
        onWorkflowCreated?.(data.patient_id);
      }
      
      // Add AI response with workflow info
      const aiMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: data.response,
        timestamp: data.timestamp || new Date().toISOString(),
        status: 'sent',
        toolCalls: data.tool_calls
      };
      setMessages(prev => [...prev, aiMessage]);
      
      // Show workflow notification if workflow was triggered
      if (data.workflow_triggered && !currentWorkflowId) {
        toast({
          title: "Workflow Started",
          description: `Your ${data.current_stage || 'request'} is being processed`,
        });
      }
    },
    onError: (error: any) => {
      toast({
        title: "Error sending message",
        description: error.response?.data?.detail || "Failed to send message",
        variant: "destructive"
      });
      
      // Mark last user message as error
      setMessages(prev => prev.map((msg, idx) => 
        idx === prev.length - 1 && msg.role === 'user' ? { ...msg, status: 'error' as const } : msg
      ));
    }
  });

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    // Add user message to chat
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
      status: 'sending'
    };
    
    setMessages(prev => [...prev, userMessage]);
    const messageToSend = inputMessage;
    setInputMessage("");
    inputRef.current?.focus();

    // Send to unified chat endpoint (handles both new and existing conversations)
    await sendMessageMutation.mutateAsync(messageToSend);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Card className={`flex flex-col ${className}`} style={{ height }}>
      <CardHeader className="border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot className="h-5 w-5 text-blue-600" />
            <CardTitle>AI Healthcare Assistant</CardTitle>
          </div>
          {currentWorkflowId && (
            <Badge variant="outline" className="text-xs">
              <Clock className="h-3 w-3 mr-1" />
              {isSessionRestored ? 'Session Restored' : 'Active Session'}
            </Badge>
          )}
          {sessionId && !currentWorkflowId && (
            <Badge variant="secondary" className="text-xs">
              Session ID: {sessionId.slice(0, 12)}...
            </Badge>
          )}
        </div>
        <CardDescription>
          {getRoleDescription(userRole)}
        </CardDescription>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
        {/* Messages Area */}
        <ScrollArea className="flex-1 p-4">
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${
                  message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                }`}
              >
                {/* Avatar */}
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  message.role === 'user' 
                    ? 'bg-blue-100 text-blue-600' 
                    : 'bg-green-100 text-green-600'
                }`}>
                  {message.role === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                </div>

                {/* Message Content */}
                <div className={`flex-1 ${message.role === 'user' ? 'text-right' : 'text-left'}`}>
                  <div className={`inline-block max-w-[80%] rounded-lg p-3 ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}>
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    
                    {/* Tool Calls */}
                    {message.toolCalls && message.toolCalls.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-gray-300 space-y-1">
                        {message.toolCalls.map((tool, idx) => (
                          <div key={idx} className="flex items-center gap-2 text-xs">
                            {tool.status === 'running' && <Loader2 className="h-3 w-3 animate-spin" />}
                            {tool.status === 'completed' && <CheckCircle className="h-3 w-3 text-green-500" />}
                            {tool.status === 'failed' && <AlertCircle className="h-3 w-3 text-red-500" />}
                            <span className="opacity-75">{tool.tool}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  {/* Timestamp & Status */}
                  <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                    <span>{format(new Date(message.timestamp), 'HH:mm')}</span>
                    {message.status === 'sending' && <Loader2 className="h-3 w-3 animate-spin" />}
                    {message.status === 'sent' && <CheckCircle className="h-3 w-3" />}
                    {message.status === 'error' && <AlertCircle className="h-3 w-3 text-red-500" />}
                  </div>
                </div>
              </div>
            ))}
            
            {/* Loading indicator */}
            {sendMessageMutation.isPending && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-green-100 text-green-600 flex items-center justify-center">
                  <Bot className="h-4 w-4" />
                </div>
                <div className="bg-gray-100 rounded-lg p-3">
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm text-gray-600">AI is thinking...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        {/* Input Area */}
        <div className="border-t p-4">
          <div className="flex gap-2">
            <Input
              ref={inputRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              disabled={sendMessageMutation.isPending}
              className="flex-1"
            />
            <Button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || sendMessageMutation.isPending}
            >
              {sendMessageMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
          
          {/* Quick Suggestions */}
          <div className="mt-2 flex flex-wrap gap-2">
            {getQuickSuggestions(userRole).map((suggestion, idx) => (
              <Button
                key={idx}
                variant="outline"
                size="sm"
                onClick={() => setInputMessage(suggestion)}
                className="text-xs"
              >
                {suggestion}
              </Button>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Helper functions
function getWelcomeMessage(role: string): string {
  switch (role) {
    case 'patient':
      return "👋 Hi! I'm your AI healthcare assistant. I can help you schedule appointments, check lab results, refill prescriptions, and answer medical questions. How can I help you today?";
    case 'doctor':
      return "👋 Hello Doctor! I can help you review patient records, order tests, check schedules, and manage treatment plans. What would you like to do?";
    case 'staff':
      return "👋 Hi! I can help you with patient registration, appointment scheduling, billing, and administrative tasks. How can I assist you?";
    case 'admin':
      return "👋 Welcome Administrator! I can provide system analytics, manage workflows, review approvals, and generate reports. What do you need?";
    default:
      return "👋 Hello! How can I help you today?";
  }
}

function getRoleDescription(role: string): string {
  switch (role) {
    case 'patient':
      return "Ask me anything about appointments, prescriptions, lab results, or billing";
    case 'doctor':
      return "Access patient records, order tests, manage treatments";
    case 'staff':
      return "Register patients, schedule appointments, process payments";
    case 'admin':
      return "System monitoring, analytics, and workflow management";
    default:
      return "AI-powered healthcare assistant";
  }
}

function getQuickSuggestions(role: string): string[] {
  switch (role) {
    case 'patient':
      return [
        "Schedule an appointment",
        "Check my lab results",
        "Refill prescription",
        "View my bill"
      ];
    case 'doctor':
      return [
        "Show today's patients",
        "Order lab test",
        "View patient history",
        "Update treatment plan"
      ];
    case 'staff':
      return [
        "Register new patient",
        "Check appointments",
        "Process payment",
        "Send reminders"
      ];
    case 'admin':
      return [
        "System overview",
        "Pending approvals",
        "Revenue report",
        "Staff performance"
      ];
    default:
      return ["Help me get started"];
  }
}
