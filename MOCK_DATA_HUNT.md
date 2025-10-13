# 🎯 Mock Data Hunt - Complete List

**Date:** October 10, 2025, 11:13 PM  
**Status:** 🔍 COMPREHENSIVE AUDIT

---

## 📋 All Mock Data Locations Found

### 1. `/app/dashboard/page.tsx` ❌ **CRITICAL**

**Lines 43-119: TONS of hardcoded mock data**

```typescript
// Mock data - replace with actual API calls
const [portfolio, setPortfolio] = useState<PortfolioStats>({
  totalValue: 5250.00,        // ❌ FAKE!
  cryptoValue: 2500.00,       // ❌ FAKE!
  realEstateValue: 2750.00,   // ❌ FAKE!
  change24h: 125.50,          // ❌ FAKE!
  changePercent: 2.45,        // ❌ FAKE!
});

const [holdings, setHoldings] = useState<Holding[]>([
  {
    type: 'crypto',
    name: 'Ethereum',
    symbol: 'ETH',
    amount: 0.5,              // ❌ FAKE!
    value: 1250.00,           // ❌ FAKE!
    change24h: 2.3,           // ❌ FAKE!
    icon: '💎',
  },
  {
    type: 'crypto',
    name: 'OMK Token',
    symbol: 'OMK',
    amount: 10000,            // ❌ FAKE 10,000 OMK!
    value: 1000.00,           // ❌ FAKE!
    change24h: 5.2,           // ❌ FAKE!
    icon: '🟡',
  },
  {
    type: 'crypto',
    name: 'USDC',
    symbol: 'USDC',
    amount: 250,              // ❌ FAKE!
    value: 250.00,            // ❌ FAKE!
    change24h: 0,             // ❌ FAKE!
    icon: '💵',
  },
  {
    type: 'real-estate',
    name: 'Dubai Marina Apartment',
    symbol: 'Blocks',
    amount: 10,               // ❌ FAKE!
    value: 1500.00,           // ❌ FAKE!
    change24h: 1.2,           // ❌ FAKE!
    icon: '🏢',
  },
  {
    type: 'real-estate',
    name: 'London Commercial Property',
    symbol: 'Blocks',
    amount: 5,                // ❌ FAKE!
    value: 1250.00,           // ❌ FAKE!
    change24h: 0.8,           // ❌ FAKE!
    icon: '🏛️',
  },
]);

const [transactions, setTransactions] = useState<Transaction[]>([
  {
    id: '1',
    type: 'buy',
    asset: 'OMK',
    amount: 1000,             // ❌ FAKE!
    value: 100.00,            // ❌ FAKE!
    timestamp: new Date(Date.now() - 3600000),
    status: 'completed',
  },
  {
    id: '2',
    type: 'buy',
    asset: 'Dubai Marina - 10 Blocks',
    amount: 10,               // ❌ FAKE!
    value: 1500.00,           // ❌ FAKE!
    timestamp: new Date(Date.now() - 7200000),
    status: 'completed',
  },
]);
```

**Impact:** HIGH - This is the main dashboard showing completely fake portfolio!

---

### 2. `/app/invest/page.tsx` ❌ **HIGH PRIORITY**

**Lines 34-92: Mock properties data**

```typescript
// Mock properties data
const [properties] = useState<Property[]>([
  {
    id: '1',
    name: 'Luxury Apartment Complex',
    location: 'Dubai Marina',
    country: 'UAE',
    image: '🏙️',
    totalValue: 100000,           // ❌ FAKE!
    blockPrice: 100,              // ❌ FAKE!
    totalBlocks: 1000,            // ❌ FAKE!
    availableBlocks: 450,         // ❌ FAKE!
    apy: 12,                      // ❌ FAKE!
    type: 'residential',
    featured: true,
  },
  {
    id: '2',
    name: 'Commercial Office Building',
    location: 'Canary Wharf',
    country: 'UK',
    image: '🏢',
    totalValue: 250000,           // ❌ FAKE!
    blockPrice: 250,              // ❌ FAKE!
    totalBlocks: 1000,            // ❌ FAKE!
    availableBlocks: 320,         // ❌ FAKE!
    apy: 10.5,                    // ❌ FAKE!
    type: 'commercial',
    featured: true,
  },
  {
    id: '3',
    name: 'Beach Resort Villa',
    location: 'Bali',
    country: 'Indonesia',
    image: '🏖️',
    totalValue: 75000,            // ❌ FAKE!
    blockPrice: 75,               // ❌ FAKE!
    totalBlocks: 1000,            // ❌ FAKE!
    availableBlocks: 580,         // ❌ FAKE!
    apy: 14,                      // ❌ FAKE!
    type: 'residential',
    featured: false,
  },
  {
    id: '4',
    name: 'Downtown Shopping Mall',
    location: 'Singapore',
    country: 'Singapore',
    image: '🏬',
    totalValue: 500000,           // ❌ FAKE!
    blockPrice: 500,              // ❌ FAKE!
    totalBlocks: 1000,            // ❌ FAKE!
    availableBlocks: 250,         // ❌ FAKE!
    apy: 9.5,                     // ❌ FAKE!
    type: 'commercial',
    featured: false,
  },
]);
```

