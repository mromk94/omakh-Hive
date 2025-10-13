# 🔍 MOCK DATA AUDIT & IMPLEMENTATION PLAN

**Date:** October 12, 2025, 7:35 PM  
**Status:** 🔴 CRITICAL BUGS FOUND + MOCK DATA IDENTIFIED

---

## 🚨 **CRITICAL BUG FOUND**

### **Authentication Token Mismatch**
- **Login page** (`/kingdom/login/page.tsx`) stores: `auth_token`
- **All Kingdom components** look for: `admin_token`
- **Result:** ❌ Authentication broken after login!

**Fix:** Standardize on `auth_token` everywhere

---

## 📋 **MOCK DATA FOUND**

### **1. DashboardCard.tsx** ❌
**Location:** `/components/cards/DashboardCard.tsx`

**Mock Data:**
```typescript
const ethValue = ethBalance ? parseFloat(ethBalance.formatted) * 2500 : 0; // Mock ETH price
const omkValue = 0; // TODO: Fetch real OMK balance from contract
const realEstateValue = 0; // TODO: Fetch from backend
const change24h = 0; // TODO: Calculate from price history
```

**Backend Endpoint Needed:**
- `GET /api/v1/user/portfolio` - Get user's complete portfolio

---

### **2. MarketDataCard.tsx** ❌
**Location:** `/components/cards/MarketDataCard.tsx`

**Mock Data:**
```typescript
generateMockData(): MarketData {
  return {
    omk: {
      price: 0.10,
      marketCap: 50000000,
      circulation: 500000000,
      totalSupply: 1000000000,
      volume24h: 2500000,
      priceChange24h: 0.0025,
      priceChangePercent: 2.56,
    },
    liquidity: { eth_omk: 1250000, usdt_omk: 1750000, total: 3000000 },
    crypto: {
      eth: { price: 2485.32, change24h: 1.85 },
      sol: { price: 98.47, change24h: -0.92 },
      btc: { price: 43250.18, change24h: 2.14 },
    }
  };
}
```

**Backend Endpoint:** Already tries `GET /api/v1/market/data` but gets 404

---

### **3. PrivateInvestorCard.tsx** ❌ ❌ ❌
**Location:** `/components/cards/PrivateInvestorCard.tsx`

**Complete Mock Registry:**
```typescript
const [investors, setInvestors] = useState<Investor[]>([
  {
    wallet: '0x742d35ab9...529fa',
    allocation: '1,000,000',
    amountPaid: '$100,000',
    pricePerToken: '$0.10',
    investorId: 'INV-001',
    distributed: true
  },
  // ... more mock data
]);
```

**Mock Functions:**
- `handleRegisterInvestor` - Just pushes to state
- `handleExecuteTGE` - Sets local flag
- `handleDistributeToInvestor` - Updates state only
- `handleDistributeAll` - Updates state only

**Backend Endpoints Needed:**
- `GET /api/v1/admin/private-investors` - List all private investors
- `POST /api/v1/admin/private-investors` - Register new investor
- `POST /api/v1/admin/private-investors/tge` - Execute TGE
- `POST /api/v1/admin/private-investors/{id}/distribute` - Distribute tokens
- `POST /api/v1/admin/private-investors/distribute-all` - Batch distribute

---

### **4. OTCPurchaseCard.tsx** ✅ (Mostly Fixed)
**Location:** `/components/cards/OTCPurchaseCard.tsx`

**Status:** ✅ Fetches config from backend  
**Issue:** Has hardcoded fallback treasury wallets

```typescript
const [treasuryWallets, setTreasuryWallets] = useState<{[key: string]: string}>({
  USDT: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0',  // Fallback
  USDC: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0',
  DAI: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0'
});
```

**Fix:** Use backend config or show error if not set

---

### **5. Kingdom Page Authentication** ❌
**Location:** `/app/kingdom/page.tsx`

**Issues:**
- Checks for `admin_token` (wrong key!)
- No actual token verification with backend
- Just sets `isAuthenticated = true` without validation

```typescript
const token = localStorage.getItem('admin_token');  // Wrong!
if (!token) {
  router.push('/kingdom/login');
  return;
}
// TODO: Verify token with backend
setIsAuthenticated(true);  // No verification!
```

**Fix:** Use `auth_token` and verify with backend

---

### **6. User Management** ❌
**Location:** `/app/kingdom/components/UserManagement.tsx`

