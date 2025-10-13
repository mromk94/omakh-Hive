# 👑 Queen AI & Her Hive - Complete Structure

**Date:** October 11, 2025  
**Purpose:** Comprehensive guide to Queen AI architecture and Elasticsearch implementation

---

## 🏗️ **QUEEN AI ARCHITECTURE**

### **1. Main Entry Point**
**File:** `backend/queen-ai/main.py`

```python
# Application flow:
1. FastAPI app created with lifespan context
2. QueenOrchestrator initialized on startup
3. Queen stored in app.state.queen
4. All API routers registered under /api/v1
5. Health check at /health
```

**Key Components:**
- **QueenOrchestrator** - Central AI brain
- **API Routers** - All endpoints
- **CORS** - Frontend communication
- **Lifespan** - Startup/shutdown management

---

### **2. Queen Orchestrator**
**File:** `app/core/orchestrator.py`

**Responsibilities:**
- Initialize all bees
- Coordinate bee activities
- Handle LLM integrations (Claude, Gemini)
- Manage system health
- Execute complex workflows

**Integration Points:**
- BeeManager (manages all worker bees)
- LLM providers (Claude, Gemini)
- Elasticsearch (activity logging)
- Blockchain bees
- Market Data Agent (new!)

---

### **3. Queen System Manager**
**File:** `app/core/queen_system_manager.py`

**Purpose:** Autonomous development with safety constraints

**Features:**
- ✅ System indexing (knows entire codebase)
- ✅ Protected files (cannot modify admin/contracts)
- ✅ Safe web surfing (whitelisted domains only)
- ✅ Sandbox testing before production
- ✅ Command execution validation
- ✅ File modification permissions
- ✅ Audit logging of all actions

**Protected Files:**
- Admin powers: `app/api/v1/admin.py`
- Smart contracts: `contracts/*.sol`
- Environment: `.env`
- Core settings: `app/config/settings.py`

**Safe Domains:**
- api.github.com
- api.coingecko.com
- api.etherscan.io
- pypi.org, npmjs.org

**Blocked Commands:**
- `rm -rf`, `sudo`, `chmod 777`
- `dd if=`, `mkfs`
- Fork bombs, arbitrary scripts

---

### **4. The Hive (Bee System)**
**Directory:** `app/bees/`

**Bee Manager:** `app/bees/manager.py`
- Spawns and coordinates all bees
- Assigns tasks
- Monitors performance
- Handles bee lifecycle

**Current Bees (23 total):**

| Bee | File | Purpose |
|-----|------|---------|
| **MathsBee** | `maths_bee.py` | Pool calculations, APY, price averaging |
| **TreasuryBee** | `treasury_bee.py` | Budget tracking, spending proposals |
| **PrivateSaleBee** | `private_sale_bee.py` | OTC sales, tiered pricing |
| **BlockchainBee** | `blockchain_bee.py` | On-chain interactions |
| **LiquiditySentinelBee** | `liquidity_sentinel_bee.py` | Price monitoring, rebalancing |
| **DataPipelineBee** | `data_pipeline_bee.py` | Data ETL operations |
| **MonitoringBee** | `monitoring_bee.py` | System health checks |
| **OnboardingBee** | `onboarding_bee.py` | User registration flows |
| **BridgeBee** | `bridge_bee.py` | Cross-chain operations |
| **GovernanceBee** | `governance_bee.py` | DAO proposals |
| **StakeBotBee** | `stake_bot_bee.py` | Staking operations |
| **TokenizationBee** | `tokenization_bee.py` | Asset tokenization |
| **PurchaseBee** | `purchase_bee.py` | Purchase processing |
| **LogicBee** | `logic_bee.py` | Business logic |
| **PatternBee** | `pattern_bee.py` | Pattern recognition |
| **SecurityBee** | `security_bee.py` | Security validation |
| **EnhancedSecurityBee** | `enhanced_security_bee.py` | Advanced security |
| **DataBee** | `data_bee.py` | Data operations |
| **UserExperienceBee** | `user_experience_bee.py` | UX optimization |
| **VisualizationBee** | `visualization_bee.py` | Data visualization |