**Impact:** HIGH - Invest page showing completely fake properties!

---

### 3. `/components/cards/PrivateInvestorCard.tsx` ❌ **MEDIUM**

**Lines 31-45: Mock investors**

```typescript
// Mock data - replace with actual contract calls
const [investors, setInvestors] = useState<Investor[]>([
  {
    wallet: '0x742d35ab9...529fa',    // ❌ FAKE address!
    allocation: 50000,                // ❌ FAKE!
    amountPaid: 5000,                 // ❌ FAKE!
    pricePerToken: 0.10,              // ❌ FAKE!
    registeredAt: new Date('2024-01-15'),
    distributed: false,
  },
  {
    wallet: '0x8f3e7a4b2...931cd',    // ❌ FAKE address!
    allocation: 100000,               // ❌ FAKE!
    amountPaid: 10000,                // ❌ FAKE!
    pricePerToken: 0.10,              // ❌ FAKE!
    registeredAt: new Date('2024-01-20'),
    distributed: false,
  },
]);
```

**Lines 70-113: Mock contract calls**

```typescript
// Mock registration - replace with actual contract call
await new Promise(resolve => setTimeout(resolve, 2000)); // ❌ Fake delay!

// Mock TGE execution - replace with actual contract call
await new Promise(resolve => setTimeout(resolve, 3000)); // ❌ Fake delay!

// Mock distribution - replace with actual contract call
await new Promise(resolve => setTimeout(resolve, 2000)); // ❌ Fake delay!

// Mock batch distribution - replace with actual contract call
await new Promise(resolve => setTimeout(resolve, 3000)); // ❌ Fake delay!
```

**Impact:** MEDIUM - Admin panel showing fake investors and fake transactions

---

### 4. `/components/cards/DashboardCard.tsx` ⚠️ **PARTIALLY FIXED**

**Line 21: Mock ETH price**

```typescript
const ethValue = ethBalance ? parseFloat(ethBalance.formatted) * 2500 : 0; // Mock ETH price
```

**Line 41: Mock ETH price (BalanceBubble)**

```typescript
(ethBalance ? parseFloat(ethBalance.formatted) * 2500 : 0); // Mock ETH price
```

**Status:** Uses real balance but hardcoded price ($2,500)

**Impact:** LOW - Price should come from oracle but balance is real

---

### 5. `/components/web3/BalanceBubble.tsx` ⚠️ **PARTIALLY FIXED**

**Lines 157-173: Mock OMK balance**

```typescript
{/* OMK Balance (Mock) */}
<div className="flex items-center justify-between p-3 bg-yellow-500/5 rounded-lg">
  <div className="flex items-center gap-2">
    <span className="text-2xl">🟡</span>
    <div>
      <div className="text-sm font-semibold text-stone-100">OMK</div>
      <div className="text-xs text-stone-400">Omakh Token</div>
    </div>
  </div>
  <div className="text-right">
    <div className="text-sm font-bold text-stone-100">
      0.00                          // ❌ Hardcoded zero!
    </div>
    <div className="text-xs text-stone-400">
      {formatCurrency(0)}          // ❌ Hardcoded zero!
    </div>
  </div>
</div>
```

**Impact:** LOW - Shows 0, should fetch from contract

---

## 📊 Priority Matrix

### 🔴 CRITICAL (Must Fix ASAP)
1. **`/app/dashboard/page.tsx`** - Entire dashboard is fake!
   - Mock portfolio stats
   - Mock holdings (ETH, OMK, USDC, properties)
   - Mock transactions
   - **Severity: 10/10**

### 🟠 HIGH (Fix Soon)
2. **`/app/invest/page.tsx`** - All properties are fake!
   - 4 fake properties with fake data
   - Users think these are real investments
   - **Severity: 8/10**

### 🟡 MEDIUM (Fix When Possible)
3. **`/components/cards/PrivateInvestorCard.tsx`** - Admin panel fake
   - Mock investors
   - Fake contract interactions
   - **Severity: 6/10**

### 🟢 LOW (Nice to Have)
4. **ETH Price** - Hardcoded $2,500
   - Should use Chainlink oracle
   - **Severity: 3/10**

5. **OMK Balance** - Shows hardcoded 0
   - Should fetch from contract
   - **Severity: 3/10**

---

## 🔧 Recommended Fixes

### Fix #1: Dashboard Page (CRITICAL)

**Replace mock data with real queries:**

