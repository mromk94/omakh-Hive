# 🎯 OMK HIVE - Critical Implementation Roadmap

**Started**: October 13, 2025, 8:12 PM  
**Approach**: Critical Issues → Missing APIs → Full Integration  
**Timeline**: 3-4 weeks (aggressive)

---

## 🔴 **PHASE 1: CRITICAL FIXES (Days 1-3)**

### **Task 1.1: Fix Backend API Connection** ✅ PRIORITY 1

**Problem**: Frontend expects `localhost:8001`, backend is deployed at Cloud Run

**Files to Update**:
- `/omk-frontend/.env.local` (create/update)
- `/omk-frontend/.env.production` (create)
- `/omk-frontend/lib/api.ts` (verify)
- Any hardcoded URLs in components

**Actions**:
```bash
# Create production environment file
NEXT_PUBLIC_QUEEN_API_URL=https://omk-queen-ai-475745165557.us-central1.run.app
NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID=<get_from_cloud_wallet_connect>
```

**Test**:
- [ ] Health check connects
- [ ] Chat API responds
- [ ] Greetings endpoint works
- [ ] Login/register flows work

---

### **Task 1.2: Hide Incomplete Features** ✅ PRIORITY 1

**Problem**: Users can access broken features (properties, staking, governance)

**Files to Update**:
- `/omk-frontend/app/chat/page.tsx` - Comment out broken flows
- `/omk-frontend/components/menu/FloatingMenu.tsx` - Hide broken menu items

**Features to Hide/Disable**:
```typescript
// In chat/page.tsx
case 'show_properties': // HIDE - No backend
case 'show_staking': // HIDE - No backend  
case 'show_governance': // HIDE - No backend
case 'show_partners': // HIDE - No backend
```

**Show Graceful Messages**:
```typescript
addMessage('ai', '🚧 This feature is coming soon! Our team is working hard to bring you real estate investing. Stay tuned! 🏠');
```

---

### **Task 1.3: Fix Dashboard Mock Data** ✅ PRIORITY 2

**Problem**: Dashboard shows fake portfolio data

**Options**:
1. **Quick Fix**: Show "Connect wallet to see portfolio" message
2. **Better Fix**: Implement basic portfolio API (read wallet balances)

**File**: `/omk-frontend/components/cards/DashboardCard.tsx`

**Approach**: Option 1 for now, Option 2 in Phase 2

---

## 🟡 **PHASE 2: BUILD MISSING BACKEND APIs (Days 4-14)**

### **Task 2.1: Properties API** 🏠 CRITICAL

**Endpoints to Build**:
```python
# backend/queen-ai/app/api/v1/properties.py

GET  /api/v1/properties                    # List all properties
GET  /api/v1/properties/{id}               # Property details
POST /api/v1/properties/{id}/invest        # Invest in property
GET  /api/v1/properties/{id}/analytics     # Property performance
POST /api/v1/admin/properties              # Create property (admin)
PUT  /api/v1/admin/properties/{id}         # Update property (admin)
```

**Data Model**:
```python
class Property(Base):
    id: str
    title: str
    description: str
    location: str
    city: str
    country: str
    property_type: str  # apartment, villa, condo
    total_value: float
    token_price: float
    total_tokens: int
    available_tokens: int
    annual_yield: float  # Expected rental yield %
    images: list[str]
    status: str  # active, funded, earning
    created_at: datetime
```

**Implementation Steps**:
- [ ] Create database models
- [ ] Create CRUD operations
- [ ] Build API endpoints
- [ ] Add Queen AI integration (property recommendations)
- [ ] Test with frontend PropertyCard

---

### **Task 2.2: Portfolio API** 💼 CRITICAL

**Endpoints to Build**:
```python
# backend/queen-ai/app/api/v1/portfolio.py

GET  /api/v1/user/portfolio                # Complete portfolio
GET  /api/v1/user/holdings/crypto          # Crypto holdings
GET  /api/v1/user/holdings/real-estate     # Property holdings
GET  /api/v1/user/transactions             # Transaction history
GET  /api/v1/user/performance              # ROI analytics
```

**Data Aggregation**:
- Read wallet balances (Ethereum/Solana)
- Query property ownership from contracts
- Calculate total portfolio value
- Track transaction history
- Compute performance metrics

