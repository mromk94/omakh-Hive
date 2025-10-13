# 🤖 Market Data AI Agent Implementation - TODO

**Created:** October 11, 2025, 8:10 PM  
**Priority:** HIGH  
**Status:** 📋 PLANNING PHASE

---

## 🎯 **OBJECTIVE**

Replace mock market data with **real-time data** from an AI agent that:
1. Fetches live crypto market data (BTC, ETH, SOL, USDT, USDC)
2. Provides crypto news and trends
3. Manages OMK token data (on-chain when available, OTC fallback otherwise)
4. Updates automatically and intelligently

---

## 📊 **ARCHITECTURE OVERVIEW**

```
┌─────────────────────────────────────────────────────────────┐
│                    MARKET DATA AI AGENT                      │
│                 (Agentverse/Custom Agent)                    │
└────────────┬────────────────────────────────────────────────┘
             │
      ┌──────┴───────┐
      │              │
┌─────▼──────┐  ┌───▼────────┐
│  External  │  │   Queen    │
│   APIs     │  │  AI Bees   │
└────┬───────┘  └────┬───────┘
     │               │
     │    ┌──────────┴──────────┐
     │    │                     │
┌────▼────▼─────┐   ┌───────────▼──────┐
│  Market Data  │   │   OMK OTC Data   │
│   (On-chain   │   │  (Queen + Bees)  │
│  + Oracles)   │   │                  │
└───────┬───────┘   └──────────┬───────┘
        │                      │
        └──────────┬───────────┘
                   │
         ┌─────────▼──────────┐
         │   Backend API      │
         │  /api/v1/market    │
         └─────────┬──────────┘
                   │
         ┌─────────▼──────────┐
         │  Frontend Display  │
         │  MarketDataCard    │
         └────────────────────┘
```

---

## 🔧 **PHASE 1: Fix Double Wallet Message** ⚡ URGENT

### Issue
Wallet connection message appears twice in chat after connecting wallet.

### Root Cause
`WalletConnectCard` component likely being rendered twice or callback fired multiple times.

### Solution
```typescript
// Option 1: Add ref to track if message sent
const messagesSentRef = useRef(new Set());

onConnected={(address) => {
  if (!messagesSentRef.current.has(address)) {
    messagesSentRef.current.add(address);
    addMessage('ai', `Great! Your wallet...`);
  }
}}

// Option 2: Check if message already exists before adding
const hasDuplicateMessage = messages.some(
  msg => msg.content.includes(`Your wallet ${address}...is connected`)
);
if (!hasDuplicateMessage) {
  addMessage('ai', `Great! Your wallet...`);
}
```

### Files to Modify
- `omk-frontend/app/chat/page.tsx` (line ~1684)
- OR `omk-frontend/components/cards/WalletConnectCard.tsx`

---

## 🤖 **PHASE 2: Market Data AI Agent Setup**

### 2.1 Agent Platform Decision

**Option A: Use Agentverse/ASI:One** (Already integrated)
- ✅ Infrastructure ready
- ✅ DeltaV integration
- ✅ Agent protocols established
- ⚠️ Dependency on external service

**Option B: Build Custom Agent** (Recommended)
- ✅ Full control
- ✅ Can deploy to Agentverse later
- ✅ Integrates directly with Queen
- ✅ No external dependencies

**Decision:** Build custom agent that can be deployed to both platforms

### 2.2 Agent Responsibilities

#### **Market Data Collection**
- [ ] Fetch BTC, ETH, SOL prices from CoinGecko/CoinMarketCap
- [ ] Get USDT, USDC stats
- [ ] Track total market cap
- [ ] Monitor 24h trading volumes
- [ ] Fetch crypto news from CryptoPanic/NewsAPI

#### **OMK Token Data Management**
**When Contract Address Available (On-Chain):**
- [ ] Query OMK contract for total supply
- [ ] Get circulating supply from on-chain data
- [ ] Fetch price from DEX (Uniswap/Raydium)
- [ ] Get liquidity pool stats (ETH/OMK, USDT/OMK)
- [ ] Calculate market cap from on-chain data

