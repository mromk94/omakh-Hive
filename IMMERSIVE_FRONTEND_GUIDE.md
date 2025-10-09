# 🎨 Immersive AI Frontend - Implementation Guide

**Revolutionary Web3 UX - Conversational, Multilingual, User-Friendly**

---

## 🎯 Vision

An **AI-first, chat-based interface** that feels like talking to a friend, not filling out forms. Users who've never touched Web3 should feel completely comfortable.

---

## 📊 Backend Ready ✅

**2 New Bees Created:**
- **OnboardingBee** (bee_id=18): User management & authentication
- **UserExperienceBee** (bee_id=19): Conversational AI interactions

**API Base URL:** `http://localhost:8001/api/v1/frontend`

**All 19+ endpoints ready to use!**

---

## 🏗️ Tech Stack

### Required
- **Framework:** Next.js 14+ (App Router)
- **Styling:** TailwindCSS
- **Animations:** Framer Motion
- **3D Elements:** Three.js + React Three Fiber
- **State:** Zustand
- **HTTP:** Axios
- **i18n:** next-intl or react-i18next

### Nice to Have
- **Lottie:** For micro-animations
- **React Hook Form:** Form handling
- **Sound:** Howler.js (optional sound effects)

---

## 📁 Project Structure

```
frontend/
├── app/
│   ├── page.tsx                    # Greeting screen
│   ├── chat/page.tsx               # Main chat interface
│   ├── dashboard/page.tsx          # User dashboard
│   └── layout.tsx                  # Root layout
├── components/
│   ├── greeting/
│   │   ├── AnimatedGreeting.tsx    # Multilingual greetings
│   │   ├── LanguageSelector.tsx    # Language picker
│   │   └── FloatingButton.tsx      # Animated buttons
│   ├── chat/
│   │   ├── ChatInterface.tsx       # Main chat
│   │   ├── MessageBubble.tsx       # Chat messages
│   │   ├── ThemeSelector.tsx       # Theme picker
│   │   ├── OptionsMenu.tsx         # Choice buttons
│   │   └── InfoSnippet.tsx         # Info cards
│   ├── dashboard/
│   │   ├── WalletBubble.tsx        # Balance display
│   │   ├── ROIIndicator.tsx        # ROI glow effect
│   │   └── QuickActions.tsx        # Action buttons
│   └── shared/
│       ├── FloatingSidebar.tsx     # Menu drawer
│       ├── ThemeProvider.tsx       # Theme context
│       └── AnimatedBackground.tsx  # Parallax bg
├── lib/
│   ├── api.ts                      # API client
│   ├── store.ts                    # Zustand store
│   └── animations.ts               # Framer Motion configs
├── hooks/
│   ├── useChat.ts                  # Chat logic
│   ├── useAuth.ts                  # Authentication
│   └── useTheme.ts                 # Theme switching
└── public/
    ├── locales/                    # i18n translations
    └── sounds/                     # Sound effects
```

---

## 🚀 Implementation Steps

### Step 1: Setup Next.js Project

```bash
npx create-next-app@latest omk-hive-frontend --typescript --tailwind --app
cd omk-hive-frontend

# Install dependencies
npm install framer-motion @react-three/fiber @react-three/drei three
npm install zustand axios
npm install next-intl
npm install lucide-react  # For icons
```

### Step 2: Configure API Client

**`lib/api.ts`:**
```typescript
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1/frontend';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('session_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API methods
export const frontendAPI = {
  // Greetings
  getGreetings: () => api.get('/greetings'),
  getWelcome: (language: string) => api.post('/welcome', { language }),
  
  // Theme
  getThemeSelection: (language: string) => api.post('/theme-selection', { language }),
  
  // Auth
  checkEmail: (email: string) => api.post('/check-email', { email }),
  register: (data: any) => api.post('/register', data),
  login: (email: string, password: string) => api.post('/login', { email, password }),
  verifySession: (token: string) => api.post('/verify-session', { session_token: token }),
  
  // Chat
  chat: (userInput: string, context?: any) => api.post('/chat', { user_input: userInput, context }),
  menuClick: (menuItem: string) => api.post('/menu-interaction', { menu_item: menuItem }),
  
  // Info
  getInfoSnippet: (snippetId: string, showMore: boolean = false) => 
    api.get(`/info-snippet/${snippetId}?show_more=${showMore}`),
};
```

### Step 3: Create Greeting Screen

