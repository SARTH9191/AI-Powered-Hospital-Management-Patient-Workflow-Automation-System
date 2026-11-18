'use client';

import { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';
import {
  Bot,
  User,
  Send,
  Calendar,
  FileText,
  TestTube,
  Pill,
  DollarSign,
  Heart,
  Clock,
} from 'lucide-react';

interface Message {
  id: string;
  sender: 'user' | 'ai';
  content: string;
  timestamp: string;
  type?: 'text' | 'quick_action';
}

const quickActions = [
  { icon: Calendar, label: 'Book Appointment', prompt: 'I want to book an appointment' },
  { icon: FileText, label: 'View Health Records', prompt: 'Show me my health records' },
  { icon: TestTube, label: 'Lab Results', prompt: 'What are my latest lab results?' },
  { icon: Pill, label: 'Medication Info', prompt: 'Tell me about my medications' },
  { icon: DollarSign, label: 'Billing Questions', prompt: 'I have questions about my bill' },
  { icon: Heart, label: 'Health Tips', prompt: 'Give me health tips based on my records' },
];

const sampleResponses: { [key: string]: string } = {
  'book appointment': 'I can help you book an appointment! What type of specialist do you need to see? We have:\n\n• Cardiologist\n• General Physician\n• Dermatologist\n• Dentist\n• Orthopedic\n• Pediatrician\n\nPlease let me know your preference.',
  
  'health records': 'I found your recent health records:\n\n📋 **Recent Visits:**\n• Annual Physical - Sept 15, 2024 (Dr. Sarah Johnson)\n• Follow-up Consultation - Jun 5, 2024 (Dr. Sarah Johnson)\n\n🩺 **Diagnoses:**\n• Seasonal Allergies - Aug 10, 2024\n\n🏥 **Procedures:**\n• Dental Cleaning - Jul 20, 2024\n\nWould you like more details on any of these?',
  
  'lab results': 'Here are your latest lab results:\n\n🧪 **Complete Blood Count (Oct 12, 2024):**\n✅ All values normal\n\n🧪 **Lipid Panel (Oct 7, 2024):**\n⚠️ Total Cholesterol: 210 mg/dL (Slightly High)\n⚠️ LDL Cholesterol: 130 mg/dL (Slightly High)\n✅ HDL Cholesterol: Normal\n✅ Triglycerides: Normal\n\n**Recommendation:** Consider dietary changes and follow up with Dr. Chen.\n\nWould you like specific dietary recommendations?',
  
  'medications': 'You currently have 3 active medications:\n\n💊 **Lisinopril 10mg**\n• Once daily in the morning\n• For blood pressure control\n• 3 refills remaining\n\n💊 **Metformin 500mg**\n• Twice daily with meals\n• For blood sugar management\n• 2 refills remaining\n\n💊 **Atorvastatin 20mg**\n• Once daily in the evening\n• For cholesterol management\n• 5 refills remaining\n\n⚠️ **Note:** Vitamin D3 needs refill!\n\nWould you like to request a refill or learn more about any medication?',
  
  'billing': 'Let me check your billing information:\n\n💰 **Outstanding Balance:** $0.00\n✅ **Status:** All invoices paid!\n\n📄 **Recent Invoices:**\n• INV-2024-001: $450.00 (Paid) - Cardiology Consultation\n• INV-2024-002: $280.00 (Paid) - Blood Work\n• INV-2024-003: $320.00 (Paid) - Dental Cleaning\n\n**Total Paid This Year:** $1,050.00\n\nIs there anything specific about billing I can help with?',
  
  'health tips': 'Based on your health records, here are personalized health tips:\n\n🥗 **Nutrition:**\n• Reduce saturated fats to help with cholesterol\n• Increase fiber intake (oats, beans, fruits)\n• Limit sodium to support blood pressure control\n\n🏃 **Exercise:**\n• Aim for 30 minutes of moderate activity daily\n• Walking, swimming, or cycling are excellent choices\n• Consider strength training 2-3 times per week\n\n💊 **Medications:**\n• Take Lisinopril consistently in the morning\n• Don\'t forget Metformin with meals\n• Take Atorvastatin in the evening for best results\n\n😴 **Lifestyle:**\n• Maintain regular sleep schedule (7-8 hours)\n• Manage stress through relaxation techniques\n• Stay hydrated (8 glasses of water daily)\n\nWould you like more specific guidance on any of these areas?',
  
  'default': 'I\'m here to help! I can assist you with:\n\n• 📅 Booking appointments\n• 📋 Viewing your health records\n• 🧪 Checking lab results\n• 💊 Managing medications and refills\n• 💰 Billing and payment questions\n• ❤️ Personalized health recommendations\n\nWhat would you like help with today?',
};

export default function PatientAIAssistant() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: 'ai',
      content: 'Hello! 👋 I\'m your AI Health Assistant. I can help you with appointments, medications, lab results, and answer health questions. How can I assist you today?',
      timestamp: new Date().toISOString(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const getAIResponse = (userMessage: string): string => {
    const lowerMessage = userMessage.toLowerCase();
    
    if (lowerMessage.includes('appointment') || lowerMessage.includes('book')) {
      return sampleResponses['book appointment'];
    } else if (lowerMessage.includes('health record') || lowerMessage.includes('medical record')) {
      return sampleResponses['health records'];
    } else if (lowerMessage.includes('lab') || lowerMessage.includes('test result')) {
      return sampleResponses['lab results'];
    } else if (lowerMessage.includes('medication') || lowerMessage.includes('prescription') || lowerMessage.includes('refill')) {
      return sampleResponses['medications'];
    } else if (lowerMessage.includes('bill') || lowerMessage.includes('payment') || lowerMessage.includes('invoice')) {
      return sampleResponses['billing'];
    } else if (lowerMessage.includes('health tip') || lowerMessage.includes('advice') || lowerMessage.includes('recommendation')) {
      return sampleResponses['health tips'];
    } else if (lowerMessage.includes('hello') || lowerMessage.includes('hi')) {
      return 'Hello! How can I help you today? 😊';
    } else if (lowerMessage.includes('thank')) {
      return 'You\'re welcome! Is there anything else I can help you with?';
    } else {
      return sampleResponses['default'];
    }
  };

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      sender: 'user',
      content: inputValue,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate AI typing delay
    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        content: getAIResponse(inputValue),
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1500);
  };

  const handleQuickAction = (prompt: string) => {
    setInputValue(prompt);
    setTimeout(() => handleSendMessage(), 100);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar role="patient" />
        <main className="flex-1 ml-64 mt-16">
          <div className="p-8">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Health Assistant</h1>
              <p className="text-gray-600">Get instant help with your healthcare needs</p>
            </div>

            {/* Quick Actions */}
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="text-lg">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                  {quickActions.map((action, index) => (
                    <Button
                      key={index}
                      variant="outline"
                      className="h-auto py-4 flex flex-col items-center justify-center space-y-2"
                      onClick={() => handleQuickAction(action.prompt)}
                    >
                      <action.icon className="h-5 w-5" />
                      <span className="text-xs text-center">{action.label}</span>
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Chat Interface */}
            <Card className="h-[600px] flex flex-col">
              {/* Chat Header */}
              <CardHeader className="border-b">
                <div className="flex items-center space-x-3">
                  <Avatar className="h-10 w-10 bg-blue-600">
                    <AvatarFallback>
                      <Bot className="h-6 w-6 text-white" />
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <CardTitle className="text-lg">AI Assistant</CardTitle>
                    <div className="flex items-center space-x-2">
                      <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
                      <span className="text-xs text-gray-500">Online</span>
                    </div>
                  </div>
                </div>
              </CardHeader>

              {/* Messages Area */}
              <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`flex items-start space-x-2 max-w-[80%] ${
                        message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                      }`}
                    >
                      <Avatar className={`h-8 w-8 ${message.sender === 'ai' ? 'bg-blue-600' : 'bg-purple-600'}`}>
                        <AvatarFallback>
                          {message.sender === 'ai' ? (
                            <Bot className="h-5 w-5 text-white" />
                          ) : (
                            <User className="h-5 w-5 text-white" />
                          )}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <div
                          className={`rounded-lg p-3 ${
                            message.sender === 'user'
                              ? 'bg-purple-600 text-white'
                              : 'bg-gray-100 text-gray-900'
                          }`}
                        >
                          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                        </div>
                        <p className="text-xs text-gray-500 mt-1 px-1">
                          {formatTimestamp(message.timestamp)}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}

                {/* Typing Indicator */}
                {isTyping && (
                  <div className="flex justify-start">
                    <div className="flex items-start space-x-2">
                      <Avatar className="h-8 w-8 bg-blue-600">
                        <AvatarFallback>
                          <Bot className="h-5 w-5 text-white" />
                        </AvatarFallback>
                      </Avatar>
                      <div className="bg-gray-100 rounded-lg p-3">
                        <div className="flex space-x-1">
                          <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </CardContent>

              {/* Input Area */}
              <div className="border-t p-4">
                <div className="flex space-x-2">
                  <Input
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your message..."
                    className="flex-1"
                  />
                  <Button
                    onClick={handleSendMessage}
                    disabled={!inputValue.trim() || isTyping}
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Press Enter to send • Shift+Enter for new line
                </p>
              </div>
            </Card>

            {/* Info Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center space-x-3">
                    <div className="h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
                      <Clock className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">24/7 Availability</p>
                      <p className="text-xs text-gray-600">Get help anytime</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center space-x-3">
                    <div className="h-10 w-10 bg-green-100 rounded-full flex items-center justify-center">
                      <Heart className="h-5 w-5 text-green-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">Personalized Care</p>
                      <p className="text-xs text-gray-600">Based on your records</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center space-x-3">
                    <div className="h-10 w-10 bg-purple-100 rounded-full flex items-center justify-center">
                      <Bot className="h-5 w-5 text-purple-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">AI-Powered</p>
                      <p className="text-xs text-gray-600">Smart assistance</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
