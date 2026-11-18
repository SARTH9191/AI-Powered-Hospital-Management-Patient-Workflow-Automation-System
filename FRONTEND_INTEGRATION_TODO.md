# 🎨 Frontend Integration TODO - Priority List

**For:** Frontend Developer  
**Before:** End-to-End Testing Tomorrow  
**Timeline:** Tonight/Early Morning

---

## 🔴 CRITICAL (Must Have for Testing)

### 1. **Stage Progress Indicator** ⭐⭐⭐⭐⭐

**Location:** `frontend/src/components/StageProgress.tsx` (new file)

**Purpose:** Show user which stage they're in (1-12)

**Component:**
```tsx
interface StageProgressProps {
  currentStage: number;
  completedStages: number[];
}

export default function StageProgress({ currentStage, completedStages }: StageProgressProps) {
  const stages = [
    { id: 1, name: "Registration", icon: "✨" },
    { id: 2, name: "Documents", icon: "📄" },
    { id: 3, name: "Medical History", icon: "🩺" },
    { id: 4, name: "Doctor Approval", icon: "👨‍⚕️" },
    { id: 5, name: "Lab Scheduling", icon: "🧪" },
    { id: 6, name: "Lab Results", icon: "📊" },
    { id: 7, name: "Consultation", icon: "🏥" },
    { id: 11, name: "Prescription", icon: "💊" },
    { id: 12, name: "Completion", icon: "🎉" }
  ];

  return (
    <div className="flex justify-between items-center p-4 bg-white rounded-lg shadow">
      {stages.map((stage) => (
        <div key={stage.id} className="flex flex-col items-center">
          <div className={`
            w-12 h-12 rounded-full flex items-center justify-center text-2xl
            ${completedStages.includes(stage.id) ? 'bg-green-500' : ''}
            ${currentStage === stage.id ? 'bg-blue-500 animate-pulse' : ''}
            ${currentStage < stage.id ? 'bg-gray-300' : ''}
          `}>
            {stage.icon}
          </div>
          <span className="text-xs mt-2">{stage.name}</span>
        </div>
      ))}
    </div>
  );
}
```

**Integration in chatbot page:**
```tsx
// In frontend/src/app/patient/chatbot/page.tsx
import StageProgress from '@/components/StageProgress';

// Add state
const [currentStage, setCurrentStage] = useState(2);
const [completedStages, setCompletedStages] = useState<number[]>([1]);

// Update on message response
useEffect(() => {
  if (response?.stage) {
    setCurrentStage(response.stage);
  }
  if (response?.stage_complete) {
    setCompletedStages(prev => [...prev, response.stage]);
  }
}, [response]);

// Add in JSX before chat messages
<StageProgress currentStage={currentStage} completedStages={completedStages} />
```

---

### 2. **Document Link Display** ⭐⭐⭐⭐⭐

**Location:** Update `frontend/src/app/patient/chatbot/page.tsx`

**Purpose:** Show document link prominently when created

**Add this component:**
```tsx
interface DocumentLinkProps {
  docUrl?: string;
  docId?: string;
}

function DocumentLink({ docUrl, docId }: DocumentLinkProps) {
  if (!docUrl) return null;
  
  return (
    <div className="p-4 mb-4 bg-blue-50 border-2 border-blue-200 rounded-lg">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <FileText className="h-6 w-6 text-blue-600" />
          <div>
            <p className="font-semibold text-blue-900">Your Medical Workflow Document</p>
            <p className="text-sm text-blue-600">ID: {docId}</p>
          </div>
        </div>
        <a 
          href={docUrl} 
          target="_blank" 
          rel="noopener noreferrer"
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Open Document
        </a>
      </div>
    </div>
  );
}

// In main component
const [workflowDocUrl, setWorkflowDocUrl] = useState<string>();
const [workflowDocId, setWorkflowDocId] = useState<string>();

// Update on message response
useEffect(() => {
  if (response?.workflow_doc_url) {
    setWorkflowDocUrl(response.workflow_doc_url);
    setWorkflowDocId(response.workflow_doc_id);
  }
}, [response]);

// Add in JSX after StageProgress
<DocumentLink docUrl={workflowDocUrl} docId={workflowDocId} />
```

---

### 3. **Calendar Event Display** ⭐⭐⭐⭐

