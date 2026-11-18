'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/hooks/useAuth';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';
import {
  MessageSquare,
  Send,
  Search,
  Plus,
  User,
  Clock,
  Mail,
  MailOpen,
  Archive,
  Star,
} from 'lucide-react';
import axios from 'axios';

interface Message {
  message_id: string;
  sender_id: string;
  sender_name: string;
  sender_role: string;
  recipient_id: string;
  recipient_name: string;
  subject: string;
  body: string;
  timestamp: string;
  read: boolean;
  starred: boolean;
  thread_id?: string;
}

export default function DoctorMessages() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const doctorId = 'doctor001'; // TODO: Get from authenticated user

  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [selectedMessage, setSelectedMessage] = useState<Message | null>(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [composeDialogOpen, setComposeDialogOpen] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    recipient_id: '',
    recipient_name: '',
    subject: '',
    body: '',
  });

  // Fetch messages
  const { data: messagesData, isLoading } = useQuery({
    queryKey: ['doctor-messages', doctorId],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `http://localhost:8000/api/doctors/${doctorId}/messages`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data?.data?.messages || [];
    },
    enabled: !!doctorId,
  });

  // Send message mutation
  const sendMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        'http://localhost:8000/api/messages',
        {
          ...data,
          sender_id: doctorId,
          sender_name: user?.username || 'Doctor',
          sender_role: 'doctor',
          timestamp: new Date().toISOString(),
          read: false,
          starred: false,
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
      queryClient.invalidateQueries({ queryKey: ['doctor-messages'] });
      setComposeDialogOpen(false);
      resetForm();
    },
  });

  // Mark as read mutation
  const markAsReadMutation = useMutation({
    mutationFn: async (messageId: string) => {
      const token = localStorage.getItem('token');
      const response = await axios.put(
        `http://localhost:8000/api/messages/${messageId}/read`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['doctor-messages'] });
    },
  });

  // Toggle star mutation
  const toggleStarMutation = useMutation({
    mutationFn: async ({ messageId, starred }: { messageId: string; starred: boolean }) => {
      const token = localStorage.getItem('token');
      const response = await axios.put(
        `http://localhost:8000/api/messages/${messageId}/star`,
        { starred },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['doctor-messages'] });
    },
  });

  const messages: Message[] = messagesData || [];

  // Filter messages
  const filteredMessages = messages.filter((msg) => {
    if (filterType === 'unread' && msg.read) return false;
    if (filterType === 'starred' && !msg.starred) return false;
    if (filterType === 'sent' && msg.sender_id !== doctorId) return false;
    if (filterType === 'received' && msg.recipient_id !== doctorId) return false;
    if (
      searchQuery &&
      !msg.subject.toLowerCase().includes(searchQuery.toLowerCase()) &&
      !msg.sender_name.toLowerCase().includes(searchQuery.toLowerCase()) &&
      !msg.body.toLowerCase().includes(searchQuery.toLowerCase())
    ) {
      return false;
    }
    return true;
  });

  const resetForm = () => {
    setFormData({
      recipient_id: '',
      recipient_name: '',
      subject: '',
      body: '',
    });
  };

  const handleViewMessage = (message: Message) => {
    setSelectedMessage(message);
    setViewDialogOpen(true);
    if (!message.read && message.recipient_id === doctorId) {
      markAsReadMutation.mutate(message.message_id);
    }
  };

  const handleSend = () => {
    sendMutation.mutate(formData);
  };

  const handleToggleStar = (message: Message, e: React.MouseEvent) => {
    e.stopPropagation();
    toggleStarMutation.mutate({
      messageId: message.message_id,
      starred: !message.starred,
    });
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const unreadCount = messages.filter((m) => !m.read && m.recipient_id === doctorId).length;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar role="doctor" />
        <main className="flex-1 ml-64 mt-16">
          <div className="p-8">
            {/* Header */}
            <div className="mb-8 flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">Messages</h1>
                <p className="text-gray-600">Internal messaging with staff and patients</p>
              </div>
              <Button onClick={() => setComposeDialogOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                New Message
              </Button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Total Messages
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-gray-900">{messages.length}</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Unread
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-blue-600">{unreadCount}</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Starred
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-yellow-600">
                    {messages.filter((m) => m.starred).length}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Sent
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-gray-900">
                    {messages.filter((m) => m.sender_id === doctorId).length}
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Filters */}
            <Card className="mb-6">
              <CardContent className="pt-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* Search */}
                  <div className="relative md:col-span-2">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Search messages..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>

                  {/* Filter */}
                  <Select value={filterType} onValueChange={setFilterType}>
                    <SelectTrigger>
                      <SelectValue placeholder="Filter" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Messages</SelectItem>
                      <SelectItem value="unread">Unread</SelectItem>
                      <SelectItem value="starred">Starred</SelectItem>
                      <SelectItem value="received">Received</SelectItem>
                      <SelectItem value="sent">Sent</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Messages List */}
            {isLoading ? (
              <div className="space-y-3">
                {[1, 2, 3, 4, 5].map((i) => (
                  <Card key={i}>
                    <CardContent className="pt-6">
                      <Skeleton className="h-16 w-full" />
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : filteredMessages.length === 0 ? (
              <Card>
                <CardContent className="pt-12 pb-12 text-center">
                  <MessageSquare className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 text-lg mb-2">No messages found</p>
                  <p className="text-gray-500 text-sm mb-4">
                    Start a conversation by composing a new message
                  </p>
                  <Button onClick={() => setComposeDialogOpen(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    New Message
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-2">
                {filteredMessages.map((message) => {
                  const isReceived = message.recipient_id === doctorId;
                  const displayName = isReceived ? message.sender_name : message.recipient_name;
                  const displayRole = isReceived ? message.sender_role : 'recipient';

                  return (
                    <Card
                      key={message.message_id}
                      className={`hover:shadow-md transition-shadow cursor-pointer ${
                        !message.read && isReceived ? 'bg-blue-50 border-blue-200' : ''
                      }`}
                      onClick={() => handleViewMessage(message)}
                    >
                      <CardContent className="pt-4 pb-4">
                        <div className="flex items-center space-x-4">
                          {/* Avatar */}
                          <Avatar className="h-10 w-10">
                            <AvatarFallback className="bg-blue-100 text-blue-600 font-semibold">
                              {displayName.split(' ').map(n => n[0]).join('').slice(0, 2)}
                            </AvatarFallback>
                          </Avatar>

                          {/* Message Info */}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center space-x-2 mb-1">
                              <span className={`font-semibold text-gray-900 ${
                                !message.read && isReceived ? 'font-bold' : ''
                              }`}>
                                {displayName}
                              </span>
                              <Badge variant="outline" className="text-xs">
                                {displayRole}
                              </Badge>
                              {!isReceived && (
                                <Badge variant="secondary" className="text-xs">
                                  Sent
                                </Badge>
                              )}
                            </div>
                            <p className={`text-sm mb-1 ${
                              !message.read && isReceived ? 'font-semibold text-gray-900' : 'text-gray-900'
                            }`}>
                              {message.subject}
                            </p>
                            <p className="text-sm text-gray-600 truncate">
                              {message.body.substring(0, 100)}...
                            </p>
                          </div>

                          {/* Actions */}
                          <div className="flex items-center space-x-3">
                            <button
                              onClick={(e) => handleToggleStar(message, e)}
                              className="text-gray-400 hover:text-yellow-500 transition-colors"
                            >
                              <Star
                                className={`h-5 w-5 ${
                                  message.starred ? 'fill-yellow-500 text-yellow-500' : ''
                                }`}
                              />
                            </button>
                            <div className="flex items-center space-x-1 text-sm text-gray-600">
                              <Clock className="h-4 w-4" />
                              <span>{formatTimestamp(message.timestamp)}</span>
                            </div>
                            {!message.read && isReceived ? (
                              <Mail className="h-5 w-5 text-blue-600" />
                            ) : (
                              <MailOpen className="h-5 w-5 text-gray-400" />
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            )}
          </div>
        </main>
      </div>

      {/* View Message Dialog */}
      <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Message</DialogTitle>
          </DialogHeader>

          {selectedMessage && (
            <div className="space-y-6">
              {/* Header */}
              <div className="pb-4 border-b">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <Avatar className="h-12 w-12">
                      <AvatarFallback className="bg-blue-100 text-blue-600 font-semibold">
                        {selectedMessage.sender_name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <p className="font-semibold text-gray-900">{selectedMessage.sender_name}</p>
                      <p className="text-sm text-gray-600 capitalize">{selectedMessage.sender_role}</p>
                    </div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleStarMutation.mutate({
                        messageId: selectedMessage.message_id,
                        starred: !selectedMessage.starred,
                      });
                    }}
                    className="text-gray-400 hover:text-yellow-500 transition-colors"
                  >
                    <Star
                      className={`h-6 w-6 ${
                        selectedMessage.starred ? 'fill-yellow-500 text-yellow-500' : ''
                      }`}
                    />
                  </button>
                </div>
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <span>To:</span>
                  <span className="font-medium text-gray-900">{selectedMessage.recipient_name}</span>
                  <span>•</span>
                  <Clock className="h-3 w-3" />
                  <span>{new Date(selectedMessage.timestamp).toLocaleString()}</span>
                </div>
              </div>

              {/* Subject */}
              <div>
                <Label className="text-gray-600">Subject</Label>
                <p className="text-lg font-semibold text-gray-900 mt-1">
                  {selectedMessage.subject}
                </p>
              </div>

              {/* Body */}
              <div>
                <Label className="text-gray-600">Message</Label>
                <div className="mt-2 p-4 bg-gray-50 rounded-lg">
                  <p className="text-gray-900 whitespace-pre-wrap">{selectedMessage.body}</p>
                </div>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setViewDialogOpen(false)}>
              Close
            </Button>
            <Button
              onClick={() => {
                setFormData({
                  recipient_id: selectedMessage?.sender_id || '',
                  recipient_name: selectedMessage?.sender_name || '',
                  subject: `Re: ${selectedMessage?.subject}`,
                  body: '',
                });
                setViewDialogOpen(false);
                setComposeDialogOpen(true);
              }}
            >
              <Send className="h-4 w-4 mr-2" />
              Reply
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Compose Message Dialog */}
      <Dialog open={composeDialogOpen} onOpenChange={setComposeDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>New Message</DialogTitle>
            <DialogDescription>Send a message to staff or patients</DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="recipient_id">Recipient ID *</Label>
                <Input
                  id="recipient_id"
                  value={formData.recipient_id}
                  onChange={(e) => setFormData({ ...formData, recipient_id: e.target.value })}
                  placeholder="Enter recipient ID"
                />
              </div>
              <div>
                <Label htmlFor="recipient_name">Recipient Name *</Label>
                <Input
                  id="recipient_name"
                  value={formData.recipient_name}
                  onChange={(e) => setFormData({ ...formData, recipient_name: e.target.value })}
                  placeholder="Enter recipient name"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="subject">Subject *</Label>
              <Input
                id="subject"
                value={formData.subject}
                onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                placeholder="Enter message subject"
              />
            </div>

            <div>
              <Label htmlFor="body">Message *</Label>
              <Textarea
                id="body"
                value={formData.body}
                onChange={(e) => setFormData({ ...formData, body: e.target.value })}
                placeholder="Type your message here..."
                rows={10}
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setComposeDialogOpen(false);
                resetForm();
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSend}
              disabled={sendMutation.isPending || !formData.recipient_id || !formData.subject || !formData.body}
            >
              <Send className="h-4 w-4 mr-2" />
              Send Message
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