**Implementation Steps**:
- [ ] Create portfolio service
- [ ] Integrate with Web3 (read blockchain)
- [ ] Build aggregation logic
- [ ] Create API endpoints
- [ ] Test with DashboardCard

---

### **Task 2.3: OTC Purchase Complete Flow** 💎 HIGH PRIORITY

**Endpoints to Build**:
```python
# backend/queen-ai/app/api/v1/otc.py (enhance existing)

POST /api/v1/otc/submit                    # Submit OTC request
GET  /api/v1/otc/status/{id}               # Check status
POST /api/v1/admin/otc/approve/{id}        # Approve request
POST /api/v1/admin/otc/reject/{id}         # Reject request
POST /api/v1/admin/otc/verify-payment/{id} # Verify crypto payment
POST /api/v1/admin/otc/execute-tge         # Execute TGE (distribute tokens)
GET  /api/v1/admin/otc/requests            # List all requests
```

**Workflow**:
1. User submits OTC request (amount, wallet)
2. Admin reviews in Kingdom portal
3. User sends crypto to specified wallet
4. Admin verifies payment on-chain
5. Admin approves → adds to distribution list
6. At TGE: Admin executes batch distribution

**Implementation Steps**:
- [ ] Enhance OTC model (add payment verification)
- [ ] Build approval/rejection flow
- [ ] Create payment verification (check blockchain)
- [ ] Build TGE execution (batch transfer)
- [ ] Add notifications (email/webhook)
- [ ] Test full flow end-to-end

---

### **Task 2.4: KYC Verification System** 🔐 HIGH PRIORITY

**Endpoints to Build**:
```python
# backend/queen-ai/app/api/v1/kyc.py

POST /api/v1/user/kyc/submit               # Upload documents
GET  /api/v1/user/kyc/status               # Check KYC status
POST /api/v1/admin/kyc/approve/{user_id}   # Approve KYC
POST /api/v1/admin/kyc/reject/{user_id}    # Reject KYC
GET  /api/v1/admin/kyc/pending             # Pending KYC list
```

**Document Storage**:
- Use Google Cloud Storage for document uploads
- Store encrypted metadata in database
- Generate unique URLs with expiry

**Implementation Steps**:
- [ ] Create KYC model
- [ ] Integrate Cloud Storage
- [ ] Build upload endpoint (multipart/form-data)
- [ ] Create admin review interface
- [ ] Add email notifications
- [ ] Test upload flow

---

### **Task 2.5: Market Data Integration** 📊 MEDIUM PRIORITY

**Endpoints to Build**:
```python
# backend/queen-ai/app/api/v1/market.py (enhance existing)

GET  /api/v1/market/prices                 # OMK + major tokens
GET  /api/v1/market/omk-stats              # OMK token stats
GET  /api/v1/market/trending               # Trending properties
GET  /api/v1/market/analytics              # Market analytics
```

**Data Sources**:
- CoinGecko API (token prices)
- On-chain data (OMK supply, holders)
- Internal analytics (property performance)

**Implementation Steps**:
- [ ] Integrate CoinGecko API
- [ ] Create caching layer (Redis)
- [ ] Build aggregation service
- [ ] Create API endpoints
- [ ] Test with MarketDataCard

---

### **Task 2.6: Governance System** 🗳️ LOW PRIORITY

**Endpoints to Build**:
```python
# backend/queen-ai/app/api/v1/governance.py

GET  /api/v1/governance/proposals          # List proposals
GET  /api/v1/governance/proposals/{id}     # Proposal details
POST /api/v1/governance/proposals          # Create proposal
POST /api/v1/governance/vote               # Vote on proposal
GET  /api/v1/governance/treasury           # Treasury stats
```

**Integration**:
- Read from GovernanceDAO contract
- Display proposals on-chain
- Enable voting through contract
- Track voting power

**Implementation Steps**:
- [ ] Create governance service
- [ ] Integrate with contracts
- [ ] Build API endpoints
- [ ] Create UI (new page)
- [ ] Test voting flow

---

### **Task 2.7: Staking Dashboard** 🥩 LOW PRIORITY

**Endpoints to Build**:
```python
# backend/queen-ai/app/api/v1/staking.py

GET  /api/v1/staking/pools                 # Available pools
GET  /api/v1/staking/user-stakes           # User's stakes
POST /api/v1/staking/stake                 # Stake tokens
POST /api/v1/staking/unstake               # Unstake tokens
POST /api/v1/staking/claim-rewards         # Claim rewards
GET  /api/v1/staking/apy                   # Current APY
```