**Location:** Add to `frontend/src/app/patient/chatbot/page.tsx`

**Purpose:** Show when calendar events are created

**Component:**
```tsx
interface CalendarEventProps {
  eventId?: string;
  eventType: 'lab' | 'followup';
  date?: string;
  time?: string;
}

function CalendarEventAlert({ eventId, eventType, date, time }: CalendarEventProps) {
  if (!eventId) return null;
  
  return (
    <div className="p-4 mb-4 bg-green-50 border-2 border-green-200 rounded-lg">
      <div className="flex items-center space-x-3">
        <Calendar className="h-6 w-6 text-green-600" />
        <div>
          <p className="font-semibold text-green-900">
            {eventType === 'lab' ? '🧪 Lab Appointment' : '📞 Follow-up'} Scheduled!
          </p>
          {date && <p className="text-sm text-green-600">📅 {date} at {time}</p>}
          <p className="text-xs text-green-500">Event ID: {eventId}</p>
        </div>
        <a 
          href="https://calendar.google.com" 
          target="_blank" 
          className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700"
        >
          View Calendar
        </a>
      </div>
    </div>
  );
}

// Track calendar events
const [labEventId, setLabEventId] = useState<string>();
const [followupEventId, setFollowupEventId] = useState<string>();

// Update from backend response (extract from AI message or separate field)
```

---

### 4. **Message Response Type Handling** ⭐⭐⭐⭐

**Location:** Update `frontend/src/app/patient/chatbot/page.tsx`

**Purpose:** Handle backend response structure correctly

**Update sendMessageMutation:**
```tsx
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
  onSuccess: (data) => {
    // Extract backend response
    const agentResponse = data.data || data;
    
    // Update stage
    if (agentResponse.stage) {
      setCurrentStage(agentResponse.stage);
    }
    
    // Update document URL
    if (agentResponse.workflow_doc_url) {
      setWorkflowDocUrl(agentResponse.workflow_doc_url);
      setWorkflowDocId(agentResponse.workflow_doc_id);
      toast.success('Medical document created!');
    }
    
    // Check for calendar event (parse from response or separate field)
    if (agentResponse.response.includes('Calendar Event ID:')) {
      const eventIdMatch = agentResponse.response.match(/Event ID: ([a-zA-Z0-9]+)/);
      if (eventIdMatch) {
        if (currentStage === 5) {
          setLabEventId(eventIdMatch[1]);
          toast.success('Lab appointment scheduled!');
        } else if (currentStage === 11) {
          setFollowupEventId(eventIdMatch[1]);
          toast.success('Follow-up scheduled!');
        }
      }
    }
    
    // Mark stage complete
    if (agentResponse.stage_complete) {
      setCompletedStages(prev => [...prev, agentResponse.stage]);
      toast.success(`Stage ${agentResponse.stage} complete!`);
    }
    
    // Refresh messages
    queryClient.invalidateQueries({ queryKey: ['chat-messages'] });
    setInputMessage('');
    setIsTyping(false);
  },
  onError: (error: any) => {
    toast.error(error.message || 'Failed to send message');
    setIsTyping(false);
  },
});
```

---

### 5. **Loading States** ⭐⭐⭐

**Purpose:** Show when AI is processing

**Update in chatbot page:**
```tsx
{isTyping && (
  <div className="flex items-start space-x-3 mb-4">
    <Avatar className="h-8 w-8">
      <Bot className="h-5 w-5" />
    </Avatar>
    <div className="bg-gray-100 rounded-lg p-3">
      <div className="flex space-x-2">
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
      </div>
    </div>
  </div>
)}
```

---

## 🟡 IMPORTANT (Should Have)

### 6. **Quick Skip Button for Stage 2** ⭐⭐⭐

**Purpose:** Easy skip for returning patients

```tsx
{currentStage === 2 && (
  <div className="mb-4 flex justify-center">
    <button
      onClick={() => sendMessageMutation.mutate('skip')}
      className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
    >
      Skip Document Upload →
    </button>
  </div>
)}
```

---

### 7. **Error Handling** ⭐⭐⭐

**Purpose:** Show user-friendly errors