**When Contract Address Missing (OTC Fallback):**
- [ ] Get OTC price from Queen/Admin
- [ ] Calculate OTC treasury liquidity
- [ ] Get available OMK in OTC treasury
- [ ] Use maths_bee for price calculations
- [ ] Correlate data from private_sale_bee

### 2.3 Agent Architecture

```python
# backend/queen-ai/app/agents/market_data_agent.py

class MarketDataAgent:
    """
    Autonomous agent for fetching and managing market data
    """
    
    def __init__(self, queen_instance):
        self.queen = queen_instance
        self.maths_bee = queen.bee_manager.get_bee("maths")
        self.price_bee = queen.bee_manager.get_bee("liquidity_sentinel")  
        self.user_mgmt_bee = queen.bee_manager.get_bee("onboarding")
        self.blockchain_bee = queen.bee_manager.get_bee("blockchain")
        
        # Data sources
        self.coingecko_api = "https://api.coingecko.com/api/v3"
        self.cryptopanic_api = "https://cryptopanic.com/api/v1"
        
        # OMK Configuration
        self.omk_contract_address = None  # Set by admin
        self.omk_otc_price = 0.10  # Default, overridden by admin
        
    async def fetch_crypto_market_data(self):
        """Fetch real-time crypto data"""
        pass
        
    async def fetch_omk_data(self):
        """
        Fetch OMK data:
        - If contract_address exists: on-chain data
        - Else: OTC data from Queen
        """
        pass
        
    async def get_otc_data_from_queen(self):
        """Get OTC data by coordinating with bees"""
        pass
        
    async def fetch_crypto_news(self):
        """Fetch latest crypto news and trends"""
        pass
```

---

## 🗄️ **PHASE 3: Backend API Implementation**

### 3.1 Market Data Endpoints

```python
# backend/queen-ai/app/api/v1/market.py

from fastapi import APIRouter, HTTPException
from app.agents.market_data_agent import MarketDataAgent

router = APIRouter(prefix="/market", tags=["Market Data"])

@router.get("/data")
async def get_market_data(request: Request):
    """
    Get comprehensive market data
    Returns: OMK stats, crypto prices, liquidity, news
    """
    queen = request.app.state.queen
    agent = queen.market_data_agent
    
    data = await agent.get_comprehensive_data()
    return {"success": True, "data": data}

@router.get("/omk")
async def get_omk_data(request: Request):
    """Get OMK-specific data (on-chain or OTC)"""
    queen = request.app.state.queen
    agent = queen.market_data_agent
    
    omk_data = await agent.fetch_omk_data()
    return {"success": True, "data": omk_data}

@router.get("/news")
async def get_crypto_news(request: Request):
    """Get latest crypto news"""
    queen = request.app.state.queen
    agent = queen.market_data_agent
    
    news = await agent.fetch_crypto_news()
    return {"success": True, "news": news}
```

### 3.2 Admin Configuration Endpoints

```python
# backend/queen-ai/app/api/v1/admin.py (extend existing)

@router.post("/config/omk-contract")
async def set_omk_contract_address(data: Dict[str, str], request: Request):
    """
    Admin-only: Set OMK contract address
    When set, agent will fetch on-chain data
    """
    queen = request.app.state.queen
    # Verify admin authentication
    
    contract_address = data.get("address")
    queen.market_data_agent.set_omk_contract(contract_address)
    
    return {"success": True, "message": "Contract address updated"}

@router.post("/config/omk-otc-price")
async def set_omk_otc_price(data: Dict[str, float], request: Request):
    """
    Admin-only: Set OMK OTC price
    Takes precedence over calculated price
    """
    queen = request.app.state.queen
    
    otc_price = data.get("price")
    queen.market_data_agent.set_otc_price(otc_price)
    
    return {"success": True, "message": f"OTC price set to ${otc_price}"}

@router.get("/config/system")
async def get_system_config(request: Request):
    """
    Admin-only: Get current system configuration
    """
    queen = request.app.state.queen
    agent = queen.market_data_agent
    
    return {
        "success": True,
        "config": {
            "omk_contract_address": agent.omk_contract_address,
            "omk_otc_price": agent.omk_otc_price,
            "data_source": "on-chain" if agent.omk_contract_address else "otc",
        }
    }
```

---

## 👑 **PHASE 4: Queen + Bees Coordination**