**NEW (Just Added):**
| Bee/Agent | File | Purpose |
|-----------|------|---------|
| **MarketDataAgent** | `app/agents/market_data_agent.py` | Real-time crypto market data |

---

### **5. API Structure**
**Directory:** `app/api/v1/`

**Router Registry:** `app/api/v1/__init__.py`

**Endpoints:**
- `/api/v1/frontend` - Frontend operations (chat, OTC, dashboard)
- `/api/v1/admin` - Admin configuration
- `/api/v1/queen` - Queen direct interaction
- `/api/v1/queen_dev` - Development/debug endpoints
- **NEW:** `/api/v1/market` - Market data

---

## 🔍 **ELASTICSEARCH IMPLEMENTATION**

### **Purpose: AI-Powered Search & Knowledge Management**

**File:** `app/integrations/elastic_search.py`

### **What Elasticsearch Does:**

#### **1. Bee Activity Logging**
Every bee action is logged to Elasticsearch:
```python
await elastic.log_bee_activity(
    bee_name="MathsBee",
    action="calculate_weighted_average_price",
    data={"requests": [...], "result": 0.1225},
    success=True,
    tags=["otc", "price", "calculation"]
)
```

**Benefits:**
- Track all system operations
- Debug bee behavior
- Audit trail
- Performance analytics

#### **2. Knowledge Base**
Stores system knowledge for RAG:
```python
await elastic.store_knowledge(
    title="OMK Tokenomics",
    content="Total supply: 1B, Initial price: $0.10...",
    category="tokenomics",
    tags=["omk", "token", "supply"]
)
```

**Benefits:**
- Queen can search internal docs
- Contextual answers
- Knowledge discovery

#### **3. Transaction Logging**
Records all blockchain transactions:
```python
await elastic.log_transaction(
    tx_hash="0x123...",
    type="token_purchase",
    amount=100000,
    status="confirmed"
)
```

**Benefits:**
- Transaction history
- Fraud detection
- Analytics

#### **4. Hybrid Search**
Combines keyword + semantic search:
```python
results = await elastic.hybrid_search(
    query="How do I calculate OTC price?",
    indices=["knowledge_base", "bee_activities"],
    size=10
)
```

**Benefits:**
- Natural language queries
- Semantic understanding
- Contextual results

#### **5. RAG (Retrieval Augmented Generation)**
Powers conversational AI:
```python
answer = await elastic.rag_query(
    query="What's the weighted average OTC price?",
    gemini_client=gemini
)
```

**Flow:**
1. Search Elasticsearch for relevant context
2. Pass context to Gemini/Claude
3. Generate informed answer
4. Return to user

**Benefits:**
- Accurate, context-aware answers
- Reduces hallucinations
- Uses real system data

---

### **Elasticsearch Indices**

#### **1. `bee_activities_index`**
```json
{
  "bee_name": "MathsBee",
  "action": "calculate_weighted_average_price",
  "timestamp": "2025-10-11T20:30:00Z",
  "data": {"requests": 15, "average_price": 0.1225},
  "success": true,
  "response_time": 0.05,
  "tags": ["otc", "price"]
}
```

#### **2. `knowledge_base_index`**
```json
{
  "title": "OTC Pricing Model",
  "content": "OMK OTC uses tiered pricing...",
  "category": "tokenomics",
  "tags": ["otc", "pricing", "tiers"],
  "created_at": "2025-10-11T20:00:00Z",
  "embedding": [0.123, 0.456, ...] // 768-dim vector
}
```

#### **3. `transactions_index`**
```json
{
  "tx_hash": "0x123abc...",
  "type": "token_purchase",
  "from": "0xUser...",
  "to": "0xContract...",
  "amount": 100000,
  "status": "confirmed",
  "timestamp": "2025-10-11T20:15:00Z"
}
```