**Issues:**
- Calls `/api/v1/admin/users` (endpoint doesn't exist!)
- Mock actions don't actually work

**Backend Endpoints Needed:**
- `GET /api/v1/admin/users` - List all users
- `POST /api/v1/admin/users/{id}/activate` - Activate user
- `POST /api/v1/admin/users/{id}/deactivate` - Deactivate user
- `POST /api/v1/admin/users/{id}/verify-email` - Verify email
- `DELETE /api/v1/admin/users/{id}` - Delete user

---

## ✅ **BACKEND ENDPOINTS THAT EXIST**

### **Admin Endpoints (working):**
- ✅ `GET /api/v1/admin/config`
- ✅ `PUT /api/v1/admin/config`
- ✅ `GET /api/v1/admin/otc/requests`
- ✅ `POST /api/v1/admin/otc/requests/{id}/approve`
- ✅ `POST /api/v1/admin/otc/requests/{id}/reject`
- ✅ `GET /api/v1/admin/analytics/overview`
- ✅ `GET /api/v1/admin/queen/bees`
- ✅ `POST /api/v1/admin/queen/chat`

### **Auth Endpoints (working):**
- ✅ `POST /api/v1/auth/login`
- ✅ `POST /api/v1/auth/register`
- ✅ `GET /api/v1/auth/me`

---

## 🎯 **IMPLEMENTATION PRIORITY**

### **Priority 1: CRITICAL (Auth Bug)**
1. Fix token name mismatch (`admin_token` → `auth_token`)
2. Implement proper token verification in Kingdom page

### **Priority 2: HIGH (Backend Endpoints)**
3. Create `/api/v1/market/data` endpoint
4. Create `/api/v1/user/portfolio` endpoint
5. Create private investor management endpoints

### **Priority 3: MEDIUM (Frontend Updates)**
6. Remove fallback mock data from MarketDataCard
7. Connect PrivateInvestorCard to real endpoints
8. Add proper error handling when backend is down

### **Priority 4: LOW (UX Improvements)**
9. Add loading states
10. Add offline indicators
11. Better error messages

---

## 🔧 **DETAILED FIXES**

### **Fix 1: Authentication Token**

**Frontend Changes:**
```typescript
// app/kingdom/page.tsx
const token = localStorage.getItem('auth_token');  // Changed from admin_token

// Verify token with backend
const response = await fetch('http://localhost:8001/api/v1/auth/verify', {
  headers: { 'Authorization': `Bearer ${token}` }
});
```

**Backend:** Add token verification endpoint

---

### **Fix 2: Market Data Endpoint**

**New Backend File:** `/backend/queen-ai/app/api/v1/market.py`

```python
@router.get("/data")
async def get_market_data(request: Request):
    """Get comprehensive market data"""
    queen = request.app.state.queen
    agent = queen.market_data_agent
    
    # Get real data from MarketDataAgent
    omk_data = await agent.get_omk_price_data()
    crypto_data = await agent.get_crypto_prices()
    
    return {
        "success": True,
        "data": {
            "omk": omk_data,
            "crypto": crypto_data,
            "liquidity": agent.get_liquidity_data(),
            "timestamp": datetime.now().isoformat()
        }
    }
```

---

### **Fix 3: Portfolio Endpoint**

**New Backend Route:**

```python
@router.get("/portfolio")
async def get_user_portfolio(
    user: User = Depends(get_current_user)
):
    """Get user's complete portfolio"""
    return {
        "success": True,
        "portfolio": {
            "omk_balance": user.omk_balance,
            "omk_value_usd": user.omk_balance * get_omk_price(),
            "real_estate_value": calculate_user_property_value(user.id),
            "total_value": calculate_total_portfolio_value(user.id),
            "holdings": get_user_holdings(user.id)
        }
    }
```

---

### **Fix 4: Private Investor Endpoints**

**New Backend Routes:**

```python
# List investors
@router.get("/private-investors")
async def list_private_investors(admin: User = Depends(get_current_admin)):
    investors = db.get_all_private_investors()
    return {"success": True, "investors": investors}

# Register investor
@router.post("/private-investors")
async def register_private_investor(
    data: InvestorRegistration,
    admin: User = Depends(get_current_admin)
):
    investor = db.create_private_investor(data.dict())
    return {"success": True, "investor": investor}

# Execute TGE
@router.post("/private-investors/tge")
async def execute_tge(admin: User = Depends(get_current_admin)):
    result = await smart_contract_execute_tge()
    return {"success": True, "result": result}
```

---

## 📊 **SUMMARY**

### **Mock Data Issues Found:**
- ❌ 1 critical auth bug
- ❌ 3 components with complete mock data
- ❌ 5 missing backend endpoints
- ❌ 2 components with partial mocks

### **Backend Status:**
- ✅ 15 working admin endpoints
- ✅ 3 working auth endpoints
- ❌ 8 missing endpoints needed

### **Estimated Implementation Time:**
- Fix 1 (Auth bug): 15 minutes
- Fix 2 (Market data): 30 minutes  
- Fix 3 (Portfolio): 45 minutes
- Fix 4 (Private investors): 60 minutes
- Fix 5 (User management): 45 minutes
- **Total: ~3 hours**

---

## ✅ **IMPLEMENTATION CHECKLIST**

### **Phase 1: Critical Fixes (30 min)**
- [ ] Fix token name mismatch
- [ ] Add token verification endpoint
- [ ] Update all Kingdom components to use `auth_token`
- [ ] Test login flow end-to-end

### **Phase 2: Backend Endpoints (2 hrs)**
- [ ] Create `/api/v1/market/data` endpoint
- [ ] Create `/api/v1/user/portfolio` endpoint
- [ ] Create private investor CRUD endpoints
- [ ] Create user management endpoints
- [ ] Add proper database models

### **Phase 3: Frontend Integration (1 hr)**
- [ ] Update DashboardCard to use real portfolio data
- [ ] Remove mock data generators from MarketDataCard
- [ ] Connect PrivateInvestorCard to backend
- [ ] Add error handling and loading states

### **Phase 4: Testing (30 min)**
- [ ] Test admin login
- [ ] Test portfolio display
- [ ] Test private investor registration
- [ ] Test market data display
- [ ] Test offline behavior

---

## 🎉 **SUCCESS CRITERIA**

1. ✅ Admin can login and stay logged in
2. ✅ Dashboard shows real portfolio data (when wallet connected)
3. ✅ Market data comes from backend (with live prices)
4. ✅ Private investor management works end-to-end
5. ✅ No console errors related to missing endpoints
6. ✅ Graceful fallbacks when backend is offline

---

**Ready to implement? Approve and I'll fix everything systematically.**