**`app/page.tsx`:**
```typescript
'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { frontendAPI } from '@/lib/api';

export default function GreetingScreen() {
  const router = useRouter();
  const [greetings, setGreetings] = useState<any[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showLanguageSelector, setShowLanguageSelector] = useState(false);

  useEffect(() => {
    // Fetch greetings
    frontendAPI.getGreetings().then(res => {
      const greetingArray = Object.values(res.data.greetings);
      setGreetings(greetingArray);
    });
  }, []);

  // Rotate greetings every 3 seconds
  useEffect(() => {
    if (greetings.length === 0) return;
    
    const timer = setInterval(() => {
      setCurrentIndex(prev => (prev + 1) % greetings.length);
    }, 3000);
    
    return () => clearInterval(timer);
  }, [greetings]);

  // Show language selector after 5 seconds
  useEffect(() => {
    const timer = setTimeout(() => setShowLanguageSelector(true), 5000);
    return () => clearTimeout(timer);
  }, []);

  const handleLanguageSelect = (lang: string) => {
    localStorage.setItem('language', lang);
    router.push('/chat');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex flex-col items-center justify-center">
      {/* Animated Greeting */}
      <AnimatePresence mode="wait">
        {greetings[currentIndex] && (
          <motion.div
            key={currentIndex}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{ duration: 0.5 }}
            className="text-center"
          >
            <h1 className="text-8xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              {greetings[currentIndex].text}
            </h1>
            <p className="text-2xl text-gray-600 mt-4">
              {greetings[currentIndex].flag} {greetings[currentIndex].name}
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Language Selector */}
      {showLanguageSelector && (
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-16"
        >
          <button
            onClick={() => setShowLanguageSelector(true)}
            className="px-8 py-4 bg-white rounded-full shadow-2xl hover:shadow-3xl transition-all hover:scale-105 flex items-center gap-3"
          >
            <span className="text-3xl">🌍</span>
            <span className="text-lg font-semibold">Choose Your Language</span>
          </button>
          
          {/* Language Grid (show on click) */}
          <div className="grid grid-cols-4 gap-4 mt-8">
            {greetings.map((greeting, idx) => (
              <motion.button
                key={idx}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => handleLanguageSelect(Object.keys(greetings)[idx])}
                className="p-4 bg-white rounded-xl shadow-lg hover:shadow-xl transition-all"
              >
                <div className="text-4xl mb-2">{greeting.flag}</div>
                <div className="text-sm font-medium">{greeting.name}</div>
              </motion.button>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}
```

### Step 4: Create Chat Interface

**`app/chat/page.tsx`:**
```typescript
'use client';

import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { frontendAPI } from '@/lib/api';
import MessageBubble from '@/components/chat/MessageBubble';
import ThemeSelector from '@/components/chat/ThemeSelector';
import OptionsMenu from '@/components/chat/OptionsMenu';

export default function ChatInterface() {
  const [messages, setMessages] = useState<any[]>([]);
  const [stage, setStage] = useState('welcome'); // welcome, theme, account, info
  const [theme, setTheme] = useState('light');
  const [language, setLanguage] = useState('en');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Get language from localStorage
    const lang = localStorage.getItem('language') || 'en';
    setLanguage(lang);
    
    // Get initial welcome message
    frontendAPI.getWelcome(lang).then(res => {
      addMessage('ai', res.data.message);
      setStage('theme');
    });
  }, []);

  const addMessage = (sender: 'user' | 'ai', content: string, options?: any) => {
    setMessages(prev => [...prev, { sender, content, options, timestamp: new Date() }]);
    scrollToBottom();
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleThemeSelect = async (selectedTheme: string) => {
    setTheme(selectedTheme);
    addMessage('user', `I choose ${selectedTheme} theme`);
    
    // Get next prompt
    const res = await frontendAPI.getThemeSelection(language);
    addMessage('ai', res.data.message);
    setStage('account');
  };

  const handleUserInput = async (input: string) => {
    addMessage('user', input);
    
    // Send to AI
    const res = await frontendAPI.chat(input);
    addMessage('ai', res.data.message, res.data.options);
  };

  return (
    <div className={`min-h-screen transition-colors duration-500 ${
      theme === 'dark' ? 'bg-gray-900' : 'bg-gradient-to-br from-blue-50 via-white to-purple-50'
    }`}>
      {/* Chat Container */}
      <div className="max-w-4xl mx-auto pt-20 pb-32 px-4">
        {/* Messages */}
        <div className="space-y-6">
          {messages.map((msg, idx) => (
            <MessageBubble key={idx} message={msg} theme={theme} />
          ))}
          
          {/* Theme Selector (shows at appropriate time) */}
          {stage === 'theme' && (
            <ThemeSelector onSelect={handleThemeSelect} />
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Box (fixed at bottom) */}
      <div className="fixed bottom-0 left-0 right-0 bg-white/80 backdrop-blur-lg border-t p-4">
        <div className="max-w-4xl mx-auto flex gap-2">
          <input
            type="text"
            placeholder="Type your message..."
            className="flex-1 px-6 py-4 rounded-full border-2 focus:border-blue-500 outline-none"
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleUserInput((e.target as HTMLInputElement).value);
                (e.target as HTMLInputElement).value = '';
              }
            }}
          />
          <button className="px-6 py-4 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors">
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
```

