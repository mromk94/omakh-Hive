# 🔄 SERVER RESTART REQUIRED

**Critical:** Backend server MUST be restarted to load all the changes!

---

## 🚨 **WHY RESTART IS NEEDED**

We made several changes to `main.py`:

1. ✅ Added `notifications.router`
2. ✅ Added `claude_analysis.router`  
3. ✅ Added `queen.router` (for chat to work)
4. ✅ Added `queen_dev.router` (for development chat)

**None of these are active until the server restarts!**

---

## 🚀 **RESTART INSTRUCTIONS**

### **Step 1: Stop Backend**

If running in terminal:
```bash
# Press Ctrl+C in the terminal window where backend is running
^C  # This stops the server
```

Or if running as background process:
```bash
# Find and kill the process
lsof -ti:8001 | xargs kill -9
```

---

### **Step 2: Start Backend Fresh**

```bash
cd /Users/mac/CascadeProjects/omakh-Hive/backend/queen-ai

# Activate virtual environment
source venv/bin/activate

# Start server
python main.py
```

**Wait for these messages:**
```
✅ Database schema initialized
✅ Queen AI ready and operational
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
```

---

### **Step 3: Verify Backend is Running**

Test in another terminal:
```bash
# Test health endpoint
curl http://localhost:8001/health

# Should return:
{
  "service": "Queen AI Orchestrator",
  "version": "1.0.0",
  "environment": "development",
  "status": "healthy"
}
```

---

### **Step 4: Test Auth Endpoint**

```bash
# Test login endpoint
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "king@omakh.io",
    "password": "Admin2025!!"
  }'

# Should return:
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "king@omakh.io",
    "role": "admin"
  }
}
```

---

### **Step 5: Clear Browser & Test Frontend**

```bash
# In browser DevTools Console (F12):
localStorage.clear()
# Then refresh page

# Or just hard refresh:
# Mac: Cmd + Shift + R
# Windows/Linux: Ctrl + Shift + R
```

---

## 🎯 **FULL CLEAN RESTART SEQUENCE**

```bash
# ========================================
# Terminal 1: Backend
# ========================================

cd /Users/mac/CascadeProjects/omakh-Hive/backend/queen-ai

# Kill any existing backend
lsof -ti:8001 | xargs kill -9

# Start fresh
source venv/bin/activate
python main.py

# Wait for "✅ Queen AI ready and operational"

# ========================================
# Terminal 2: Frontend (optional restart)
# ========================================

cd /Users/mac/CascadeProjects/omakh-Hive/omk-frontend
npm run dev

# ========================================
# Browser
# ========================================

# 1. Open DevTools (F12)
# 2. Console tab
# 3. Run: localStorage.clear()
# 4. Go to: http://localhost:3000/kingdom/login
# 5. Login: king@omakh.io / Admin2025!!
# 6. Should work within 5 seconds ✅
```

---

## 🐛 **IF STILL LAGGING**

### **Check Backend Logs:**

Look for errors in the terminal where backend is running:

**Good:**
```
✅ Queen AI ready and operational
INFO:     127.0.0.1:54321 - "POST /api/v1/auth/login HTTP/1.1" 200 OK
```

**Bad:**
```
ERROR:    Exception in ASGI application
❌ Database connection failed
```

---

### **Check Database Connection:**

```bash
cd /Users/mac/CascadeProjects/omakh-Hive/backend/queen-ai
source venv/bin/activate
python

>>> from app.database.connection import SessionLocal
>>> db = SessionLocal()
>>> from sqlalchemy import text
>>> db.execute(text("SELECT 1")).fetchone()
(1,)  # ✅ Good!

# If this hangs or errors, database issue!
```

---

### **Check MySQL is Running:**

```bash
# macOS (if using brew)
brew services list | grep mysql

# Should show:
# mysql  started

# If not:
brew services start mysql
```

---

### **Common Issues:**

1. **Port 8001 Already in Use:**
   ```bash
   lsof -ti:8001 | xargs kill -9
   ```

2. **Database Not Running:**
   ```bash
   brew services start mysql
   ```

3. **Wrong Directory:**
   ```bash
   # Must be in backend/queen-ai
   pwd
   # Should show: .../backend/queen-ai
   ```

4. **Virtual Environment Not Activated:**
   ```bash
   which python
   # Should show: .../venv/bin/python
   
   # If not:
   source venv/bin/activate
   ```

---

## ✅ **VERIFICATION**

After restart, test everything:

### **1. Backend Health:**
```bash
curl http://localhost:8001/health
# Should return JSON immediately
```

### **2. Backend Docs:**
Visit: http://localhost:8001/docs
- Should see Swagger UI
- Check for `/auth/me` endpoint
- Check for `/queen-dev/chat` endpoint
- Check for `/admin/notifications` endpoint

### **3. Login Flow:**
1. Go to http://localhost:3000/kingdom/login
2. Clear localStorage (F12 → Console → `localStorage.clear()`)
3. Enter: king@omakh.io / Admin2025!!
4. Should redirect to dashboard within 2-3 seconds

### **4. Dashboard Loads:**
- User profile shows real name (not "A")
- Hive badge shows number (not hardcoded)
- OTC badge shows count
- No infinite loading

---

## 🎯 **EXPECTED BEHAVIOR**

### **Before Restart:**
```
❌ Login hangs
❌ "Loading Kingdom..." forever
❌ 5-second timeout triggers
❌ Redirects back to login
❌ Chat endpoints 404
```

### **After Restart:**
```
✅ Login responds in 1-2 seconds
✅ Dashboard loads quickly
✅ User profile shows correctly
✅ Real badge counts
✅ All chat endpoints work
✅ No timeouts
```

---

## 🔥 **QUICK RESTART COMMAND**

One-liner to restart everything:

```bash
# Stop backend, start fresh
cd /Users/mac/CascadeProjects/omakh-Hive/backend/queen-ai && \
lsof -ti:8001 | xargs kill -9 2>/dev/null; \
source venv/bin/activate && \
python main.py
```

---

## 📊 **WHAT GOT CHANGED**

Total changes in this session:

### **Backend (`main.py`):**
- Line 91: Added imports for notifications, claude_analysis, queen, queen_dev
- Line 98-99: Registered notifications.router
- Line 100-101: Registered queen.router and queen_dev.router

### **Frontend (`page.tsx`):**
- Added 5-second timeout to auth check
- Added better error logging
- Improved user profile display
- Added real badge counts

### **New Files Created:**
- `/backend/queen-ai/app/api/v1/notifications.py`
- `/backend/queen-ai/app/api/v1/claude_analysis.py`

**ALL REQUIRE SERVER RESTART TO TAKE EFFECT!**

---

## ✅ **CONFIRMATION**

After restart, you should see in backend logs:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
🚀 Starting Queen AI Orchestrator
🗄️  Initializing MySQL database...
✅ Database schema initialized
✅ Queen AI ready and operational
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

And in browser console (after login):
```
✅ No timeout errors
✅ User data loads
✅ Dashboard renders
```

---

**TL;DR: YES, restart the backend server!** 🔄