```tsx
// Add error state
const [error, setError] = useState<string>();

// Show error banner
{error && (
  <div className="mb-4 p-4 bg-red-50 border-2 border-red-200 rounded-lg">
    <p className="text-red-800">{error}</p>
    <button 
      onClick={() => setError(undefined)}
      className="text-sm text-red-600 underline mt-2"
    >
      Dismiss
    </button>
  </div>
)}
```

---

### 8. **Message Formatting** ⭐⭐⭐

**Purpose:** Format AI messages nicely

```tsx
function formatMessage(content: string) {
  // Convert markdown-style formatting
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold
    .replace(/\*(.*?)\*/g, '<em>$1</em>') // Italic
    .replace(/\n/g, '<br/>') // Line breaks
    .replace(/• /g, '• '); // Keep bullets
}

// Use in message display
<div dangerouslySetInnerHTML={{ __html: formatMessage(message.content) }} />
```

---

### 9. **Refresh Notification** ⭐⭐

**Purpose:** Tell user to check document

```tsx
{currentStage === 4 && (
  <div className="mb-4 p-4 bg-yellow-50 border-2 border-yellow-200 rounded-lg">
    <p className="text-yellow-800 font-semibold">⏳ Waiting for Doctor Approval</p>
    <p className="text-sm text-yellow-600 mt-1">
      The doctor is reviewing your medical history. This usually takes a few minutes.
    </p>
    <button 
      onClick={() => sendMessageMutation.mutate('check')}
      className="mt-2 px-4 py-1 bg-yellow-600 text-white rounded hover:bg-yellow-700"
    >
      Check Status
    </button>
  </div>
)}
```

---

## 🟢 NICE TO HAVE (If Time Permits)

### 10. **Stage Instructions** ⭐⭐

Show what user needs to do at each stage

### 11. **Notification Toast Improvements** ⭐

Better toast messages with icons

### 12. **Mobile Responsive Check** ⭐

Test on mobile viewport

### 13. **Keyboard Shortcuts** ⭐

Enter to send, Escape to clear

---

## 📋 Testing Checklist for Frontend Developer

Before handing off for testing:

- [ ] Stage progress indicator shows current stage
- [ ] Completed stages highlighted in green
- [ ] Current stage animated/highlighted
- [ ] Document link appears when doc created
- [ ] Document link opens in new tab
- [ ] Calendar events show when created
- [ ] Loading indicator shows while AI processes
- [ ] Error messages display clearly
- [ ] Messages formatted nicely (bold, italics, line breaks)
- [ ] Quick skip button works for Stage 2
- [ ] Toast notifications appear for major events
- [ ] Auto-scroll works when new messages arrive
- [ ] Send button disabled while sending
- [ ] No console errors
- [ ] Works in Chrome/Firefox/Edge

---

## 🎯 Priority Order

**If short on time, implement in this order:**

1. **Stage Progress Indicator** (30 min) - Critical for UX
2. **Document Link Display** (20 min) - Must have
3. **Message Response Handling** (30 min) - Bug fixes
4. **Loading States** (10 min) - Better UX
5. **Calendar Event Display** (20 min) - Nice to have
6. **Skip Button** (10 min) - QoL improvement
7. **Error Handling** (15 min) - Safety net
8. Everything else if time permits

**Total estimated time:** ~2-3 hours for critical items

---

## 🚀 Quick Test After Implementation

```bash
# 1. Start backend
python main.py

# 2. Start frontend
cd frontend
npm run dev

# 3. Open browser
# http://localhost:3000

# 4. Quick test:
# - Login
# - Send a message
# - Check if stage indicator appears
# - Check if document link shows (Stage 3)
# - Check if calendar events display (Stage 5)
# - Check loading states
```

---

## 📞 If Stuck

**Backend response structure:**
```json
{
  "response": "AI message text",
  "stage": 3,
  "stage_complete": true,
  "next_stage": 4,
  "workflow_doc_url": "https://docs.google.com/...",
  "workflow_doc_id": "1kAgV4v..."
}
```

**Console log to debug:**
```tsx
console.log('Backend response:', data);
console.log('Stage:', data.stage);
console.log('Doc URL:', data.workflow_doc_url);
```

---

**Good luck! 🚀**

**Questions?** Check `FRONTEND_CAPABILITIES_AND_WORKFLOW.md` for detailed specs.