```typescript
// ✅ REAL DATA
import { useBalance, useReadContract } from 'wagmi';
import { useQuery } from '@tanstack/react-query';

// Real ETH balance
const { data: ethBalance } = useBalance({ address });

// Real OMK balance
const { data: omkBalance } = useReadContract({
  address: OMK_TOKEN_ADDRESS,
  abi: ERC20_ABI,
  functionName: 'balanceOf',
  args: [address],
});

// Real properties from backend
const { data: properties } = useQuery({
  queryKey: ['properties', address],
  queryFn: async () => {
    const res = await fetch(`/api/v1/properties/user/${address}`);
    return res.json();
  },
});

// Real transactions from backend
const { data: transactions } = useQuery({
  queryKey: ['transactions', address],
  queryFn: async () => {
    const res = await fetch(`/api/v1/transactions/${address}`);
    return res.json();
  },
});

// Calculate REAL portfolio
const ethValue = ethBalance ? parseFloat(ethBalance.formatted) * ethPrice : 0;
const omkValue = omkBalance ? parseFloat(omkBalance) * omkPrice : 0;
const realEstateValue = properties?.reduce((sum, p) => sum + p.value, 0) ?? 0;
const totalValue = ethValue + omkValue + realEstateValue;
```

---

### Fix #2: Invest Page (HIGH)

**Fetch real properties from backend:**

```typescript
// ✅ REAL DATA
const { data: properties, isLoading } = useQuery({
  queryKey: ['properties'],
  queryFn: async () => {
    const res = await fetch('/api/v1/properties');
    return res.json();
  },
});

if (isLoading) return <div>Loading properties...</div>;
if (!properties || properties.length === 0) {
  return <div>No properties available yet</div>;
}
```

---

### Fix #3: Private Investor Card (MEDIUM)

**Use real contract interactions:**

```typescript
// ✅ REAL DATA
const { data: investors } = useReadContract({
  address: PRIVATE_INVESTOR_REGISTRY_ADDRESS,
  abi: PRIVATE_INVESTOR_REGISTRY_ABI,
  functionName: 'getAllInvestors',
});

// ✅ REAL TRANSACTION
const { writeContract } = useWriteContract();

const handleRegisterInvestor = async (data) => {
  await writeContract({
    address: PRIVATE_INVESTOR_REGISTRY_ADDRESS,
    abi: PRIVATE_INVESTOR_REGISTRY_ABI,
    functionName: 'registerInvestor',
    args: [data.wallet, data.allocation, data.amountPaid],
  });
};
```

---

### Fix #4: Price Feeds (LOW)

**Use Chainlink or DEX price:**

```typescript
// ✅ REAL PRICE from Chainlink
const { data: ethPrice } = useReadContract({
  address: CHAINLINK_ETH_USD_ADDRESS,
  abi: CHAINLINK_ABI,
  functionName: 'latestAnswer',
});

// ✅ REAL PRICE from Uniswap
const { data: omkPrice } = useQuery({
  queryKey: ['omkPrice'],
  queryFn: async () => {
    // Fetch from Uniswap V3 pool
    const res = await fetch('/api/v1/price/omk');
    return res.json();
  },
});
```

---

## 🎯 Action Plan

### Phase 1: Stop the Bleeding (Day 1) 🔴
1. ✅ Remove mock data from `DashboardCard.tsx`
2. 🔄 Remove mock data from `dashboard/page.tsx`
3. 🔄 Show "No data yet" states instead of fake data

### Phase 2: Real Data Integration (Week 1) 🟠
1. Deploy OMK ERC20 contract
2. Create backend API endpoints:
   - `GET /api/v1/properties` - List all properties
   - `GET /api/v1/properties/user/:address` - User's properties
   - `GET /api/v1/transactions/:address` - User's transactions
3. Integrate Wagmi hooks for token balances
4. Update dashboard to use real data

### Phase 3: Price Feeds (Week 2) 🟡
1. Integrate Chainlink price oracles
2. Set up price caching
3. Real-time price updates

### Phase 4: Polish (Week 3) 🟢
1. Loading states
2. Error handling
3. Empty states
4. Performance optimization

---

## 📝 Summary

### Total Mock Data Found: **5 locations**

1. ❌ **Dashboard page** - 119 lines of fake data
2. ❌ **Invest page** - 58 lines of fake properties
3. ❌ **Private Investor Card** - 45 lines of fake data
4. ⚠️ **ETH price** - Hardcoded $2,500 (2 locations)
5. ⚠️ **OMK balance** - Hardcoded 0 (1 location)

### Estimated Work:
- **Critical fixes:** 2-3 days
- **High priority:** 1 week
- **Complete cleanup:** 2-3 weeks

---

**Next Step:** Start with `dashboard/page.tsx` - it's the most visible fake data! 🎯