### 4.1 OTC Data Calculation Flow

When contract address is **not set**, agent must calculate OTC data:

```python
async def get_otc_data_from_queen(self):
    """
    Coordinate with Queen's bees to calculate OTC metrics
    """
    
    # 1. Get OTC treasury balance from TreasuryBee
    treasury_data = await self.queen.bee_manager.execute_bee("treasury", {
        "type": "get_otc_balance"
    })
    otc_treasury_balance = treasury_data.get("balance", 0)
    
    # 2. Get all OTC requests from PrivateSaleBee
    otc_requests = await self.queen.bee_manager.execute_bee("private_sale", {
        "type": "get_all_requests"
    })
    
    # 3. Calculate total OMK allocated
    total_allocated = sum(req.get("allocation", 0) for req in otc_requests)
    
    # 4. Get available OMK in treasury
    available_omk = otc_treasury_balance - total_allocated
    
    # 5. Calculate average OTC price using MathsBee
    price_calc = await self.queen.bee_manager.execute_bee("maths", {
        "type": "calculate_weighted_average_price",
        "requests": otc_requests
    })
    calculated_price = price_calc.get("average_price", 0.10)
    
    # 6. Use admin price if set (takes precedence)
    final_price = self.omk_otc_price if self.omk_otc_price > 0 else calculated_price
    
    # 7. Calculate OTC market metrics
    otc_market_cap = total_allocated * final_price
    otc_liquidity = available_omk * final_price
    
    return {
        "price": final_price,
        "circulating_supply": total_allocated,
        "available_supply": available_omk,
        "treasury_balance": otc_treasury_balance,
        "market_cap": otc_market_cap,
        "liquidity": otc_liquidity,
        "data_source": "otc",
        "price_source": "admin_set" if self.omk_otc_price > 0 else "calculated"
    }
```

### 4.2 Bees Required

**Already Exist:**
- ✅ `maths_bee.py` - Price calculations
- ✅ `treasury_bee.py` - Treasury balance
- ✅ `private_sale_bee.py` - OTC requests
- ✅ `liquidity_sentinel_bee.py` - Price monitoring (rename to price_bee?)
- ✅ `onboarding_bee.py` - User management

**May Need Enhancement:**
- [ ] `maths_bee` - Add weighted average price calculation
- [ ] `treasury_bee` - Add OTC treasury tracking
- [ ] `private_sale_bee` - Add aggregation methods

---

## 🖥️ **PHASE 5: Admin Dashboard (Kingdom)**

### 5.1 Admin Configuration Interface

Create admin panel in `/kingdom` for:

#### **OMK Contract Configuration**
```typescript
// omk-frontend/app/kingdom/config/page.tsx

<section>
  <h2>OMK Token Configuration</h2>
  
  <div>
    <label>Contract Address (Ethereum)</label>
    <input 
      type="text" 
      placeholder="0x..."
      value={contractAddress}
      onChange={(e) => setContractAddress(e.target.value)}
    />
    <button onClick={saveContractAddress}>
      Save Contract Address
    </button>
  </div>
  
  <div>
    <label>OTC Price (USD)</label>
    <input 
      type="number" 
      step="0.01"
      placeholder="0.10"
      value={otcPrice}
      onChange={(e) => setOtcPrice(e.target.value)}
    />
    <button onClick={saveOtcPrice}>
      Set OTC Price
    </button>
    <span className="note">
      This price takes precedence over calculated price
    </span>
  </div>
  
  <div>
    <h3>Current Data Source</h3>
    <p>
      {contractAddress ? '✅ On-Chain Data' : '⚠️ OTC Data (Fallback)'}
    </p>
  </div>
</section>
```

#### **Treasury Addresses**
```typescript
<section>
  <h2>Treasury Wallets</h2>
  
  {treasuryTypes.map(type => (
    <div key={type}>
      <label>{type} Treasury</label>
      <input 
        type="text"
        placeholder="0x..."
        value={treasuries[type]}
        onChange={(e) => updateTreasury(type, e.target.value)}
      />
    </div>
  ))}
  
  <button onClick={saveTreasuries}>
    Save All Treasuries
  </button>
</section>
```

