# OMK Queen - Frontend Connection Guide

## 🏗️ **Architecture Overview**

The chat interface (`omk-frontend`) is **directly connected** to Queen AI's Hive backend. This is not a standalone chat - it's Queen's frontend interface where she lives and operates.

```
┌─────────────────────────────────────────┐
│         OMK Queen (Frontend)            │
│      /omk-frontend/app/chat             │
│                                         │
│  - User Interface                       │
│  - Conversational UI Components         │
│  - Real-time Chat Display               │
└──────────────┬──────────────────────────┘
               │
               │ HTTP Requests
               │ (localhost:8001)
               ▼
┌─────────────────────────────────────────┐
│    Queen AI Hive (Backend)              │
│    /backend/queen-ai                    │
│                                         │
│  ✅ Gemini AI (Primary LLM)             │
│  ✅ OpenAI (Fallback)                   │
│  ✅ Anthropic Claude (Optional)         │
│  ✅ 16 PRIME2 Smart Contracts           │
│  ✅ Bee Orchestration System            │
│  ✅ Data Pipeline & Analytics           │
└─────────────────────────────────────────┘
```

---

## 🔗 **Connection Details**

### **Frontend → Backend**

| Component | Endpoint | Purpose |
|-----------|----------|---------|
| Chat Interface | `POST /api/v1/frontend/chat` | Send user messages to Queen AI |
| Menu Interactions | `POST /api/v1/frontend/menu-interaction` | Handle menu clicks conversationally |
| Greetings | `GET /api/v1/frontend/greetings` | Get multilingual welcome messages |
| Onboarding | `POST /api/v1/frontend/register` | User registration via Queen |
| Feature Explanations | `POST /api/v1/frontend/explain/{feature}` | AI-powered feature explanations |

**Base URL:** `http://localhost:8001/api/v1/frontend`

**API Implementation:** `/omk-frontend/lib/api.ts`

---

## 🤖 **Queen's AI Stack**

### **Gemini Integration**

Queen uses Google's Gemini AI as her primary LLM provider. The configuration is in:

```
/backend/queen-ai/.env
```

**Key Variables:**
```bash
# Google Gemini API
GOOGLE_API_KEY=your_gemini_key_here
LLM_PRIMARY_PROVIDER=google

# Fallback providers
OPENAI_API_KEY=your_openai_key_optional
ANTHROPIC_API_KEY=your_anthropic_key_optional
```

### **How Queen Processes Messages:**

1. **User sends message** → Frontend (`/app/chat/page.tsx`)
2. **API call** → `frontendAPI.chat(userInput)`
3. **Backend receives** → `/backend/queen-ai/app/api/v1/frontend.py`
4. **Bee Manager** → Routes to `UserExperienceBee`
5. **LLM Provider** → Calls Gemini API via `/app/llm/providers/google.py`
6. **Queen responds** → Contextual, conversational response
7. **Frontend displays** → Message appears in chat

---

## ✅ **Verifying Connection**

### **Step 1: Check Queen Backend is Running**

```bash
cd /Users/mac/CascadeProjects/omakh-Hive/backend/queen-ai
python main.py
```

Should see:
```
🚀 Starting Queen AI Orchestrator
✅ Queen AI ready and operational
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8001
```

### **Step 2: Check Frontend Environment**

Create `/omk-frontend/.env.local`:
```bash
NEXT_PUBLIC_QUEEN_API_URL=http://localhost:8001
NEXT_PUBLIC_DEBUG=true
```

### **Step 3: Test Connection**

```bash
# From frontend directory
cd /Users/mac/CascadeProjects/omakh-Hive/omk-frontend

# Check if Queen is accessible
curl http://localhost:8001/health

# Should return:
{
  "service": "Queen AI Orchestrator",
  "version": "1.0.0",
  "status": "operational",
  ...
}
```

### **Step 4: Test Chat Endpoint**

```bash
curl -X POST http://localhost:8001/api/v1/frontend/chat \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Hello Queen!", "context": {}}'

# Should get an AI response from Gemini
```

---

## 🐝 **Queen's Bee System**

When you interact with the chat, Queen delegates tasks to specialized "Bees":

### **UserExperienceBee**
- Handles conversational responses
- Manages onboarding flow
- Provides feature explanations
- Uses Gemini for natural language generation

### **OnboardingBee**
- User registration & login
- Email verification
- Session management
- Wallet creation

### **DataPipelineBee**
- Real-time market data
- Price feeds (OMK/USDT)
- Property analytics

### **BlockchainBee**
- Smart contract interactions
- Transaction monitoring
- Token operations

---

## 🚨 **Troubleshooting**

### **"Queen not responding"**

1. **Check backend is running:**
   ```bash
   cd backend/queen-ai
   python main.py
   ```

2. **Check Gemini API key:**
   ```bash
   cd backend/queen-ai
   grep GOOGLE_API_KEY .env
   ```

3. **Check frontend is hitting correct URL:**
   ```typescript
   // In browser console
   console.log(process.env.NEXT_PUBLIC_QUEEN_API_URL);
   // Should be: http://localhost:8001
   ```

### **"Gemini API errors"**

Check backend logs for:
```
❌ Google LLM Provider error: ...
```

Solutions:
- Verify API key is valid
- Check API quota/billing
- Ensure `.env` file exists and is loaded

### **"CORS errors"**

Backend should have CORS configured for frontend:

```python
# backend/queen-ai/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🎯 **Current Implementation Status**

✅ **Connected:**
- Frontend API client (`/lib/api.ts`)
- Backend endpoints (`/backend/queen-ai/app/api/v1/frontend.py`)
- Chat endpoint integration
- Menu interaction handling

⏳ **Needs Verification:**
- Gemini responses appearing in frontend
- Real-time bee orchestration feedback
- Error handling and fallbacks

---

## 📝 **Next Steps**

1. **Start Queen Backend:**
   ```bash
   cd backend/queen-ai
   python main.py
   ```

2. **Start Frontend:**
   ```bash
   cd omk-frontend
   npm run dev
   ```

3. **Test Chat:**
   - Open `http://localhost:3001`
   - Send a message
   - Watch backend logs for Gemini API calls

4. **Monitor Connection:**
   - Check browser Network tab
   - Look for `POST /api/v1/frontend/chat`
   - Verify 200 responses

---

## 🌟 **Queen is Ready!**

The frontend is **already configured** to use Queen's backend. The Gemini API key in the backend `.env` file is the key that powers ALL conversations.

**This is not a mock interface - it's Queen's real operational frontend!** 👑✨
