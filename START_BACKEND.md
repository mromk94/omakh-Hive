# 🚀 How to Start the Backend

## ✅ **FIXED: Import Error**

The `ModuleNotFoundError: No module named 'app.core.database'` has been fixed in `websocket.py`.

---

## 🔧 **Start Backend (Correct Way)**

### **Option 1: Using start.py (Recommended)**
```bash
cd backend/queen-ai
python3 start.py --component queen
```

### **Option 2: Using venv directly**
```bash
cd backend/queen-ai

# Activate virtual environment
source venv/bin/activate

# Start server
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### **Option 3: Using manage script**
```bash
cd backend/queen-ai
./manage.py start
```

---

## ❌ **Common Errors & Solutions**

### **Error: `ModuleNotFoundError: No module named 'fastapi'`**
**Cause:** Virtual environment not activated

**Solution:**
```bash
cd backend/queen-ai
source venv/bin/activate
python3 main.py
```

### **Error: `ModuleNotFoundError: No module named 'app.core.database'`**
**Cause:** Wrong import in websocket.py

**Solution:** ✅ Already fixed!

### **Error: `Database connection failed`**
**Cause:** MySQL not running

**Solution:**
```bash
# Start MySQL
brew services start mysql

# Or on Linux
sudo systemctl start mysql
```

---

## ✅ **Verify It's Running**

```bash
# Check process
lsof -i :8001

# Test health endpoint
curl http://localhost:8001/health

# Should return: {"status": "healthy"}
```

---

## 📝 **What Was Fixed**

### **In `websocket.py`:**

**Before (❌ Broken):**
```python
from app.core.database import DatabaseManager  # This module doesn't exist!
```

**After (✅ Fixed):**
```python
import app.models.database as db  # Correct import matching other files
```

All database manager references removed and replaced with direct `db` module calls.

---

## 🚀 **Start Now:**

```bash
cd /Users/mac/CascadeProjects/omakh-Hive/backend/queen-ai
python3 start.py --component queen
```

This should work now! ✅