#### **Price Discovery Control**
```typescript
<section>
  <h2>Liquidity & Price Control</h2>
  
  <div>
    <label>Price Deviation Threshold (%)</label>
    <input 
      type="number"
      value={priceThreshold}
      onChange={(e) => setPriceThreshold(e.target.value)}
    />
  </div>
  
  <div>
    <label>Auto-Rebalance</label>
    <Switch 
      checked={autoRebalance}
      onChange={setAutoRebalance}
    />
  </div>
  
  <button onClick={saveLiquidityConfig}>
    Save Liquidity Settings
  </button>
</section>
```

### 5.2 Backend Routes for Admin

```python
# backend/queen-ai/app/api/v1/admin.py

@router.post("/treasuries")
async def set_treasuries(data: Dict[str, Dict[str, str]], request: Request):
    """Set all treasury addresses"""
    pass

@router.post("/liquidity/config")
async def set_liquidity_config(data: Dict[str, Any], request: Request):
    """Configure liquidity and price control settings"""
    pass

@router.get("/system/status")
async def get_system_status(request: Request):
    """Get comprehensive system status"""
    pass
```

---

## 📝 **PHASE 6: Implementation Checklist**

### Immediate (Phase 1) - Fix Double Message
- [ ] **FILE:** `omk-frontend/app/chat/page.tsx`
- [ ] Add ref to track sent messages
- [ ] Prevent duplicate wallet connection messages
- [ ] Test wallet connection flow

### Backend Agent (Phase 2-3)
- [ ] **CREATE:** `backend/queen-ai/app/agents/__init__.py`
- [ ] **CREATE:** `backend/queen-ai/app/agents/market_data_agent.py`
  - [ ] Initialize with Queen and bees
  - [ ] Implement `fetch_crypto_market_data()`
  - [ ] Implement `fetch_omk_data()`
  - [ ] Implement on-chain data fetching
  - [ ] Implement OTC data calculation
  - [ ] Implement `fetch_crypto_news()`
  - [ ] Add caching layer (Redis/memory)
  - [ ] Add error handling and fallbacks

- [ ] **CREATE:** `backend/queen-ai/app/api/v1/market.py`
  - [ ] GET `/market/data` - comprehensive data
  - [ ] GET `/market/omk` - OMK-specific data
  - [ ] GET `/market/news` - crypto news
  - [ ] Add rate limiting
  - [ ] Add caching headers

- [ ] **MODIFY:** `backend/queen-ai/app/api/v1/admin.py`
  - [ ] POST `/admin/config/omk-contract`
  - [ ] POST `/admin/config/omk-otc-price`
  - [ ] POST `/admin/treasuries`
  - [ ] POST `/admin/liquidity/config`
  - [ ] GET `/admin/config/system`
  - [ ] GET `/admin/system/status`

### Bee Enhancements (Phase 4)
- [ ] **MODIFY:** `backend/queen-ai/app/bees/maths_bee.py`
  - [ ] Add `calculate_weighted_average_price()`
  - [ ] Add OTC price calculation methods

- [ ] **MODIFY:** `backend/queen-ai/app/bees/treasury_bee.py`
  - [ ] Add `get_otc_balance()`
  - [ ] Track OTC treasury separately

- [ ] **MODIFY:** `backend/queen-ai/app/bees/private_sale_bee.py`
  - [ ] Add `get_all_requests()` aggregation
  - [ ] Add `get_total_allocated()`

- [ ] **VERIFY:** `backend/queen-ai/app/bees/liquidity_sentinel_bee.py`
  - [ ] Confirm price monitoring capabilities
  - [ ] Add OTC price tracking if needed

### Frontend Admin Panel (Phase 5)
- [ ] **CREATE:** `omk-frontend/app/kingdom/config/page.tsx`
  - [ ] OMK contract address input
  - [ ] OTC price setter
  - [ ] Treasury addresses manager
  - [ ] Liquidity configuration
  - [ ] System status display

- [ ] **CREATE:** `omk-frontend/lib/api/admin.ts`
  - [ ] API calls for admin config
  - [ ] TypeScript interfaces

### Frontend Market Data Integration (Phase 6)
- [ ] **MODIFY:** `omk-frontend/components/cards/MarketDataCard.tsx`
  - [ ] Replace mock data generator
  - [ ] Call real `/api/v1/market/data` endpoint
  - [ ] Handle on-chain vs OTC data display
  - [ ] Add data source indicator
  - [ ] Show crypto news section

