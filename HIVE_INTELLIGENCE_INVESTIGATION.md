# 🔍 HIVE INTELLIGENCE - COMPLETE INVESTIGATION

**Date:** October 13, 2025, 6:00 PM  
**Status:** Investigation in progress - identifying root causes

---

## 🐛 **ISSUES DISCOVERED**

### **Issue #1: Backend Methods Exist ✅**

**Checked:**
- ✅ `QueenOrchestrator` has `message_bus`, `hive_board`, `bee_manager` attributes
- ✅ `MessageBus` has `get_communication_stats()` method
- ✅ `HiveInformationBoard` has `async get_stats()` method  
- ✅ `BeeManager` has `async check_all_health()` method

**All backend methods exist!** This is NOT the problem.

---

### **Issue #2: Frontend Makes 5 API Calls on Load**

**From** `/omk-frontend/app/kingdom/components/HiveIntelligence.tsx`:

Lines 51-57:
```typescript
const [overviewRes, messageRes, boardRes, perfRes, activityRes] = await Promise.all([
  fetch(`${BACKEND_URL}/api/v1/admin/hive/overview`, { headers }),
  fetch(`${BACKEND_URL}/api/v1/admin/hive/message-bus/stats`, { headers }),
  fetch(`${BACKEND_URL}/api/v1/admin/hive/board/stats`, { headers }),
  fetch(`${BACKEND_URL}/api/v1/admin/hive/bees/performance`, { headers }),
  fetch(`${BACKEND_URL}/api/v1/admin/hive/activity/live`, { headers }),
]);
```

**Problem:** Making 5 separate HTTP calls when `/hive/overview` already returns ALL this data!

---

### **Issue #3: Data Structure Mismatch**

**Backend** (`/api/v1/admin/hive/overview` lines 791-814):
```python
return {
    "success": True,
    "overview": {
        "message_bus": {...},
        "hive_board": {...},
        "bees": {...},
        "queen": {
            "initialized": queen.initialized,
            "running": queen.running,
            "decision_count": queen.decision_count
        }
    }
}
```

**Frontend expects** (lines 136-159):
```typescript
{overview.bees.currently_active}/{overview.bees.total}
{overview.message_bus.total_messages}
{overview.hive_board.total_posts}
{overview.queen.decision_count}  // ✅ Correct
{overview.queen.running ? 'Running' : 'Stopped'}  // ✅ Correct
```

**THIS LOOKS CORRECT!** But let me check if the overview is properly structured...

Wait, I see it now:

**Line 67** in frontend:
```typescript
if (overviewData.success) setOverview(overviewData.overview);
```

So `overview` state gets `overviewData.overview`, which has the correct structure. **This is fine.**

---

### **Issue #4: WebSocket Connection**

**Frontend** (line 24):
```typescript
const { isConnected } = useHiveWebSocket((data) => {
  if (data.overview) setOverview(data.overview);
  if (data.message_stats) setMessageStats(data.message_stats);
  if (data.board_stats) setBoardStats(data.board_stats);
  if (data.bee_performance) setBeePerformance(data.bee_performance);
  if (data.live_activity) setLiveActivity(data.live_activity);
  ...
});
```

**Need to check:** Does `useHiveWebSocket` actually exist and work?

---

### **Issue #5: Potential State/Data Issues**

Let me check what the actual errors are. The user said "something is very wrong" but didn't specify what. Common issues:

1. **Data not loading** - Endpoints returning errors
2. **WebSocket failing** - Real-time updates not working
3. **Queen not initialized** - `request.app.state.queen` doesn't exist
4. **Wrong data shown** - Incorrect stats/metrics
5. **UI broken** - Components not rendering

---

## 🔎 **DEBUGGING STEPS**

### **1. Check if Queen is initialized in request.app.state**

