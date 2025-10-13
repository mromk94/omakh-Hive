# 🚀 **QUEEN AUTONOMOUS SYSTEM - QUICK SETUP**

## ⚡ **INSTALLATION** (5 minutes)

### **Step 1: Install Dependencies**
```bash
cd backend/queen-ai
pip install anthropic
```

### **Step 2: Get Claude API Key**
1. Go to: https://console.anthropic.com/
2. Create account or login
3. Generate API key
4. Copy the key (starts with `sk-ant-`)

### **Step 3: Add to Environment**
```bash
# Edit backend/queen-ai/.env
echo "ANTHROPIC_API_KEY=sk-ant-your-actual-key-here" >> .env
echo "PROJECT_ROOT=/Users/mac/CascadeProjects/omakh-Hive" >> .env
```

### **Step 4: Create Directories**
```bash
cd /Users/mac/CascadeProjects/omakh-Hive
mkdir -p proposals sandbox backups
```

### **Step 5: Start Backend**
```bash
cd backend/queen-ai
uvicorn main:app --reload --port 8001
```

---

## 🧪 **TESTING** (Quick Validation)

### **Test 1: Chat with Queen**
```bash
# Replace YOUR_ADMIN_TOKEN with actual token
curl -X POST http://localhost:8001/api/v1/queen-dev/chat \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello Queen, introduce yourself and your capabilities",
    "include_system_info": true
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "response": "I am the Queen AI of the OMK Hive, powered by Claude...",
  "code_proposal_created": false,
  "proposal_id": null,
  "tokens_used": {
    "input": 150,
    "output": 250
  }
}
```

### **Test 2: Ask Queen to Analyze System**
```bash
curl -X POST http://localhost:8001/api/v1/queen-dev/analyze-system \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Expected: Queen analyzes system and may propose improvements**

### **Test 3: List Proposals**
```bash
curl http://localhost:8001/api/v1/queen-dev/proposals \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## 📋 **FIRST USE WORKFLOW**

### **Scenario: Ask Queen to Fix Something**

**Step 1: Start Conversation**
```bash
curl -X POST http://localhost:8001/api/v1/queen-dev/chat \
  -H "Authorization: Bearer admin_token" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Queen, I noticed the analytics dashboard is slow. Can you investigate and propose a fix?",
    "include_system_info": true
  }'
```

**Queen's Response:**
```
"I've analyzed the analytics code. The slow performance is due to:
1. Unoptimized database queries (N+1 problem)
2. Missing caching layer
3. Redundant calculations

I can propose a fix that will:
- Add query batching
- Implement Redis caching
- Optimize calculations

This should reduce load time by 70%. Would you like me to create a code proposal?"
```

**Step 2: Request Proposal**
```bash
curl -X POST http://localhost:8001/api/v1/queen-dev/chat \
  -H "Authorization: Bearer admin_token" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Yes, please create a detailed code proposal for this optimization"
  }'
```

**Queen Creates Proposal** (automatically detected and saved)

**Step 3: Review Proposal**
```bash
# Get proposal ID from previous response
PROPOSAL_ID="abc-123-def"

curl http://localhost:8001/api/v1/queen-dev/proposals/$PROPOSAL_ID \
  -H "Authorization: Bearer admin_token"
```

**Step 4: Deploy to Sandbox**
```bash
curl -X POST http://localhost:8001/api/v1/queen-dev/proposals/$PROPOSAL_ID/deploy-sandbox \
  -H "Authorization: Bearer admin_token"
```

**Response:**
```json
{
  "success": true,
  "sandbox_path": "/path/to/sandbox/abc-123-def",
  "files_applied": [
    "backend/queen-ai/app/api/v1/admin.py",
    "backend/queen-ai/app/core/cache.py"
  ]
}
```

**Step 5: Run Tests**
```bash
curl -X POST http://localhost:8001/api/v1/queen-dev/proposals/$PROPOSAL_ID/run-tests \
  -H "Authorization: Bearer admin_token"
```

**Response:**
```json
{
  "success": true,
  "test_results": {
    "tests": [
      {"name": "Python Linting", "status": "passed"},
      {"name": "Syntax Check", "status": "passed"},
      {"name": "Unit Tests", "status": "passed"}
    ],
    "overall_status": "passed"
  }
}
```

**Step 6: Approve**
```bash
curl -X POST http://localhost:8001/api/v1/queen-dev/proposals/$PROPOSAL_ID/approve \
  -H "Authorization: Bearer admin_token" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Tests passed, looks good. Deploying to production."
  }'
```

**Step 7: Apply to Production**
```bash
curl -X POST http://localhost:8001/api/v1/queen-dev/proposals/$PROPOSAL_ID/apply \
  -H "Authorization: Bearer admin_token"
```