### Step 5: Create Message Bubble Component

**`components/chat/MessageBubble.tsx`:**
```typescript
import { motion } from 'framer-motion';

export default function MessageBubble({ message, theme }: any) {
  const isAI = message.sender === 'ai';
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex ${isAI ? 'justify-start' : 'justify-end'}`}
    >
      <div className={`max-w-[70%] ${
        isAI 
          ? 'bg-white shadow-lg rounded-3xl rounded-tl-none' 
          : 'bg-blue-600 text-white rounded-3xl rounded-tr-none'
      } px-6 py-4`}>
        {/* AI Icon */}
        {isAI && (
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">🤖</span>
            <span className="text-sm font-semibold text-gray-600">Queen AI</span>
          </div>
        )}
        
        {/* Message Content */}
        <div className="text-base leading-relaxed whitespace-pre-wrap">
          {message.content}
        </div>
        
        {/* Options (if any) */}
        {message.options && (
          <div className="mt-4 space-y-2">
            {message.options.map((opt: any, idx: number) => (
              <button
                key={idx}
                className="w-full text-left px-4 py-3 bg-blue-50 hover:bg-blue-100 rounded-xl transition-colors"
              >
                {opt.label}
              </button>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}
```

---

## 🎨 Design Guidelines

### Colors

**Light Theme:**
- Primary: `#3B82F6` (blue-600)
- Secondary: `#8B5CF6` (purple-600)
- Background: Gradient `from-blue-50 via-white to-purple-50`
- Text: `#1F2937` (gray-800)

**Dark Theme:**
- Primary: `#60A5FA` (blue-400)
- Secondary: `#A78BFA` (purple-400)
- Background: `#111827` (gray-900)
- Text: `#F9FAFB` (gray-50)

### Typography
- **Font:** Inter or DM Sans
- **Headings:** Bold, large (text-6xl to text-8xl for greetings)
- **Body:** Regular, comfortable (text-base to text-lg)

### Animations
- **Duration:** 300-500ms (smooth but not slow)
- **Easing:** `ease-out` for entrances, `ease-in-out` for interactions
- **Scale:** 0.95-1.1 for buttons
- **Opacity:** 0-1 for fades

---

## 🔌 API Endpoint Usage

### Example: User Registration Flow

```typescript
// 1. Check if email exists
const checkResult = await frontendAPI.checkEmail('user@example.com');

if (checkResult.data.exists) {
  // Show login
} else {
  // 2. Register new user
  const registerResult = await frontendAPI.register({
    email: 'user@example.com',
    password: 'secure_password',
    full_name: 'John Doe',
    user_type: 'investor',
    language: 'en',
    theme: 'light'
  });
  
  // 3. Save session token
  localStorage.setItem('session_token', registerResult.data.session_token);
  
  // 4. Redirect to dashboard
  router.push('/dashboard');
}
```

---

## 🧪 Testing the Backend

Start Queen AI:
```bash
cd backend/queen-ai
python3 main.py
```

Test endpoints:
```bash
# Get greetings
curl http://localhost:8001/api/v1/frontend/greetings

# Check email
curl -X POST http://localhost:8001/api/v1/frontend/check-email \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# Chat with AI
curl -X POST http://localhost:8001/api/v1/frontend/chat \
  -H "Content-Type: application/json" \
  -d '{"user_input": "What is OMK?"}'
```

API Docs: http://localhost:8001/docs

---

## ✨ Key Features to Implement

### Phase 1 (Core)
- ✅ Animated greeting screen
- ✅ Language selection
- ✅ Theme selection
- ✅ Chat interface
- ✅ User registration/login
- ✅ Session management

### Phase 2 (Enhanced)
- 🔄 Wallet connection (MetaMask)
- 🔄 Dashboard with balance
- 🔄 ROI indicator
- 🔄 Transaction history
- 🔄 Staking interface

### Phase 3 (Polish)
- 🔄 Sound effects
- 🔄 3D floating elements
- 🔄 Parallax background
- 🔄 Micro-animations
- 🔄 Mobile responsive

---

## 📱 Mobile Responsive

Use Tailwind breakpoints:
```typescript
<div className="
  text-4xl md:text-6xl lg:text-8xl
  px-4 md:px-8 lg:px-16
  py-8 md:py-12 lg:py-20
">
```

---

## 🎯 Summary

**Backend:** ✅ Complete (19 bees, 19+ API endpoints)
**Frontend:** 🔄 Ready to build

**Start with:**
1. Create Next.js project
2. Implement greeting screen
3. Build chat interface
4. Connect to API endpoints
5. Add animations
6. Polish UX

**The backend is waiting! Let's build the most user-friendly Web3 interface ever! 🚀✨**
