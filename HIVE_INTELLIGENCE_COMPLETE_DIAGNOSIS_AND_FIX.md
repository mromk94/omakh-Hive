# 🐝 HIVE INTELLIGENCE - COMPLETE DIAGNOSIS & FIX

**Date:** October 13, 2025, 6:15 PM  
**Status:** ROOT CAUSE IDENTIFIED - Multiple critical bugs found

---

## 🚨 **CRITICAL BUGS FOUND**

### **BUG #1: WebSocket Returns Empty Data (CRITICAL)**

**File:** `/backend/queen-ai/app/api/v1/websocket.py`  
**Lines:** 203-211

**Problem:**
```python
async def get_hive_data() -> dict:
    """Get all hive intelligence data"""
    try:
        # Placeholder - will be filled with real data from Queen state
        # For now, return empty data
        return {}  # ❌ EMPTY DICT!
    except Exception as e:
        logger.error(f"Error fetching hive data: {e}")
        return {}
```

**Impact:**
- WebSocket connects successfully ✅
- But sends `{"type": "hive_update", "data": {}}` 
- Frontend receives empty data
- All stats show 0 or nothing
- **THIS IS THE MAIN PROBLEM!**

---

### **BUG #2: Duplicate Queen Assignment**

**File:** `/backend/queen-ai/app/api/v1/admin.py`  
**Line:** 772

**Problem:**
```python
try:
    queen = request.app.state.queen
except AttributeError:
    # Handle queen not initialized
    return {...}

queen = request.app.state.queen  # ❌ DUPLICATE! Will throw error if not initialized
```

**Impact:**
- If Queen not initialized, exception handler returns early ✅
- But line 772 tries to access queen again ❌
- Will throw AttributeError even after handling it

---

### **BUG #3: Missing Fields in Fallback Response**

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

**Impact:**
- When Queen not initialized, frontend gets partial queen object
- Accessing `.running` or `.decision_count` causes TypeError
- UI breaks or shows "undefined"

---

### **BUG #4: get_bee_data() Also Returns Empty**

**File:** `/backend/queen-ai/app/api/v1/websocket.py`  
**Lines:** 244-256

**Problem:**
```python
async def get_bee_data() -> dict:
    """Get bee monitoring data"""
    try:
        # Placeholder for bee data
        return {
            "bees": [],
            "total": 0,
            "active": 0,
            "idle": 0
        }
```

**Impact:**
- Bee WebSocket also doesn't work properly
- Returns placeholder data

---

## ✅ **THE FIXES**

### **FIX #1: Implement get_hive_data() (PRIORITY 1)**

**File:** `/backend/queen-ai/app/api/v1/websocket.py`

**Replace lines 203-211 with:**
```python
async def get_hive_data() -> dict:
    """Get all hive intelligence data from Queen state"""
    try:
        from fastapi import Request
        from starlette.requests import Request as StarletteRequest
        
        # Access app state - this requires request context
        # Alternative: Store queen reference globally or pass it
        
        # For now, import the initialized queen from main
        # This is a temporary fix until proper dependency injection
        from app.core.orchestrator import QueenOrchestrator
        
        # Try to get queen from request context (if available)
        # Otherwise create temporary connection
        
        # BETTER APPROACH: Accept queen as parameter
        return {}  # Will fix in implementation
        
    except Exception as e:
        logger.error(f"Error fetching hive data: {e}")
        return {}
```

**Actually, the REAL fix needs access to Queen. Let me redesign:**