**Integration**:
- Read from StakingManager contract
- Enable staking through contract
- Track rewards
- Display APY

**Implementation Steps**:
- [ ] Create staking service
- [ ] Integrate with contracts
- [ ] Build API endpoints
- [ ] Create UI (new page)
- [ ] Test staking flow

---

## 🟢 **PHASE 3: FULL INTEGRATION (Days 15-21)**

### **Task 3.1: Connect All Frontend Cards to Real APIs**

**Cards to Update**:
- [ ] `DashboardCard.tsx` → Portfolio API
- [ ] `PropertyCard.tsx` → Properties API
- [ ] `OTCPurchaseCard.tsx` → Complete OTC flow
- [ ] `PrivateInvestorCard.tsx` → Admin OTC management
- [ ] `MarketDataCard.tsx` → Market API
- [ ] `SwapCard.tsx` → DEX integration (future)

---

### **Task 3.2: Enhance Queen AI Context Awareness**

**Improvements**:
- User state tracking (wallet connected, KYC status, portfolio)
- Intelligent routing based on user context
- Personalized recommendations
- Conversation memory (persist across sessions)

**File**: `/backend/queen-ai/app/api/v1/frontend.py`

**Enhancements**:
```python
async def chat(request: ChatRequest):
    # Analyze user context
    user_context = await analyze_user_context(
        wallet_address=request.wallet_address,
        chat_history=request.chat_history
    )
    
    # Route to appropriate bee
    if "invest" in request.user_input.lower():
        if not user_context.wallet_connected:
            return {"message": "First, let's connect your wallet!"}
        elif not user_context.kyc_verified:
            return {"message": "You need KYC verification to invest"}
        else:
            return {"message": "Here are available properties", "cards": [...]}
```

---

### **Task 3.3: End-to-End Testing**

**Test Flows**:
- [ ] Greeting → Language → Theme → Chat
- [ ] New User → Wallet Connect → KYC → OTC Purchase
- [ ] Existing User → Dashboard → View Portfolio
- [ ] Property Browse → Invest → Transaction
- [ ] Admin → Approve OTC → Execute TGE
- [ ] Admin → Kingdom → Deploy Contracts

---

### **Task 3.4: Performance Optimization**

**Optimizations**:
- [ ] Implement Redis caching (market data, properties)
- [ ] Add pagination (properties, transactions)
- [ ] Optimize database queries
- [ ] Add CDN for images
- [ ] Enable API rate limiting
- [ ] Add request queuing (background tasks)

---

### **Task 3.5: Deploy Frontend**

**Steps**:
- [ ] Update all environment variables
- [ ] Build production bundle
- [ ] Deploy to Netlify/Vercel
- [ ] Configure custom domain
- [ ] Enable HTTPS
- [ ] Test deployed app

---

## 📊 **PROGRESS TRACKING**

### **Week 1: Critical Fixes + Properties API**
- Days 1-2: Fix API connections, hide broken features
- Days 3-5: Build Properties API
- Days 6-7: Integrate Properties with frontend

### **Week 2: Portfolio + OTC Complete**
- Days 8-10: Build Portfolio API
- Days 11-14: Complete OTC flow (approval, TGE)

### **Week 3: KYC + Market Data**
- Days 15-17: KYC system
- Days 18-19: Market data integration
- Days 20-21: Integration testing

### **Week 4: Governance + Staking + Deploy**
- Days 22-24: Governance system
- Days 25-26: Staking dashboard
- Days 27-28: Final testing + deployment

---

## ✅ **SUCCESS CRITERIA**

- [ ] All API endpoints respond correctly
- [ ] Frontend connects to deployed backend
- [ ] Zero broken features visible to users
- [ ] Complete user flows work end-to-end
- [ ] Admin can manage OTC requests
- [ ] Properties can be browsed and invested in
- [ ] Portfolio shows real data
- [ ] KYC verification works
- [ ] Queen AI routes intelligently
- [ ] Performance < 3s load time
- [ ] Zero console errors
- [ ] Mobile responsive

---

**Next Action**: Start with Task 1.1 - Fix Backend API Connection

