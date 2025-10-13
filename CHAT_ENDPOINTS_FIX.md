# 🚨 CHAT ENDPOINTS - BROKEN & FIX

**Issue Found:** Chat endpoints exist but are NOT registered in `main.py`

---

## 🔍 **ROOT CAUSE**

### **What's Broken:**
In `/backend/queen-ai/main.py`:

```python
# Line 91: Imports queen_dev but...
from app.api.v1 import auth, queen, queen_dev, health, admin, frontend, market, notifications, claude_analysis

# Lines 94-99: NEVER includes queen_dev.router!
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(frontend.router, prefix="/api/v1")
app.include_router(market.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1/admin")
app.include_router(claude_analysis.router, prefix="/api/v1/admin")
# ❌ queen_dev.router is MISSING!
# ❌ queen.router is also MISSING!
```

---

## 📋 **MISSING ENDPOINTS**

### **1. Queen Development Chat** ❌
**Frontend calls:** `POST /api/v1/queen-dev/chat`  
**Backend has:** ✅ `/app/api/v1/queen_dev.py` line 81  
**Registered:** ❌ NO - router not included in main.py

### **2. Queen Development Endpoints** ❌
- `POST /api/v1/queen-dev/chat` - Chat with Claude
- `GET /api/v1/queen-dev/conversation-history` - Load history
- `GET /api/v1/queen-dev/proposals` - List proposals
- `POST /api/v1/queen-dev/analyze-system` - System analysis
- `POST /api/v1/queen-dev/proposals/{id}/approve` - Approve
- `POST /api/v1/queen-dev/proposals/{id}/reject` - Reject
- And more...

**All exist but NOT accessible!**

### **3. Queen Chat (Admin)** ✅ WORKING
**Frontend calls:** `POST /api/v1/admin/queen/chat`  
**Backend has:** ✅ `/app/api/v1/admin.py` line 237  
**Registered:** ✅ YES - admin.router IS included

This one should work!

---

## ✅ **THE FIX**

Add the missing routers to `main.py`:

```python
# In main.py around line 99, add:
app.include_router(queen.router, prefix="/api/v1")
app.include_router(queen_dev.router, prefix="/api/v1")
```

---

## 🎯 **EXPECTED RESULT**

After fix, these endpoints will be available:

### **Queen Development:**
- ✅ `POST /api/v1/queen-dev/chat`
- ✅ `GET /api/v1/queen-dev/conversation-history`
- ✅ `GET /api/v1/queen-dev/proposals`
- ✅ `POST /api/v1/queen-dev/analyze-system`
- ✅ `POST /api/v1/queen-dev/proposals/{id}/approve`
- ✅ `POST /api/v1/queen-dev/proposals/{id}/reject`
- ✅ `POST /api/v1/queen-dev/proposals/{id}/deploy-sandbox`
- ✅ `POST /api/v1/queen-dev/proposals/{id}/run-tests`
- ✅ `POST /api/v1/queen-dev/reboot-system`

### **Queen Basic:**
- ✅ `POST /api/v1/queen/analyze`
- ✅ `POST /api/v1/queen/decide`
- ✅ `GET /api/v1/queen/health`

### **Already Working:**
- ✅ `POST /api/v1/admin/queen/chat` (QueenChatInterface)
- ✅ `GET /api/v1/admin/queen/bees`
- ✅ `GET /api/v1/admin/queen/status`