```python
# At top of websocket.py, add:
queen_instance = None

def set_queen_instance(queen):
    """Set global queen instance for WebSocket access"""
    global queen_instance
    queen_instance = queen

async def get_hive_data() -> dict:
    """Get all hive intelligence data"""
    global queen_instance
    
    if not queen_instance:
        logger.warning("Queen not initialized for WebSocket")
        return {
            "overview": {},
            "message_stats": {},
            "board_stats": {},
            "bee_performance": {},
            "live_activity": []
        }
    
    try:
        queen = queen_instance
        
        # Message bus stats
        message_stats = queen.message_bus.get_communication_stats()
        
        # Hive board stats
        board_stats = await queen.hive_board.get_stats()
        
        # Bee performance
        bee_performance = {}
        for bee_name, bee in queen.bee_manager.bees.items():
            bee_performance[bee_name] = {
                "task_count": bee.task_count,
                "success_count": bee.success_count,
                "error_count": bee.error_count,
                "success_rate": (bee.success_count / bee.task_count * 100) if bee.task_count > 0 else 0,
                "last_task_time": bee.last_task_time.isoformat() if bee.last_task_time else None,
                "status": bee.status,
                "llm_enabled": bee.llm_enabled
            }
        
        # Live activity
        from datetime import datetime
        now = datetime.utcnow()
        active_tasks = []
        for bee_name, bee in queen.bee_manager.bees.items():
            if bee.last_task_time:
                time_diff = (now - bee.last_task_time).total_seconds()
                if time_diff < 10:
                    active_tasks.append({
                        "bee_name": bee_name,
                        "status": bee.status,
                        "last_active": bee.last_task_time.isoformat(),
                        "seconds_ago": int(time_diff)
                    })
        
        # Bee health
        bee_health = await queen.bee_manager.check_all_health()
        active_count = sum(1 for bee in queen.bee_manager.bees.values() 
                          if bee.last_task_time and (now - bee.last_task_time).total_seconds() < 10)
        
        # Overview
        overview = {
            "message_bus": {
                "total_messages": message_stats["total_messages"],
                "delivery_rate": message_stats["delivery_rate"],
                "active_bees": message_stats["active_bees"]
            },
            "hive_board": {
                "total_posts": board_stats["total_posts"],
                "active_categories": board_stats["active_categories"],
                "total_subscribers": board_stats["total_subscribers"]
            },
            "bees": {
                "total": len(queen.bee_manager.bees),
                "healthy": len([b for b in bee_health["bees"].values() if b["status"] == "active"]),
                "currently_active": active_count
            },
            "queen": {
                "initialized": queen.initialized,
                "running": queen.running,
                "decision_count": queen.decision_count
            }
        }
        
        return {
            "overview": overview,
            "message_stats": message_stats,
            "board_stats": board_stats,
            "bee_performance": bee_performance,
            "live_activity": active_tasks
        }
        
    except Exception as e:
        logger.error(f"Error fetching hive data: {e}", exc_info=True)
        return {
            "overview": {},
            "message_stats": {},
            "board_stats": {},
            "bee_performance": {},
            "live_activity": []
        }
```

**And in main.py, after queen initialization:**
```python
from app.api.v1.websocket import set_queen_instance

# After queen.initialize()
set_queen_instance(queen)
logger.info("✅ Queen instance set for WebSocket access")
```

---

### **FIX #2: Remove Duplicate Queen Assignment**

**File:** `/backend/queen-ai/app/api/v1/admin.py`

**Delete line 772:**
```python
# Line 772 - DELETE THIS
queen = request.app.state.queen  # ❌ Remove this line
```

---

### **FIX #3: Add Missing Fields to Fallback**

**File:** `/backend/queen-ai/app/api/v1/admin.py`

**Replace lines 764-769:**
```python
# OLD:
"queen": {"status": "not_initialized", "uptime_seconds": 0}

# NEW:
"queen": {
    "status": "not_initialized",
    "initialized": False,
    "running": False,
    "decision_count": 0
}
```

---

### **FIX #4: Implement get_bee_data()**

**File:** `/backend/queen-ai/app/api/v1/websocket.py`

**Replace lines 244-256:**
```python
async def get_bee_data() -> dict:
    """Get bee monitoring data"""
    global queen_instance
    
    if not queen_instance:
        return {
            "bees": [],
            "total": 0,
            "active": 0,
            "idle": 0
        }
    
    try:
        queen = queen_instance
        from datetime import datetime
        now = datetime.utcnow()
        
        bees = []
        for bee_name, bee in queen.bee_manager.bees.items():
            bees.append({
                "name": bee_name,
                "status": bee.status,
                "task_count": bee.task_count,
                "success_rate": (bee.success_count / bee.task_count * 100) if bee.task_count > 0 else 0,
                "last_active": bee.last_task_time.isoformat() if bee.last_task_time else None,
                "llm_enabled": bee.llm_enabled
            })
        
        active = sum(1 for bee in queen.bee_manager.bees.values() 
                    if bee.last_task_time and (now - bee.last_task_time).total_seconds() < 30)
        
        return {
            "bees": bees,
            "total": len(bees),
            "active": active,
            "idle": len(bees) - active
        }
    except Exception as e:
        logger.error(f"Error fetching bee data: {e}")
        return {
            "bees": [],
            "total": 0,
            "active": 0,
            "idle": 0
        }
```

---

## 📊 **SUMMARY**

**Root Cause:**
- WebSocket endpoint exists but returns empty data
- `get_hive_data()` was a placeholder that was never implemented

**Why It Broke:**
- Frontend connects to WebSocket ✅
- WebSocket accepts connection ✅
- WebSocket sends updates every 5 seconds ✅
- **But sends empty dict `{}`** ❌
- Frontend receives `{type: "hive_update", data: {}}` ❌
- All state variables remain null/empty ❌

**Impact:**
- Hive Intelligence shows no data
- All stats display 0 or nothing
- WebSocket appears "connected" (green indicator)
- But no actual data flows

---

## 🔧 **IMPLEMENTATION PLAN**

**Step 1:** Add queen instance management to websocket.py  
**Step 2:** Implement get_hive_data() with real Queen data  
**Step 3:** Implement get_bee_data() with real Queen data  
**Step 4:** Fix admin.py bugs (duplicate assignment, missing fields)  
**Step 5:** Update main.py to set queen instance for WebSocket  
**Step 6:** Test WebSocket connection and data flow  

**Time Estimate:** 15-20 minutes

**Should I implement these fixes now?**