- [ ] **ADD:** News display component
  - [ ] Crypto news carousel
  - [ ] Trending topics
  - [ ] Market sentiment

### Integration & Testing
- [ ] Connect agent to Queen initialization
- [ ] Test on-chain data fetching (with testnet)
- [ ] Test OTC fallback mode
- [ ] Test admin configuration endpoints
- [ ] End-to-end testing
- [ ] Performance testing (caching, rate limits)

### Deployment
- [ ] Add environment variables for API keys
- [ ] Deploy agent to Agentverse (optional)
- [ ] Set up monitoring
- [ ] Create admin documentation
- [ ] Update deployment guides

---

## 🔑 **API KEYS NEEDED**

### Required
- [ ] **CoinGecko API** - `COINGECKO_API_KEY`
- [ ] **CoinMarketCap API** (Alternative) - `COINMARKETCAP_API_KEY`

### Optional
- [ ] **CryptoPanic API** - `CRYPTOPANIC_API_KEY` (news)
- [ ] **NewsAPI** - `NEWS_API_KEY` (alternative news)
- [ ] **Chainlink** - For price oracles
- [ ] **Infura/Alchemy** - `INFURA_PROJECT_ID` (Ethereum RPC)
- [ ] **Helius** - `HELIUS_API_KEY` (Solana RPC)

Add to:
```bash
# backend/queen-ai/.env
COINGECKO_API_KEY=your_key_here
CRYPTOPANIC_API_KEY=your_key_here
INFURA_PROJECT_ID=your_project_id
```

---

## 📊 **DATA FLOW DIAGRAM**

```
User Views Dashboard
         │
         ▼
Frontend calls GET /api/v1/market/data
         │
         ▼
Backend Market Data Agent
         │
    ┌────┴────┐
    │         │
    ▼         ▼
Check OMK   Fetch Crypto
Contract?   Market Data
    │         │
    │         ├─► CoinGecko API
    │         ├─► CryptoPanic API
    │         └─► Return BTC/ETH/SOL/News
    │
    ├─► YES: Contract exists
    │    ├─► Query blockchain (Infura)
    │    ├─► Get Uniswap pools
    │    ├─► Calculate on-chain metrics
    │    └─► Return on-chain data
    │
    └─► NO: Contract not set
         ├─► Call TreasuryBee (OTC balance)
         ├─► Call PrivateSaleBee (OTC requests)
         ├─► Call MathsBee (price calc)
         ├─► Use admin OTC price if set
         └─► Return OTC data
         
Combined Data
         │
         ▼
Return to Frontend
         │
         ▼
MarketDataCard displays real data
```

---

## 🎯 **SUCCESS CRITERIA**

### Must Have
- ✅ Real crypto prices (BTC, ETH, SOL)
- ✅ OMK data (on-chain OR OTC)
- ✅ Admin can set contract address
- ✅ Admin can set OTC price
- ✅ Data refreshes automatically
- ✅ No more mock data in production

### Nice to Have
- 🌟 Crypto news integration
- 🌟 Price alerts
- 🌟 Historical price charts
- 🌟 Market sentiment analysis
- 🌟 Deploy agent to Agentverse

---

## ⏱️ **ESTIMATED TIMELINE**

- **Phase 1** (Fix double message): 30 mins
- **Phase 2** (Agent setup): 3-4 hours
- **Phase 3** (Backend API): 2-3 hours
- **Phase 4** (Bees coordination): 2 hours
- **Phase 5** (Admin panel): 3-4 hours
- **Phase 6** (Frontend integration): 2 hours
- **Testing & Polish**: 2-3 hours

**Total:** ~16-20 hours of focused development

---

## 🚀 **NEXT STEPS**

1. **Fix double wallet message** (30 mins) ⚡
2. **Set up API keys** (CoinGecko, etc.)
3. **Create market_data_agent.py** 
4. **Implement backend endpoints**
5. **Build admin configuration panel**
6. **Connect frontend to real data**
7. **Test and deploy**

---

**Ready to implement! Let's start with Phase 1 (fixing the double message).**
