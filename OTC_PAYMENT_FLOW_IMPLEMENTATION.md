# 🔄 OTC Payment Flow - Complete Implementation Plan

**Date:** October 11, 2025, 9:50 PM  
**Status:** 🚧 READY TO IMPLEMENT

---

## 📊 **CURRENT STATE ANALYSIS**

### **✅ What Already Exists:**

1. **Private Sale Bee** (`app/bees/private_sale_bee.py`)
   - Full tiered pricing system (10 tiers, $0.10 - $0.145)
   - Purchase tracking and validation
   - Investor whitelist management
   - Queen approval workflow for large purchases
   - Sales statistics and reporting

2. **OTC Database** (`app/models/database.py`)
   - OTC requests storage (JSON-based)
   - Status tracking (pending/approved/rejected/distributed)
   - User management
   - Analytics tracking

3. **OTC Frontend Card** (`components/cards/OTCPurchaseCard.tsx`)
   - Multi-step form (welcome → wallet → amount → contact → review → submitted)
   - Basic submission to backend
   - **MISSING:** Actual payment step

4. **Backend API** (`app/api/v1/frontend.py`)
   - POST `/api/v1/frontend/otc-request` endpoint
   - Creates OTC request in database

---

## ❌ **WHAT'S MISSING**

### **1. Payment Step in Frontend**
Current flow skips payment:
```
Review → Submit → "Wait for email with payment instructions"
```

Should be:
```
Review → Pay Crypto → Verify Payment → Submit → Automatic Processing
```

### **2. Treasury Wallet Configuration**
- No admin UI to set treasury wallet address
- Hardcoded or missing treasury addresses
- Need different addresses for different stablecoins (USDT, USDC, DAI)

### **3. Payment Verification**
- No automated payment detection
- No blockchain transaction monitoring
- Manual verification only

### **4. Automatic Distribution at TGE**
- System needs to track all private sale purchases
- Automatic vested token distribution
- Integration with token vesting contracts

---

## 🎯 **IMPLEMENTATION PLAN**

### **Phase 1: Add Payment Step (Critical)**

#### **Step 1.1: Update OTC Frontend Flow**
Add payment step between 'review' and 'submitted':

```typescript
// New steps
type Step = 'welcome' | 'wallet' | 'amount' | 'contact' | 'review' | 'payment' | 'payment_pending' | 'submitted';

// Payment step workflow:
1. User reviews purchase
2. Click "Continue to Payment"
3. Show treasury wallet address for chosen stablecoin
4. User sends crypto
5. User enters transaction hash
6. Backend verifies transaction
7. Auto-update status to "payment_confirmed"
8. Show success message
```

#### **Step 1.2: Add Treasury Wallet Config to Admin**
Location: `app/kingdom/page.tsx` → SystemConfigTab

```typescript
<div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
  <h3 className="text-lg font-semibold text-white mb-4">Treasury Wallets (OTC Payments)</h3>
  
  <div className="space-y-4">
    <div>
      <label>USDT Treasury Wallet</label>
      <input type="text" placeholder="0x..." />
    </div>
    <div>
      <label>USDC Treasury Wallet</label>
      <input type="text" placeholder="0x..." />
    </div>
    <div>
      <label>DAI Treasury Wallet</label>
      <input type="text" placeholder="0x..." />
    </div>
    <div>
      <label>ETH Treasury Wallet (Backup)</label>
      <input type="text" placeholder="0x..." />
    </div>
  </div>
  
  <button>Save Treasury Configuration</button>
</div>
```

#### **Step 1.3: Add Payment Verification Endpoint**
Location: `app/api/v1/frontend.py`

```python
@router.post("/verify-otc-payment")
async def verify_otc_payment(
    request_id: str,
    tx_hash: str,
    payment_token: str,  # USDT/USDC/DAI/ETH
):
    """
    Verify that payment transaction is valid:
    1. Check tx exists on blockchain
    2. Verify amount matches request
    3. Verify sent to correct treasury wallet
    4. Update request status to 'payment_confirmed'
    5. Notify Private Sale Bee
    """
    # Use Web3.py or Etherscan API to verify transaction
    # ...
    return {
        "success": True,
        "payment_verified": True,
        "status": "payment_confirmed"
    }
```

---

### **Phase 2: Private Sale Ledger Integration**

#### **Step 2.1: Enhanced OTC Request Model**
Add fields to track full payment flow:

```json
{
  "id": "OTC-001",
  "status": "payment_confirmed",  // pending → payment_confirmed → tokens_distributed
  "investor": {
    "name": "John Doe",
    "email": "john@example.com",
    "wallet": "0x...",
    "kyc_status": "approved"
  },
  "purchase": {
    "omk_tokens": 250000,
    "price_per_token": 0.10,
    "total_usd": 25000,
    "tier": 1
  },
  "payment": {
    "token": "USDT",
    "tx_hash": "0x...",
    "confirmed_at": "2025-10-11T21:00:00Z",
    "verified": true,
    "treasury_wallet": "0x..."
  },
  "distribution": {
    "scheduled_for_tge": true,
    "vesting_schedule": "20% unlock at TGE, 80% vested over 6 months",
    "distributed": false,
    "distribution_tx_hash": null
  },
  "timestamps": {
    "created_at": "2025-10-11T20:30:00Z",
    "payment_confirmed_at": "2025-10-11T21:00:00Z",
    "distributed_at": null
  }
}
```

#### **Step 2.2: Private Sale Ledger Storage**
Create new file: `backend/queen-ai/data/private_sale_ledger.json`

```json
{
  "total_raised_usd": 125000,
  "total_tokens_sold": 1250000,
  "unique_investors": 5,
  "investors": [
    {
      "wallet": "0x...",
      "total_tokens": 250000,
      "total_paid_usd": 25000,
      "purchases": [
        {
          "request_id": "OTC-001",
          "tokens": 250000,
          "price": 0.10,
          "date": "2025-10-11"
        }
      ],
      "distribution_status": "pending_tge"
    }
  ]
}
```

---

### **Phase 3: Automatic TGE Distribution**

#### **Step 3.1: TGE Trigger Endpoint**
Location: `app/api/v1/admin.py`

```python
@router.post("/trigger-tge")
async def trigger_tge():
    """
    Trigger Token Generation Event:
    1. Load all approved OTC requests with payment_confirmed status
    2. Deploy vesting contracts
    3. Distribute tokens to investor wallets
    4. Update ledger with distribution_tx_hash
    5. Send confirmation emails
    """
    # Load private sale ledger
    ledger = load_private_sale_ledger()
    
    # For each investor:
    for investor in ledger['investors']:
        if investor['distribution_status'] == 'pending_tge':
            # Deploy vesting contract
            tx_hash = deploy_vesting_contract(
                investor['wallet'],
                investor['total_tokens'],
                vesting_schedule={'cliff': 0, 'duration': 180}  # 6 months
            )
            
            # Update status
            investor['distribution_status'] = 'distributed'
            investor['distribution_tx_hash'] = tx_hash
    
    save_private_sale_ledger(ledger)
    
    return {"success": True, "distributed_count": len(investors)}
```

---

## 👑 **ADMIN APPROVAL WORKFLOW**

### **Automatic Processing (No Admin Needed):**
- ✅ Standard purchases: < 20M OMK tokens
- ✅ Payment verified on blockchain
- ✅ Investor KYC approved
- ✅ Within purchase limits

**Flow:**
```
User submits → Pays crypto → System verifies → Auto-approved → Queued for TGE
```

### **Requires Admin Approval (Whale Sales):**
- ⚠️ Large purchases: ≥ 20M OMK tokens
- ⚠️ Bulk sales / institutional investors
- ⚠️ Special pricing requests
- ⚠️ Payment issues or disputes

**Flow:**
```
User submits → Pays crypto → System verifies → Flagged for admin review → 
Admin approves/rejects → If approved, queued for TGE
```

### **Admin Review Interface:**
Location: `app/kingdom/page.tsx` → OTC Management Tab