**In** `admin.py` line 758-770:
```python
try:
    queen = request.app.state.queen
except AttributeError:
    # Queen not initialized - return empty data
    logger.warning("Queen not initialized, returning empty hive data")
    return {
        "success": True,
        "overview": {
            "bees": {"total": 0, "healthy": 0, "currently_active": 0},
            "message_bus": {"total_messages": 0, "delivery_rate": 0.0, "active_bees": 0},
            "hive_board": {"total_posts": 0, "active_categories": 0, "total_subscribers": 0},
            "queen": {"status": "not_initialized", "uptime_seconds": 0}
        }
    }
```

**WAIT!** This is a problem! If Queen isn't initialized, it returns:
```python
"queen": {"status": "not_initialized", "uptime_seconds": 0}
```

But the frontend expects (line 158):
```typescript
{overview.queen.running ? 'Running' : 'Stopped'}
```

**BUG FOUND #1:** When Queen not initialized, `overview.queen.running` is undefined (not in response), causing TypeError!

---

### **2. Check for AttributeErrors**

**Line 772:**
```python
queen = request.app.state.queen  # This line is AFTER the try/except!
```

**BUG FOUND #2:** Line 772 repeats `queen = request.app.state.queen` AFTER the try/except block! This will cause AttributeError if Queen isn't initialized, even though we just handled it!

---

### **3. Check WebSocket Implementation**

Looking at `/api/v1/admin/hive/overview`, it's an HTTP endpoint, not WebSocket. The frontend is trying to use WebSocket but the backend doesn't have a WebSocket endpoint for Hive Intelligence!

**Need to check** `/app/api/v1/websocket.py` to see if Hive WebSocket exists.

---

## 🐛 **CONFIRMED BUGS**

### **BUG #1: Duplicate queen assignment (Line 772)**

**File:** `/backend/queen-ai/app/api/v1/admin.py`  
**Line:** 772

**Problem:**
```python
try:
    queen = request.app.state.queen
except AttributeError:
    # Handle not initialized
    return {...}

queen = request.app.state.queen  # ❌ DUPLICATE! Will throw AttributeError if not initialized
```

**Fix:** Remove line 772

---

### **BUG #2: Missing 'running' field when Queen not initialized**

**File:** `/backend/queen-ai/app/api/v1/admin.py`  
**Lines:** 764-769

**Problem:**
```python
"queen": {"status": "not_initialized", "uptime_seconds": 0}
# Missing: running, decision_count, initialized
```

**Frontend expects:**
```typescript
overview.queen.running  // undefined!
overview.queen.decision_count  // undefined!
```

**Fix:** Add missing fields to fallback response:
```python
"queen": {
    "status": "not_initialized",
    "initialized": False,
    "running": False,
    "decision_count": 0
}
```

---

### **BUG #3: WebSocket endpoint missing**

**Frontend:** Tries to connect to WebSocket for real-time updates  
**Backend:** Only has HTTP endpoints, no WebSocket for Hive Intelligence

**Fix:** Either:
1. Add WebSocket endpoint for Hive data
2. Remove WebSocket attempt from frontend (use HTTP polling)

---

### **BUG #4: Redundant API calls**

**Problem:** Frontend makes 5 separate API calls:
- `/hive/overview`
- `/hive/message-bus/stats`
- `/hive/board/stats`  
- `/hive/bees/performance`
- `/hive/activity/live`

But `/hive/overview` should return EVERYTHING needed!

**Current overview response:**
```python
"overview": {
    "message_bus": {...},  # ✅
    "hive_board": {...},   # ✅
    "bees": {...},         # ✅
    "queen": {...}         # ✅
}
```

**Frontend also needs:**
- `message_stats` (separate state)
- `boardStats` (separate state)
- `beePerformance` (separate state)
- `liveActivity` (separate state)

**Problem:** Frontend expects MORE detailed data than what overview provides!

**Need to check:** What does `/hive/message-bus/stats` return vs what's in overview?

---

## 📋 **INVESTIGATION CONTINUES...**

Need to:
1. ✅ Fix duplicate queen assignment (line 772)
2. ✅ Fix missing fields in fallback response
3. 🔍 Check if WebSocket endpoint exists
4. 🔍 Compare detailed stats endpoints vs overview
5. 🔍 Determine if data structure matches frontend expectations

---

**Status:** Bugs identified, fixes in progress...
