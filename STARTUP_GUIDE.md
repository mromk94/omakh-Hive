# 👑 Omakh Hive - Startup Guide

## 🚀 **Quick Start - One Command!**

Start Queen AI Backend + Frontend with a single command:

```bash
./start-omakh.sh
```

**That's it!** The script will:
- ✅ Check configuration files
- ✅ Install dependencies if needed
- ✅ Start Queen AI backend (port 8001)
- ✅ Start Next.js frontend (port 3001)
- ✅ Wait for both to be ready
- ✅ Open browser automatically

---

## 🛑 **Stop Everything**

Graceful shutdown:

```bash
./stop-omakh.sh
```

Or just press **Ctrl+C** in the terminal running `start-omakh.sh`

---

## 🔄 **Reboot (Stop + Clear Cache + Restart)**

```bash
./reboot-omakh.sh
```

This will:
- Stop all services
- Clear Next.js cache
- Clear Python cache
- Restart everything fresh

---

## 📋 **Available Scripts**

| Script | Description |
|--------|-------------|
| `./start-omakh.sh` | Start Queen + Frontend |
| `./stop-omakh.sh` | Stop all services |
| `./reboot-omakh.sh` | Clean restart |

---

## 🔍 **What Runs Where**

| Service | URL | Description |
|---------|-----|-------------|
| **Queen AI** | http://localhost:8001 | Backend API + Gemini AI |
| **Frontend** | http://localhost:3001 | Chat interface |
| **Health Check** | http://localhost:8001/health | Backend status |
| **API Docs** | http://localhost:8001/docs | Swagger docs |

---

## 📊 **Check Logs**

Logs are saved in `/logs/` directory:

```bash
# Backend logs
tail -f logs/queen-backend.log

# Frontend logs
tail -f logs/frontend.log
```

---

## ⚙️ **First Time Setup**

### **1. Backend Configuration**

The script will check for `.env` file. If missing, it creates one from template.

**Edit:** `backend/queen-ai/.env`

**Required:**
```bash
# Google Gemini API (Primary LLM)
GOOGLE_API_KEY=your_gemini_api_key_here

# Database
DATABASE_URL=sqlite:///./queen.db

# Environment
ENVIRONMENT=development
```

**Optional:**
```bash
# Fallback LLMs
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Blockchain
ETHEREUM_RPC_URL=your_infura_or_alchemy_url
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
```

### **2. Frontend Configuration**

Auto-created if missing: `omk-frontend/.env.local`

```bash
NEXT_PUBLIC_QUEEN_API_URL=http://localhost:8001
```

---

## 🐛 **Troubleshooting**

### **"Port already in use"**

```bash
# Kill processes on port 8001
lsof -ti:8001 | xargs kill -9

# Kill processes on port 3001  
lsof -ti:3001 | xargs kill -9

# Then restart
./start-omakh.sh
```

### **"Queen not responding"**

Check backend logs:
```bash
tail -f logs/queen-backend.log
```

Common issues:
- Missing Gemini API key
- Database connection failed
- Port conflict

### **"Frontend won't start"**

```bash
cd omk-frontend
rm -rf .next node_modules
npm install
cd ..
./start-omakh.sh
```

### **"Connection Status: Red Dot"**

This means frontend can't reach backend:
1. Check if backend is running: `curl http://localhost:8001/health`
2. Check backend logs: `tail logs/queen-backend.log`
3. Try reboot: `./reboot-omakh.sh`

---

## 🎯 **Development Workflow**

### **Normal Development:**
```bash
./start-omakh.sh
# Make changes to code
# Hot reload works for both frontend and backend
```

### **After Major Changes:**
```bash
./reboot-omakh.sh  # Fresh start with cache clear
```

### **End of Day:**
```bash
./stop-omakh.sh  # Graceful shutdown
```

---

## 🔥 **Manual Start (Advanced)**

If you need to start services separately:

### **Backend Only:**
```bash
cd backend/queen-ai
source venv/bin/activate
python main.py
```

### **Frontend Only:**
```bash
cd omk-frontend
npm run dev
```

---

## 🌟 **Features**

### **Automatic Startup Script:**
- ✅ Dependency checking
- ✅ Port availability check
- ✅ Health monitoring
- ✅ Graceful shutdown (Ctrl+C)
- ✅ Browser auto-open
- ✅ Color-coded output

### **Automatic Connection:**
- ✅ Frontend → Backend API
- ✅ Backend → Gemini AI
- ✅ Real-time status indicator
- ✅ Auto-reconnect on network issues

---

## 📦 **Project Structure**

```
omakh-Hive/
├── start-omakh.sh       ← Start everything
├── stop-omakh.sh        ← Stop everything
├── reboot-omakh.sh      ← Reboot everything
├── logs/                ← Log files
│   ├── queen-backend.log
│   └── frontend.log
├── backend/queen-ai/    ← Queen AI Backend
│   ├── .env            ← Configuration
│   ├── main.py         ← Entry point
│   └── venv/           ← Python env
└── omk-frontend/        ← Next.js Frontend
    ├── .env.local      ← Frontend config
    └── app/            ← Pages
```

---

## 🎨 **What You'll See**

### **When Starting:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         👑  OMAKH HIVE - STARTUP  👑         
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅  Configuration verified

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🤖  Starting Queen AI Backend...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀  Launching Queen AI on port 8001...
✅  Queen AI started (PID: 12345)
⏳  Waiting for Queen AI to initialize...
✅  Queen AI is operational!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📱  Starting Frontend...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀  Launching Next.js on port 3001...
✅  Frontend started (PID: 12346)
⏳  Waiting for Frontend to initialize...
✅  Frontend is ready!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         ✅  OMAKH HIVE IS LIVE!  ✅         
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖  Queen AI Backend:  http://localhost:8001
📱  Frontend:          http://localhost:3001

💡  Press Ctrl+C to stop all services
```

### **In Browser:**
- Black background with gold theme
- Wiggling gold crown 👑
- Green connection dot (Queen is live!)
- "OMK Queen [LIVE]" badge
- Chat powered by Gemini AI

---

## 🎯 **Next Steps**

1. **Start the system:** `./start-omakh.sh`
2. **Open browser:** http://localhost:3001
3. **Select language** (flag icons)
4. **Choose theme** (dark/light)
5. **Start chatting** with Queen AI!

---

## 📞 **Support**

- **Logs:** Check `logs/` directory
- **Health:** http://localhost:8001/health
- **API Docs:** http://localhost:8001/docs
- **Connection docs:** See `QUEEN_FRONTEND_CONNECTION.md`

---

**Powered by Queen AI 👑 + Gemini AI 🤖**