```typescript
<div className="bg-gradient-to-br from-orange-900/20 to-red-900/20 border border-orange-500/30 rounded-xl p-6">
  <div className="flex items-center gap-3 mb-4">
    <AlertCircle className="w-6 h-6 text-orange-400" />
    <h3 className="text-xl font-bold text-white">Whale Sales - Requires Approval</h3>
    <span className="px-3 py-1 bg-orange-500 text-black font-bold rounded-full text-sm">
      3 Pending
    </span>
  </div>
  
  {whaleSales.map(sale => (
    <div key={sale.id} className="bg-black/30 border border-orange-500/20 rounded-lg p-4 mb-3">
      <div className="flex justify-between items-start mb-3">
        <div>
          <p className="text-white font-bold">{sale.name}</p>
          <p className="text-sm text-gray-400">{sale.email}</p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-orange-400">
            {(sale.omk_tokens / 1000000).toFixed(1)}M OMK
          </p>
          <p className="text-sm text-green-400">${(sale.total_usd / 1000).toFixed(0)}K</p>
        </div>
      </div>
      
      <div className="bg-blue-900/20 border border-blue-500/30 rounded p-3 mb-3">
        <p className="text-xs text-gray-400 mb-1">Payment Verified:</p>
        <p className="text-sm text-white font-mono">{sale.tx_hash.slice(0, 20)}...</p>
        <p className="text-xs text-green-400 mt-1">✓ {sale.payment_amount} USDT confirmed</p>
      </div>
      
      <div className="flex gap-2">
        <button 
          onClick={() => approveWhaleSale(sale.id)}
          className="flex-1 py-2 bg-green-600 hover:bg-green-500 text-white font-bold rounded-lg"
        >
          ✓ Approve
        </button>
        <button 
          onClick={() => rejectWhaleSale(sale.id)}
          className="flex-1 py-2 bg-red-600 hover:bg-red-500 text-white font-bold rounded-lg"
        >
          ✗ Reject
        </button>
      </div>
    </div>
  ))}
</div>
```

### **Approval Threshold Configuration:**
Admin can adjust the whale sale threshold:

```typescript
<div>
  <label className="block text-sm text-gray-400 mb-2">
    Whale Sale Threshold (requires manual approval)
  </label>
  <input
    type="number"
    value={whaleSaleThreshold}
    onChange={(e) => setWhaleSaleThreshold(Number(e.target.value))}
    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white"
  />
  <p className="text-xs text-gray-500 mt-1">
    Purchases of {whaleSaleThreshold.toLocaleString()} OMK or more require admin approval
  </p>
</div>
```

**Default:** 20,000,000 OMK (20M tokens = $2M at $0.10)

---

## 🔧 **IMMEDIATE FIXES NEEDED**

### **Fix 1: Chat Scrolling (CRITICAL)**
- New messages still cut off at bottom
- Need more padding below last message

### **Fix 2: OTC Card Responsiveness**
- Modal too wide on mobile
- Text overflow issues
- Button sizes

### **Fix 3: Add Payment Step to OTC**
- Current flow incomplete
- Missing actual payment collection

---

## 📝 **IMPLEMENTATION ORDER**

1. ✅ Fix chat scrolling (COMPLETED)
2. ✅ Fix OTC to trigger based on admin config (COMPLETED)
3. 🚧 Fix OTC card responsiveness (IN PROGRESS)
4. 🚧 Add treasury wallet config to admin (IN PROGRESS)
5. ⏳ Add payment step to OTC flow (NEXT)
6. ⏳ Add payment verification backend (NEXT)
7. ⏳ Integrate with Private Sale Bee (NEXT)
8. ⏳ Add TGE distribution system (FUTURE)

---

## 🧪 **TESTING CHECKLIST**

### **OTC Payment Flow Test:**
```
1. User clicks "Buy OMK"
2. Verify shows OTC form (not swap)
3. Fill in 250,000 OMK tokens
4. Total shows $25,000 (at $0.10)
5. Click "Continue to Payment"
6. See treasury wallet address for USDT
7. Send USDT from MetaMask
8. Enter transaction hash
9. System verifies on blockchain
10. Status updates to "Payment Confirmed"
11. Show success: "Tokens will be distributed at TGE"
12. Admin can see in pending distributions
13. At TGE, admin clicks "Trigger Distribution"
14. Tokens sent to investor wallet with vesting
```

---

## 💡 **SMART CONTRACT INTEGRATION** (Future)

### **Vesting Contract:**
```solidity
contract OMKVesting {
    struct VestingSchedule {
        address beneficiary;
        uint256 totalAmount;
        uint256 cliff;  // in days
        uint256 duration;  // in days
        uint256 startTime;
        uint256 released;
    }
    
    mapping(address => VestingSchedule) public vestingSchedules;
    
    function release(address beneficiary) public {
        // Calculate vested amount based on time
        // Transfer vested tokens to beneficiary
        // Update released amount
    }
}
```

---

**Ready to implement!** 🚀

Next: Add treasury config to admin + add payment step to OTC card.
