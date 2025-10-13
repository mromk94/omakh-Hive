# 🔧 AUTO-FIX TROUBLESHOOTING

**Issue:** "Auto fix failed, manual intervention needed"

---

## 🐛 **MOST LIKELY CAUSES**

### **1. Backend Not Restarted** ⭐ **MOST COMMON**
The new auto-fix code was added but the backend server needs to be restarted.

**Fix:**
```bash
# Stop the backend
# Then restart:
cd backend/queen-ai
python main.py
```

---

### **2. Import Error**
The `proposal_auto_fix` module might not be properly loaded.

**Check:**
- ✅ File exists: `app/api/v1/proposal_auto_fix.py`
- ✅ File exists: `app/core/proposal_auto_fixer.py`  
- ✅ Module registered in `main.py` line 91

**Already Done:**
```python
# main.py line 91
from app.api.v1 import ... proposal_auto_fix

# main.py line 100
app.include_router(proposal_auto_fix.router, prefix="/api/v1/admin/proposals")
```

---

### **3. Proposal Not in Correct Status**
Auto-fix only works when `proposal.status === 'tests_failed'`

**Check:**
```
Open browser console (F12)
Look at the proposal object
Verify: proposal.status = "tests_failed"
```

**If status is different:**
- Make sure tests actually ran and failed
- Check test results exist

---

### **4. Claude API Error**
The ANTHROPIC_API_KEY might be invalid or quota exceeded.

**Verify:**
```bash
# Check if key is set
cat backend/queen-ai/.env | grep ANTHROPIC_API_KEY

# Should show:
ANTHROPIC_API_KEY=sk-ant-api03-...
```

**Test Claude directly:**
```bash
cd backend/queen-ai
python3 << EOF
from app.llm.providers.anthropic import AnthropicProvider
import asyncio

async def test():
    provider = AnthropicProvider()
    await provider.initialize()
    response = await provider.generate("Say hello", max_tokens=50)
    print(f"✅ Claude works: {response[:50]}")

asyncio.run(test())
EOF
```

---

### **5. Backend Error Response**
Check what error the backend is actually returning.

**Debug in Browser:**
1. Open Developer Tools (F12)
2. Go to Network tab
3. Click "Auto-Fix & Retry"
4. Look at the request to `/api/v1/admin/proposals/auto-fix/{id}`
5. Check the Response tab

**Common Errors:**
```json
// Error 1: Module not found
{
  "detail": "Internal Server Error"
}

// Error 2: Claude API failed
{
  "success": false,
  "error": "Claude API key not configured"
}

// Error 3: Proposal not found
{
  "detail": "Proposal not found"
}

// Error 4: Wrong status
{
  "success": false,
  "error": "Proposal has not failed tests. Current status: proposed"
}
```

---

## ✅ **QUICK FIX STEPS**

### **Step 1: Restart Backend**
```bash
# Kill current backend process
# Ctrl+C in terminal

# Restart
cd backend/queen-ai
python main.py

# Look for these lines in output:
# "✅ Queen AI ready and operational"
# Should NOT see import errors
```

### **Step 2: Verify Endpoint Exists**
```bash
# Check if endpoint is registered
curl http://localhost:8001/docs

# Search for: POST /api/v1/admin/proposals/auto-fix/{proposal_id}
# Should be visible in Swagger docs
```

### **Step 3: Test Endpoint Manually**
```bash
# Get your auth token
TOKEN="your_token_here"

# Get proposal ID from failed proposal
PROPOSAL_ID="your_proposal_id_here"

# Test the endpoint
curl -X POST \
  "http://localhost:8001/api/v1/admin/proposals/auto-fix/${PROPOSAL_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json"

# Should return JSON with success/error
```

### **Step 4: Check Backend Logs**
```bash
# If backend is running, check terminal output
# Look for error messages like:
# "❌ Auto-fix failed: ..."
# "ModuleNotFoundError: ..."
# "KeyError: ..."
```

---

## 🔍 **DETAILED DEBUGGING**

### **Enable Debug Logging:**

1. Edit `backend/queen-ai/.env`:
```bash
LOG_LEVEL=DEBUG  # Change from INFO to DEBUG
```

2. Restart backend

3. Try auto-fix again

4. Check logs for detailed error info

---

### **Test Each Component:**

**Test 1: Proposal System Works**
```bash
cd backend/queen-ai
python3 << EOF
from app.core.code_proposal_system import CodeProposalSystem

system = CodeProposalSystem()
proposals = system.proposals
print(f"✅ Found {len(proposals)} proposals")

# Find your failed proposal
for pid, p in proposals.items():
    if p['status'] == 'tests_failed':
        print(f"Found failed proposal: {p['title']}")
        print(f"  ID: {pid}")
        print(f"  Test results: {p.get('test_results')}")
EOF
```

**Test 2: Auto-Fixer Works**
```bash
python3 << EOF
from app.core.proposal_auto_fixer import ProposalAutoFixer

fixer = ProposalAutoFixer(max_attempts=3)
print(f"✅ Auto-fixer initialized")
print(f"  Max attempts: {fixer.max_attempts}")
EOF
```

**Test 3: Claude Provider Works**
```bash
python3 << EOF
import asyncio
from app.llm.providers.anthropic import AnthropicProvider
from app.config.settings import settings

async def test():
    if not settings.ANTHROPIC_API_KEY:
        print("❌ ANTHROPIC_API_KEY not set!")
        return
    
    provider = AnthropicProvider()
    await provider.initialize()
    print("✅ Claude provider initialized")
    
    response = await provider.generate("Test", max_tokens=10)
    print(f"✅ Claude response: {response[:50]}")

asyncio.run(test())
EOF
```

---

## 🚨 **IF STILL FAILING**

### **Option 1: Manual Fix (Temporary)**
1. Look at the test failure error messages
2. Manually edit the proposal files
3. Re-deploy to sandbox
4. Test again

### **Option 2: Check Proposal Status**
```python
# In Python console:
from app.core.code_proposal_system import CodeProposalSystem

system = CodeProposalSystem()
proposal = system.proposals.get('YOUR_PROPOSAL_ID')

print(f"Status: {proposal['status']}")
print(f"Needs auto-fix: {proposal.get('needs_auto_fix')}")
print(f"Test results: {proposal.get('test_results')}")
```

### **Option 3: Skip Auto-Fix**
If auto-fix isn't working, you can:
1. Manually fix the code in the proposal
2. Re-deploy to sandbox
3. The system will still work, just without automation

---

## 📝 **REPORT BACK**

If still failing after these steps, please provide:

1. **Backend terminal output** (last 50 lines)
2. **Browser console errors** (F12 → Console tab)
3. **Network tab response** (F12 → Network → auto-fix request → Response)
4. **Proposal ID** that's failing
5. **Proposal status** from the UI

This will help diagnose the exact issue!

---

## 🎯 **EXPECTED WORKING STATE**

When everything works correctly:

1. **Backend starts**: No import errors
2. **Endpoint exists**: Visible in /docs
3. **Button clicks**: Shows loading
4. **Claude analyzes**: Returns fix
5. **Alert shows**: "✅ Auto-fix applied!"
6. **Proposal updates**: Code changes visible
7. **Re-test passes**: Status → tests_passed

**Let's get it working! 🚀**