**Response:**
```json
{
  "success": true,
  "backup_id": "backup_20251011_023000_abc123",
  "files_applied": [
    "/path/to/prod/backend/queen-ai/app/api/v1/admin.py",
    "/path/to/prod/backend/queen-ai/app/core/cache.py"
  ],
  "message": "Changes applied to production successfully"
}
```

**Step 8: Monitor (or Rollback if needed)**
```bash
# If something goes wrong:
curl -X POST http://localhost:8001/api/v1/queen-dev/proposals/$PROPOSAL_ID/rollback \
  -H "Authorization: Bearer admin_token"
```

---

## 🎯 **COMMON USE CASES**

### **1. Bug Fix Request**
```
"Queen, there's a bug in the OTC approval flow where rejected requests 
still show as pending. Can you find and fix it?"
```

### **2. Performance Optimization**
```
"Queen, analyze the bee communication patterns and suggest optimizations 
to reduce latency"
```

### **3. Security Review**
```
"Queen, review the authentication system and identify any security 
vulnerabilities"
```

### **4. Feature Enhancement**
```
"Queen, add pagination to the user list endpoint with proper error handling"
```

### **5. Code Quality Improvement**
```
"Queen, refactor the OTC management code to follow better design patterns"
```

---

## 🔧 **TROUBLESHOOTING**

### **Issue: "ANTHROPIC_API_KEY not found"**
**Solution:**
```bash
# Check .env file exists and has key
cat backend/queen-ai/.env | grep ANTHROPIC_API_KEY

# If not, add it:
echo "ANTHROPIC_API_KEY=sk-ant-your-key" >> backend/queen-ai/.env
```

### **Issue: "Proposal not found"**
**Solution:**
```bash
# Check proposals directory exists
ls -la proposals/

# If not, create it:
mkdir -p proposals sandbox backups
```

### **Issue: "Sandbox deployment failed"**
**Solution:**
```bash
# Ensure PROJECT_ROOT is set correctly
echo $PROJECT_ROOT

# Set it if not:
export PROJECT_ROOT="/Users/mac/CascadeProjects/omakh-Hive"
```

### **Issue: "Tests failed"**
**Solution:**
```bash
# Check Python environment
python --version  # Should be 3.8+

# Install test dependencies
pip install pylint pytest
```

---

## 📊 **MONITORING**

### **Check Queen's Activity**
```bash
# Get statistics
curl http://localhost:8001/api/v1/queen-dev/stats \
  -H "Authorization: Bearer admin_token"
```

### **View Conversation History**
```bash
curl http://localhost:8001/api/v1/queen-dev/conversation-history \
  -H "Authorization: Bearer admin_token"
```

### **List All Proposals**
```bash
# All proposals
curl http://localhost:8001/api/v1/queen-dev/proposals \
  -H "Authorization: Bearer admin_token"

# Only pending
curl "http://localhost:8001/api/v1/queen-dev/proposals?status=proposed" \
  -H "Authorization: Bearer admin_token"

# Only approved
curl "http://localhost:8001/api/v1/queen-dev/proposals?status=approved" \
  -H "Authorization: Bearer admin_token"
```

---

## ⚡ **QUICK REFERENCE**

### **API Endpoints**
```
POST   /api/v1/queen-dev/chat                     - Chat with Queen
POST   /api/v1/queen-dev/analyze-system           - System analysis
GET    /api/v1/queen-dev/conversation-history     - History
GET    /api/v1/queen-dev/proposals                - List proposals
GET    /api/v1/queen-dev/proposals/{id}           - Details
POST   /api/v1/queen-dev/proposals/{id}/deploy-sandbox   - Deploy
POST   /api/v1/queen-dev/proposals/{id}/run-tests        - Test
POST   /api/v1/queen-dev/proposals/{id}/approve          - Approve
POST   /api/v1/queen-dev/proposals/{id}/apply            - Apply
POST   /api/v1/queen-dev/proposals/{id}/rollback         - Rollback
```

### **File Locations**
```
/backend/queen-ai/app/integrations/claude_integration.py  - Claude API
/backend/queen-ai/app/core/code_proposal_system.py       - Proposals
/backend/queen-ai/app/api/v1/queen_dev.py                - API
/proposals/                                               - Proposals
/sandbox/                                                 - Testing
/backups/                                                 - Backups
```

---

## 🎉 **YOU'RE READY!**

**The Queen Autonomous Development System is now operational!**

Start by chatting with Queen and asking her to analyze the system. She'll identify improvements and propose code changes that you can safely test and deploy.

**Welcome to the future of AI-driven development!** 🚀👑🐝