---

### **Setup Elasticsearch**

**1. Get Credentials:**
- Go to: https://cloud.elastic.co/
- Create deployment (Free tier available)
- Get Cloud ID and API Key

**2. Configure `.env`:**
```bash
ELASTIC_CLOUD_ID=your_cloud_id_here
ELASTIC_API_KEY=your_api_key_here
```

**3. Initialize:**
```bash
cd backend/queen-ai
python3 initialize_elastic.py
```

**4. Test Connection:**
```bash
python3 test_elastic_connection.py
```

---

## 🔗 **INTEGRATING MARKET DATA AGENT WITH QUEEN**

Now that we understand the structure, let's integrate our new agent!

### **Step 1: Register Agent in Orchestrator**

**File:** `app/core/orchestrator.py`

Add to Queen's initialization:
```python
from app.agents.market_data_agent import MarketDataAgent

class QueenOrchestrator:
    async def initialize(self):
        # ... existing initialization ...
        
        # Initialize Market Data Agent
        self.market_data_agent = MarketDataAgent(self)
        logger.info("✅ MarketDataAgent initialized")
```

### **Step 2: Register Market Router**

**File:** `app/api/v1/__init__.py`

Add market router:
```python
from app.api.v1 import admin, frontend, queen, queen_dev, market

router = APIRouter()

router.include_router(admin.router)
router.include_router(frontend.router)
router.include_router(queen.router)
router.include_router(queen_dev.router)
router.include_router(market.router)  # NEW
```

### **Step 3: Environment Variables**

**File:** `backend/queen-ai/.env`

Add API keys:
```bash
# Market Data APIs
COINGECKO_API_KEY=your_key
CRYPTOPANIC_API_KEY=your_key

# Optional (for on-chain data)
INFURA_PROJECT_ID=your_project_id
HELIUS_API_KEY=your_helius_key
```

---

## 📊 **COMPLETE DATA FLOW**

```
User Request → Frontend
       ↓
  /api/v1/market/data
       ↓
MarketDataAgent.get_comprehensive_data()
       ↓
   ┌────┴────┐
   │         │
   ▼         ▼
Crypto    OMK Data
(CoinGecko)  ↓
       ┌─────┴─────┐
       │           │
   On-Chain?    OTC Mode
       │           │
       ▼           ▼
  Blockchain   Queen's Bees
  (Infura)     ├─ TreasuryBee
               ├─ PrivateSaleBee
               └─ MathsBee
       │           │
       └─────┬─────┘
             ▼
       Combined Data
             ↓
       Log to Elastic
             ↓
      Return to Frontend
```

---

## 🎯 **SUMMARY**

### **Queen AI Structure:**
- **Queen Orchestrator** - Central brain (coordinates everything)
- **Bee Manager** - Manages 23+ specialized worker bees
- **System Manager** - Safety & autonomy with constraints
- **API Layer** - RESTful endpoints for all operations

### **Elasticsearch Purpose:**
1. **Activity Logging** - Track all bee operations
2. **Knowledge Base** - Store & search system knowledge
3. **Transaction History** - Record blockchain txs
4. **Hybrid Search** - Keyword + semantic search
5. **RAG** - Power intelligent Q&A with context

### **Integration Status:**
- ✅ Market Data Agent created
- ✅ API endpoints ready
- ✅ Bees enhanced
- ⏳ Need to register with Queen Orchestrator
- ⏳ Need to add router to API
- ⏳ Need environment variables

---

## 🚀 **NEXT: Complete Integration**

Ready to complete the integration? 

**Required changes:**
1. Update `app/core/orchestrator.py` - Add market agent
2. Update `app/api/v1/__init__.py` - Register market router
3. Add API keys to `.env`

Shall I proceed with these final steps?
