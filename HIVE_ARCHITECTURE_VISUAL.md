# 🐝 **HIVE ARCHITECTURE - VISUAL GUIDE**

**Date:** October 11, 2025  
**Purpose:** Visual representation of complete Hive infrastructure

---

## 🏗️ **COMPLETE SYSTEM ARCHITECTURE**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OMK HIVE ECOSYSTEM                                  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    LAYER 1: USER INTERFACES                          │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │                                                                      │  │
│  │   ┌─────────────────┐              ┌─────────────────┐            │  │
│  │   │  User Portal    │              │ Admin Portal    │            │  │
│  │   │   /chat         │              │   /kingdom      │            │  │
│  │   │                 │              │                 │            │  │
│  │   │ • Chat with AI  │              │ • Hive Monitor  │            │  │
│  │   │ • Buy OMK       │              │ • Bee Control   │            │  │
│  │   │ • Properties    │              │ • OTC Approve   │            │  │
│  │   │ • Dashboard     │              │ • Analytics     │            │  │
│  │   │ • Wallet        │              │ • Contracts     │            │  │
│  │   └────────┬────────┘              └────────┬────────┘            │  │
│  │            │                                │                     │  │
│  └────────────┼────────────────────────────────┼─────────────────────┘  │
│               │                                │                         │
│               │                                │                         │
│  ┌────────────┼────────────────────────────────┼─────────────────────┐  │
│  │            │       LAYER 2: API LAYER       │                     │  │
│  ├────────────┼────────────────────────────────┼─────────────────────┤  │
│  │            ▼                                ▼                     │  │
│  │   ┌─────────────────┐              ┌─────────────────┐          │  │
│  │   │  Frontend API   │              │   Admin API     │          │  │
│  │   │                 │              │                 │          │  │
│  │   │ POST /chat      │              │ GET /hive/*     │          │  │
│  │   │ POST /otc-req   │              │ POST /queen/*   │          │  │
│  │   │ GET /balance    │              │ PUT /config     │          │  │
│  │   └────────┬────────┘              └────────┬────────┘          │  │
│  │            │                                │                     │  │
│  └────────────┼────────────────────────────────┼─────────────────────┘  │
│               │                                │                         │
│               └────────────┬───────────────────┘                         │
│                            │                                             │
│  ┌────────────────────────┼──────────────────────────────────────────┐  │
│  │                        │   LAYER 3: QUEEN AI ORCHESTRATION        │  │
│  ├────────────────────────┼──────────────────────────────────────────┤  │
│  │                        ▼                                          │  │
│  │              ┌──────────────────────┐                            │  │
│  │              │  QUEEN ORCHESTRATOR  │                            │  │
│  │              │                      │                            │  │
│  │              │  • Task Routing      │                            │  │
│  │              │  • Bee Coordination  │                            │  │
│  │              │  • Decision Making   │                            │  │
│  │              │  • Security Control  │                            │  │
│  │              │  • Emergency Pause   │                            │  │
│  │              └──────────┬───────────┘                            │  │
│  │                         │                                        │  │
│  │         ┌───────────────┼───────────────┐                        │  │
│  │         │               │               │                        │  │
│  │         ▼               ▼               ▼                        │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐               │  │
│  │  │  Decision  │  │    LLM     │  │  Security  │               │  │
│  │  │   Engine   │  │ Abstraction│  │   Layer    │               │  │
│  │  │            │  │            │  │            │               │  │
│  │  │ • Rules    │  │ • GPT-4    │  │ • Auth     │               │  │
│  │  │ • Policy   │  │ • Claude   │  │ • Roles    │               │  │
│  │  │ • Logic    │  │ • Gemini   │  │ • Limits   │               │  │
│  │  └────────────┘  └────────────┘  └────────────┘               │  │
│  │                                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                 │                                       │
│  ┌──────────────────────────────┼─────────────────────────────────────┐│
│  │                   LAYER 4: COMMUNICATION INFRASTRUCTURE          ││
│  ├──────────────────────────────┼─────────────────────────────────────┤│
│  │                              ▼                                   ││
│  │     ┌──────────────────────────────────────────────┐            ││
│  │     │         MESSAGE BUS (Redis Pub/Sub)          │            ││
│  │     │  • Bee-to-bee messaging                      │            ││
│  │     │  • Priority queuing                          │            ││
│  │     │  • Request-response                          │            ││
│  │     │  • Broadcast                                 │            ││
│  │     └──────────────────────────────────────────────┘            ││
│  │                                                                  ││
│  │     ┌──────────────────────────────────────────────┐            ││
│  │     │      HIVE INFORMATION BOARD (Redis)          │            ││
│  │     │  • Shared knowledge                          │            ││
│  │     │  • Category-based posts                      │            ││
│  │     │  • Tag-based search                          │            ││
│  │     │  • Subscriptions                             │            ││
│  │     └──────────────────────────────────────────────┘            ││
│  │                                                                  ││
│  │     ┌──────────────────────────────────────────────┐            ││
│  │     │        ACTIVITY TRACKER (Elastic)            │  ❌ MISSING││
│  │     │  • Real-time activity logging                │            ││
│  │     │  • Performance metrics                       │            ││
│  │     │  • Historical analysis                       │            ││
│  │     └──────────────────────────────────────────────┘            ││
│  │                                                                  ││
│  └──────────────────────────────────────────────────────────────────┘│
│                                 │                                      │
│  ┌──────────────────────────────┼─────────────────────────────────────┐│
│  │                   LAYER 5: BEE EXECUTION (19 BEES)               ││
│  ├──────────────────────────────┼─────────────────────────────────────┤│
│  │                              ▼                                   ││
│  │                                                                  ││
│  │   Core Analysis Bees:                                           ││
│  │   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐            ││
│  │   │  Maths  │ │Security │ │  Data   │ │Treasury │            ││
│  │   │   Bee   │ │   Bee   │ │  Bee    │ │  Bee    │            ││
│  │   └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘            ││
│  │        │           │           │           │                   ││
│  │        └───────────┴───────────┴───────────┘                   ││
│  │                         │                                       ││
│  │   Execution & Logic Bees:                                      ││
│  │   ┌─────────┐ ┌─────────┐ ┌─────────┐                        ││
│  │   │Blockchain│ │ Logic  │ │Pattern  │                        ││
│  │   │   Bee   │ │  Bee    │ │  Bee    │                        ││
│  │   └────┬────┘ └────┬────┘ └────┬────┘                        ││
│  │        │           │           │                               ││
│  │        └───────────┴───────────┘                               ││
│  │                         │                                       ││
│  │   Specialized Operation Bees:                                  ││
│  │   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           ││
│  │   │Purchase │ │Liquidity│ │StakeBot │ │Tokenize │           ││
│  │   │   Bee   │ │Sentinel │ │   Bee   │ │   Bee   │           ││
│  │   └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘           ││
│  │        │           │           │           │                   ││
│  │        └───────────┴───────────┴───────────┘                   ││
│  │                         │                                       ││
│  │   Advanced System Bees:                                        ││
│  │   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           ││
│  │   │Monitor  │ │ Private │ │Governance│ │Visualize│           ││
│  │   │   Bee   │ │Sale Bee │ │   Bee   │ │   Bee   │           ││
│  │   └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘           ││
│  │        │           │           │           │                   ││
│  │        └───────────┴───────────┴───────────┘                   ││
│  │                         │                                       ││
│  │   Integration Bees:                                            ││
│  │   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           ││
│  │   │ Bridge  │ │  Data   │ │Onboarding│ │User Exp │           ││
│  │   │   Bee   │ │Pipeline │ │   Bee   │ │   Bee   │           ││
│  │   └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘           ││
│  │        │           │           │           │                   ││
│  │        └───────────┴───────────┴───────────┘                   ││
│  │                         │                                       ││
│  └─────────────────────────┼───────────────────────────────────────┘│
│                            │                                        │
│  ┌─────────────────────────┼─────────────────────────────────────┐ │
│  │              LAYER 6: DATA STORAGE                            │ │
│  ├─────────────────────────┼─────────────────────────────────────┤ │
│  │                         ▼                                     │ │
│  │                                                               │ │
│  │   ┌──────────────────────────────────────────┐              │ │
│  │   │    PostgreSQL / JSON Storage             │              │ │
│  │   │  • Users                                 │              │ │
│  │   │  • OTC Requests                          │              │ │
│  │   │  • System Config                         │              │ │
│  │   │  • Analytics                             │              │ │
│  │   └──────────────────────────────────────────┘              │ │
│  │                                                               │ │
│  │   ┌──────────────────────────────────────────┐              │ │
│  │   │          Redis Cache                     │              │ │
│  │   │  • Sessions                              │              │ │
│  │   │  • Real-time metrics                     │              │ │
│  │   │  • Message bus                           │              │ │
│  │   │  • Hive board                            │              │ │
│  │   └──────────────────────────────────────────┘              │ │
│  │                                                               │ │
│  │   ┌──────────────────────────────────────────┐              │ │
│  │   │       Elastic Search                     │              │ │
│  │   │  • Activity logs                         │              │ │
│  │   │  • Search & RAG                          │              │ │
│  │   │  • Error tracking                        │              │ │
│  │   └──────────────────────────────────────────┘              │ │
│  │                                                               │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 **COMPLETE REQUEST FLOW**

### **User Request Example: "Buy OMK"**

```
1. USER INITIATES:
   User types: "I want to buy OMK" in chat
   ↓

2. FRONTEND:
   POST /api/v1/frontend/chat
   {
     "user_input": "I want to buy OMK",
     "wallet_address": "0x...",
     "context": {}
   }
   ↓

3. API LAYER:
   frontend.py receives request
   ↓

4. QUEEN ORCHESTRATOR:
   • Receives request
   • Analyzes intent → "buy_omk"
   • Checks system config → OTC phase
   ↓

5. SYSTEM CONFIG:
   get_active_otc_flow() returns "private_sale"
   ↓

6. QUEEN DECIDES:
   • Phase = private_sale
   • Return OTCPurchaseCard
   ↓

7. RESPONSE TO FRONTEND:
   {
     "success": true,
     "message": "We're in Private Sale phase...",
     "options": [{"type": "otc_purchase"}],
     "otc_flow": "private_sale"
   }
   ↓

8. FRONTEND RENDERS:
   Shows OTCPurchaseCard inline in chat
   ↓

9. USER FILLS FORM:
   • Name: "John Doe"
   • Email: "john@example.com"
   • Wallet: "0x..."
   • Amount: $50,000 (500,000 OMK)
   ↓

10. USER SUBMITS:
    POST /api/v1/frontend/otc-request
    {
      "name": "John Doe",
      "email": "john@example.com",
      "wallet": "0x...",
      "allocation": "500000",
      "price_per_token": 0.10
    }
    ↓

11. BACKEND PROCESSING:
    • Validates data
    • Calculates amount_usd = 500000 * 0.10 = $50,000
    • Generates ID: "OTC-001"
    • Saves to database
    ↓

12. DATABASE:
    otc_requests.json += {
      "id": "OTC-001",
      "name": "John Doe",
      "email": "john@example.com",
      "wallet": "0x...",
      "allocation": "500000",
      "amount_usd": "50000",
      "status": "pending",
      "created_at": "2025-10-11T01:00:00Z"
    }
    ↓

13. ANALYTICS LOGGING:
    analytics.json transactions += {
      "type": "otc_request_submitted",
      "request_id": "OTC-001",
      "amount_usd": 50000,
      "timestamp": "..."
    }
    ↓

14. RESPONSE TO USER:
    {
      "success": true,
      "message": "Request submitted!",
      "request_id": "OTC-001"
    }
    ↓

15. FRONTEND CONFIRMATION:
    Shows success message:
    "✅ OTC request submitted! Request ID: OTC-001"
```

---

### **Admin Approval Flow:**

```
1. ADMIN OPENS KINGDOM:
   http://localhost:3001/kingdom
   ↓

2. GOES TO OTC MANAGEMENT TAB:
   Clicks "OTC Management"
   ↓

3. FRONTEND LOADS REQUESTS:
   GET /api/v1/admin/otc/requests
   ↓

4. BACKEND READS DATABASE:
   otc_requests.json → All requests
   ↓

5. RETURNS TO FRONTEND:
   {
     "success": true,
     "requests": [
       {
         "id": "OTC-001",
         "name": "John Doe",
         "status": "pending",
         ...
       }
     ]
   }
   ↓

6. ADMIN SEES REQUEST:
   List shows "John Doe - $50,000 - Pending"
   ↓

7. ADMIN CLICKS REQUEST:
   Modal opens with full details
   ↓

8. ADMIN CLICKS "APPROVE":
   POST /api/v1/admin/otc/requests/OTC-001/approve
   ↓

9. BACKEND UPDATES:
   otc_requests.json:
   {
     "id": "OTC-001",
     "status": "approved", // ← CHANGED
     "approved_by": "admin",
     "approved_at": "2025-10-11T01:05:00Z"
   }
   ↓

10. LOGS TRANSACTION:
    analytics.json += {
      "type": "otc_approved",
      "request_id": "OTC-001",
      "amount_usd": 50000
    }
    ↓

11. UPDATES ANALYTICS:
    analytics.total_revenue_usd += 50000
    analytics.total_omk_distributed += 500000
    ↓

12. RESPONSE TO ADMIN:
    {
      "success": true,
      "message": "Request approved!",
      "request": {...}
    }
    ↓

13. ADMIN SEES CONFIRMATION:
    "✅ OTC request OTC-001 approved"
    ↓

14. (TODO) EMAIL SENT TO USER:
    "Your OTC request has been approved!"
```

---

## 🐝 **BEE COORDINATION EXAMPLE**

### **Liquidity Check Workflow:**

```
SCENARIO: Queen needs to check liquidity health

1. QUEEN DECISION:
   "Need liquidity assessment"
   ↓

2. QUEEN ROUTES TO LIQUIDITY SENTINEL:
   await bee_manager.execute_bee("liquidity_sentinel", {
     "type": "check_pool_health",
     "pool": "OMK/ETH"
   })
   ↓

3. LIQUIDITY SENTINEL BEE ACTIVATES:
   • Logs activity start to Elastic (❌ NOT IMPLEMENTED)
   • Posts to Hive Board: "Checking OMK/ETH pool"
   ↓

4. LIQUIDITY SENTINEL NEEDS DATA:
   Sends message via Message Bus:
   → DataBee: "Get current pool stats"
   ↓

5. DATA BEE RESPONDS:
   • Queries blockchain
   • Returns: {
       "reserve_omk": "1000000",
       "reserve_eth": "500",
       "price": "0.0005 ETH per OMK"
     }
   ↓

6. LIQUIDITY SENTINEL CALCULATES:
   Needs MathsBee for calculations
   → MathsBee: "Calculate pool ratio"
   ↓

7. MATHS BEE CALCULATES:
   • Ratio = 1000000 / 500 = 2000
   • Expected ratio = 2000
   • Deviation = 0%
   • Returns: "Pool balanced"
   ↓

8. LIQUIDITY SENTINEL CHECKS PATTERN:
   → PatternBee: "Analyze price trend"
   ↓

9. PATTERN BEE ANALYZES:
   • Fetches historical data
   • Runs ML model
   • Returns: "Stable trend, low volatility"
   ↓

10. LIQUIDITY SENTINEL CONSULTS SECURITY:
    → SecurityBee: "Any risks?"
    ↓

11. SECURITY BEE VALIDATES:
    • Checks for anomalies
    • Returns: "No risks detected"
    ↓

12. LIQUIDITY SENTINEL COMPILES REPORT:
    {
      "status": "healthy",
      "ratio": 2000,
      "deviation": 0,
      "trend": "stable",
      "recommendation": "no_action_needed"
    }
    ↓

13. POSTS TO HIVE BOARD:
    category: "pool_health"
    title: "OMK/ETH pool is healthy"
    content: {...report...}
    ↓

14. RETURNS TO QUEEN:
    Queen receives full report
    ↓

15. QUEEN LOGS DECISION:
    "Liquidity check complete - no action needed"
    ↓

16. ACTIVITY COMPLETED:
    All bee activities logged to Elastic (❌ NOT IMPLEMENTED)
```

---

## 📊 **WHAT'S MISSING (Visual)**

```
┌────────────────────────────────────────┐
│    IMPLEMENTED ✅                      │
├────────────────────────────────────────┤
│                                        │
│  • 19 Bees (all coded)                 │
│  • Queen Orchestrator                  │
│  • Message Bus                         │
│  • Hive Board                          │
│  • Admin API                           │
│  • Frontend API                        │
│  • Database Layer                      │
│                                        │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│    MISSING ❌                          │
├────────────────────────────────────────┤
│                                        │
│  • Activity Tracker                    │
│  • Task Queue System                   │
│  • Performance Metrics                 │
│  • Admin Wallet Integration            │
│  • Live Hive Dashboard Data            │
│  • Bee Control Panel                   │
│  • Queen Command Center                │
│                                        │
└────────────────────────────────────────┘
```

---

## ✅ **COMPLETE SYSTEM (After TODO)**

```
┌─────────────────────────────────────────────────────────────┐
│             FULLY FUNCTIONAL HIVE SYSTEM                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  USER LAYER:                                                │
│    ✅ Chat interface                                        │
│    ✅ Wallet connection                                     │
│    ✅ Real-time responses                                   │
│                                                             │
│  ADMIN LAYER:                                               │
│    ✅ Kingdom portal                                        │
│    ✅ Wallet integration (NEW)                              │
│    ✅ Live hive monitoring (NEW)                            │
│    ✅ Bee control panel (NEW)                               │
│    ✅ Performance dashboards (NEW)                          │
│                                                             │
│  QUEEN LAYER:                                               │
│    ✅ Task orchestration                                    │
│    ✅ Decision making                                       │
│    ✅ Emergency controls                                    │
│    ✅ Activity logging (NEW)                                │
│                                                             │
│  BEE LAYER:                                                 │
│    ✅ 19 specialized bees                                   │
│    ✅ Communication infrastructure                          │
│    ✅ Performance tracking (NEW)                            │
│    ✅ Task queue management (NEW)                           │
│                                                             │
│  DATA LAYER:                                                │
│    ✅ Database (PostgreSQL/JSON)                            │
│    ✅ Cache (Redis)                                         │
│    ✅ Search (Elastic)                                      │
│    ✅ Real-time metrics (NEW)                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

**SUMMARY:** The Hive infrastructure is 70% complete. The core (bees, Queen, communication) exists and works. What's missing is the **operational visibility layer** - the ability to see, monitor, and control what's happening in real-time. This is critical for admin confidence and system optimization.
