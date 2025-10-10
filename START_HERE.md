# 👑 START OMAKH HIVE - QUICK GUIDE

## ✅ **FIXED: Syntax Error in Backend**

The backend had a syntax error that I just fixed in:
`/backend/queen-ai/app/blockchain/ethereum_client.py` (line 65-67)

---

## 🚀 **START EVERYTHING - ONE COMMAND**

```bash
./start-omakh.sh
```

**This script will:**
1. ✅ Check configuration
2. ✅ Create virtual environment if needed  
3. ✅ Install dependencies
4. ✅ Start Queen AI Backend (port 8001)
5. ✅ Start Next.js Frontend (port 3001)
6. ✅ Open browser automatically

---

## 📋 **OTHER COMMANDS**

```bash
# Stop everything gracefully
./stop-omakh.sh

# Reboot (stop + clear cache + restart)
./reboot-omakh.sh
```

---

## 🔍 **CHECK IF IT'S WORKING**

### **Backend Status:**
```bash
curl http://localhost:8001/health
```

Should return JSON with `"status": "operational"`

### **Frontend Status:**
```bash
curl http://localhost:3001
```

Should return HTML (Next.js page)

### **Connection Status in Browser:**
Open http://localhost:3001
- Look for **green pulsing dot** next to OMK Queen logo
- Should see **"LIVE" badge** when connected

---

## 🐛 **IF SOMETHING WENT WRONG**

### **Check Logs:**
```bash
# Backend logs
tail -f logs/queen-backend.log

# Frontend logs  
tail -f logs/frontend.log
```

### **Common Issues:**

**1. "Module not found" errors:**
```bash
cd backend/queen-ai
source venv/bin/activate
pip install -r requirements.txt
```

**2. "Port already in use":**
```bash
# Kill process on port 8001
lsof -ti:8001 | xargs kill -9

# Kill process on port 3001
lsof -ti:3001 | xargs kill -9
```

**3. "No module named app.core":**
Make sure you're running from the correct directory:
```bash
cd backend/queen-ai
python main.py
```

---

## 🎯 **MANUAL START (If script doesn't work)**

### **Terminal 1 - Backend:**
```bash
cd backend/queen-ai
source venv/bin/activate  # or: python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Should see:
```
🚀 Starting Queen AI Orchestrator
✅ Queen AI ready and operational
INFO: Uvicorn running on http://0.0.0.0:8001
```

### **Terminal 2 - Frontend:**
```bash
cd omk-frontend
npm install  # if first time
npm run dev
```

Should see:
```
▲ Next.js 14.1.0
- Local:        http://localhost:3001
✓ Ready in 2.3s
```

---

## ⚙️ **CONFIGURATION**

### **Backend (.env file):**
Location: `backend/queen-ai/.env`

**Minimum required:**
```bash
# Gemini AI (required for chat)
GOOGLE_API_KEY=your_gemini_api_key_here

# Database
DATABASE_URL=sqlite:///./queen.db

# Environment
ENVIRONMENT=development
```

### **Frontend (.env.local):**
Location: `omk-frontend/.env.local`

```bash
NEXT_PUBLIC_QUEEN_API_URL=http://localhost:8001
```

---

## ✅ **WHEN IT'S WORKING**

You'll see in browser (http://localhost:3001):

1. 👑 **Black background** with gold theme
2. 👑 **Wiggling gold crown** in header
3. 🟢 **Green pulsing dot** (connection status)
4. 💬 **"LIVE" badge** next to OMK Queen
5. 🟡 **Gold menu button** (top-right)
6. 💛 **Gold message bubbles** when you type

**Type a message and Queen AI (powered by Gemini) will respond!**

---

## 📊 **URLS**

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:3001 | Chat interface |
| **Backend** | http://localhost:8001 | API |
| **Health Check** | http://localhost:8001/health | Status |
| **API Docs** | http://localhost:8001/docs | Swagger UI |

---

## 🎨 **WHAT YOU'LL EXPERIENCE**

1. **Landing Page:** Black background, massive gold greetings rotating
2. **Language Select:** Click any flag (gold glow effect)
3. **Chat Interface:** Pure luxury black & gold theme
4. **Conversational AI:** Powered by Gemini - Queen responds naturally
5. **Menu System:** Gold floating menu with all features

---

## 📝 **NEXT STEPS**

1. Start: `./start-omakh.sh`
2. Wait for "OMAKH HIVE IS LIVE!" message
3. Browser opens automatically
4. Select language & theme
5. Start chatting!

---

## 🆘 **NEED HELP?**

- **Connection docs:** `QUEEN_FRONTEND_CONNECTION.md`
- **Full startup guide:** `STARTUP_GUIDE.md`
- **Luxury theme details:** `LUXURY_THEME_COMPLETE.md`

---

**🖤💛 Powered by Queen AI + Gemini 👑**
