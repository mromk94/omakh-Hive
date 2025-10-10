# FPRIME-10: Token Acquisition & Investment Flow

## 🎯 **Overview**
Complete end-to-end user journey from wallet connection to property investment, including token acquisition, swapping, and investment block purchasing.

---

## **📋 Complete User Journey**

### **Journey Map:**
```
1. Land on Platform
   ↓
2. Connect Wallet (FPRIME-8)
   ↓
3. Learn about Platform (FPRIME-9 if needed)
   ↓
4. Get OMK Tokens (THIS)
   ↓
5. Explore Properties (THIS)
   ↓
6. Invest in Blocks (THIS)
   ↓
7. Track Returns (FPRIME-1)
```

---

## **🎯 Features & Tasks**

### **PART 1: Token Acquisition Flow**

#### **A. Entry Points for "Get OMK"**

**Multiple entry points throughout platform:**
- [ ] Homepage: "Buy OMK" CTA
- [ ] Navigation: "Get OMK" menu item
- [ ] Dashboard: "Buy OMK" card
- [ ] Property page: "Need OMK?" banner
- [ ] Empty wallet state: "Get OMK to invest"

#### **B. Pre-Purchase Check**

When user clicks "Get OMK":
```
┌─────────────────────────────────────────┐
│  💎 Get OMK Tokens                      │
│                                         │
│  OMK Token Powers:                      │
│  ✓ Real estate investments             │
│  ✓ Property block purchases            │
│  ✓ Governance voting                   │
│  ✓ Platform benefits                   │
│                                         │
│  Current Price: 1 OMK = $0.10         │
│                                         │
│  Do you have crypto (ETH/SOL)?         │
│                                         │
│  [✅ Yes, I have crypto]               │
│  [📚 No, help me get some]             │
└─────────────────────────────────────────┘
```

#### **C. Token Purchase Interface**

**Main Purchase Screen:**
```
┌──────────────────────────────────────────────┐
│  💰 Buy OMK Tokens                           │
├──────────────────────────────────────────────┤
│                                              │
│  You Pay:                                    │
│  ┌──────────────────────────────────────┐   │
│  │ 0.1        [ETH ▼]        [MAX]      │   │
│  └──────────────────────────────────────┘   │
│  ≈ $250.00 USD                              │
│                                              │
│              ↓↓↓                             │
│                                              │
│  You Receive:                                │
│  ┌──────────────────────────────────────┐   │
│  │ 2,500      OMK                       │   │
│  └──────────────────────────────────────┘   │
│  ≈ $250.00 USD                              │
│                                              │
│  Price: 1 OMK = $0.10                       │
│  Network Fee: ~$5.00                        │
│  Slippage: 1%                               │
│                                              │
│  [⚙️ Advanced Settings]                     │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │        [Swap Now]                    │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  Payment Options:                            │
│  [💳 Card] [🏦 Bank] [💎 Crypto]            │
└──────────────────────────────────────────────┘
```

#### **D. Payment Method Options**

**Option 1: Crypto Swap (Fastest)**
```typescript
// Direct swap from user's wallet
ETH → OMK
SOL → OMK
USDT → OMK
USDC → OMK
```

**Features:**
- [ ] Token selector dropdown
- [ ] Real-time price quotes
- [ ] Slippage tolerance settings
- [ ] Gas estimation
- [ ] MEV protection
- [ ] Transaction simulation

**Option 2: Credit/Debit Card**
```typescript
// On-ramp via MoonPay/Wyre
USD → ETH → OMK (automatic)
```

**Features:**
- [ ] Card input form
- [ ] 3D Secure verification
- [ ] Purchase limits display
- [ ] KYC for large amounts
- [ ] Instant delivery

**Option 3: Bank Transfer**
```typescript
// ACH/SEPA transfer
USD/EUR → USDC → OMK
```

**Features:**
- [ ] Bank account linking
- [ ] Transfer instructions
- [ ] 1-3 day processing
- [ ] No fees for large amounts

---

### **PART 2: Smart Swap Integration**

#### **A. DEX Aggregator**

**Check multiple DEXs for best price:**
```
Checking prices across:
✓ Uniswap
✓ SushiSwap  
✓ PancakeSwap
✓ 1inch
✓ Jupiter (Solana)

Best price: Uniswap
You save: $2.50 (1.2%)
```

#### **B. Transaction Preview**

```
┌──────────────────────────────────────────┐
│  📝 Review Transaction                   │
├──────────────────────────────────────────┤
│                                          │
│  You're swapping:                        │
│  • 0.1 ETH ($250.00)                    │
│  →                                       │
│  • 2,500 OMK ($250.00)                  │
│                                          │
│  Route: ETH → WETH → OMK                │
│  Via: Uniswap V3                        │
│                                          │
│  Price Impact: 0.12% ✅                 │
│  Minimum Received: 2,475 OMK            │
│  Network Fee: $4.82                     │
│                                          │
│  ⚠️ You will need to approve 2 txns:    │
│  1. Approve ETH spending                 │
│  2. Execute swap                         │
│                                          │
│  [←  Back]          [Confirm Swap →]    │
└──────────────────────────────────────────┘
```

#### **C. Transaction Execution**

**Step-by-step UI:**
```
┌──────────────────────────────────────────┐
│  🔄 Swapping Tokens                      │
├──────────────────────────────────────────┤
│                                          │
│  ✅ Step 1: Approve ETH                 │
│     Waiting for confirmation...          │
│     [Tx: 0x1234...] [View on Etherscan]│
│                                          │
│  ⏳ Step 2: Execute Swap                │
│     Sign in your wallet...               │
│                                          │
│  ⏸️  Step 3: Confirmation                │
│     Pending...                           │
│                                          │
│  [ℹ️] This may take 15-60 seconds       │
└──────────────────────────────────────────┘
```

#### **D. Success Screen**

```
┌──────────────────────────────────────────┐
│  🎉 Swap Successful!                     │
├──────────────────────────────────────────┤
│                                          │
│       💎 → 🟡                            │
│                                          │
│  You received:                           │
│  2,503 OMK ($250.30)                    │
│                                          │
│  Tx: 0x1234...5678                       │
│  [View on Explorer]                      │
│                                          │
│  ✨ Bonus: +3 OMK ($0.30)               │
│  (First-time buyer bonus!)               │
│                                          │
│  What's next?                            │
│  [📊 View in Portfolio]                 │
│  [🏠 Invest in Properties]              │
│  [💰 Buy More OMK]                      │
└──────────────────────────────────────────┘
```

---

### **PART 3: Property Investment Flow**

#### **A. Property Discovery**

**Browse Interface:**
```
┌────────────────────────────────────────────┐
│  🏠 Investment Properties                  │
├────────────────────────────────────────────┤
│                                            │
│  [🔍 Search] [📍 Location] [💰 Price]     │
│  [📊 Sort: Highest APY ▼]                 │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │ 🏢 Luxury Apartment - Dubai          │ │
│  │                                      │ │
│  │ [Property Image]                     │ │
│  │                                      │ │
│  │ 📍 Dubai Marina                      │ │
│  │ 💰 Block Price: $100                 │ │
│  │ 📈 APY: 12%                          │ │
│  │ ⏱️  Monthly: 1%                       │ │
│  │ 🎯 Available: 450/1000 blocks        │ │
│  │                                      │ │
│  │ [View Details]                       │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  [More Properties...]                     │
└────────────────────────────────────────────┘
```

#### **B. Property Detail Page**

```
┌─────────────────────────────────────────────┐
│  Luxury Apartment - Dubai Marina           │
├─────────────────────────────────────────────┤
│                                             │
│  [Image Gallery - Swipeable]               │
│                                             │
│  📊 Investment Details:                     │
│  ├─ Total Value: $100,000                  │
│  ├─ Block Price: $100                      │
│  ├─ Total Blocks: 1,000                    │
│  ├─ Available: 450                         │
│  ├─ Min Investment: 1 block ($100)         │
│  └─ Max Investment: 50 blocks ($5,000)     │
│                                             │
│  💰 Returns:                                │
│  ├─ APY: 12%                                │
│  ├─ Monthly: 1%                             │
│  ├─ Quarterly: 3%                           │
│  └─ Distribution: Monthly                   │
│                                             │
│  📍 Location:                               │
│  Dubai Marina, Dubai, UAE                   │
│  [View on Map]                              │
│                                             │
│  🏢 Property Info:                          │
│  ├─ Type: Residential Apartment            │
│  ├─ Size: 1,200 sq ft                      │
│  ├─ Bedrooms: 2                             │
│  ├─ Status: Fully Rented                   │
│  └─ Built: 2022                             │
│                                             │
│  📄 Documents:                              │
│  [📋 Prospectus] [⚖️ Legal] [📊 Financials]│
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │  💡 Investment Calculator              │ │
│  │                                        │ │
│  │  Blocks: [10]        ($1,000)         │ │
│  │                                        │ │
│  │  Expected Returns:                     │ │
│  │  Monthly: $10                          │ │
│  │  Yearly: $120                          │ │
│  │                                        │ │
│  │  [Calculate]                           │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  [← Back to Properties]  [Invest Now →]    │
└─────────────────────────────────────────────┘
```

#### **C. Investment Calculator Widget**

**Interactive calculator:**
```typescript
<InvestmentCalculator 
  blockPrice={100}
  apy={12}
  onChange={(blocks) => calculateReturns(blocks)}
/>
```

**Display:**
```
┌──────────────────────────────────────┐
│  💡 Calculate Your Returns           │
├──────────────────────────────────────┤
│                                      │
│  Number of Blocks:                   │
│  ┌────────────────────────────────┐ │
│  │  [━━━━━━━━━●━━━━]  10 blocks  │ │
│  └────────────────────────────────┘ │
│                                      │
│  Investment: $1,000                  │
│                                      │
│  Expected Returns:                   │
│  ├─ Daily:    $0.33                 │
│  ├─ Monthly:  $10.00                │
│  ├─ Yearly:   $120.00               │
│  └─ 5 Years:  $600.00               │
│                                      │
│  Plus Property Appreciation! 📈      │
│  Estimated: +5-10% per year         │
│                                      │
│  [Invest This Amount]                │
└──────────────────────────────────────┘
```

#### **D. Investment Execution**

**Step 1: Review Investment**
```
┌──────────────────────────────────────────┐
│  📝 Review Your Investment               │
├──────────────────────────────────────────┤
│                                          │
│  Property:                               │
│  Luxury Apartment - Dubai Marina         │
│                                          │
│  Investment:                             │
│  • 10 blocks × $100 = $1,000            │
│  • Platform fee: $10 (1%)               │
│  • Total: 1,010 OMK                     │
│                                          │
│  Your Balance: 2,503 OMK ✅             │
│                                          │
│  Expected Returns:                       │
│  • Monthly: $10 (1%)                    │
│  • Yearly: $120 (12% APY)               │
│                                          │
│  Distribution:                           │
│  • First payout: Dec 15, 2024           │
│  • Frequency: Monthly                    │
│  • Method: Auto to wallet               │
│                                          │
│  [☑️] I understand this is an investment│
│       and returns may vary               │
│                                          │
│  [←  Back]          [Confirm Investment]│
└──────────────────────────────────────────┘
```

**Step 2: Wallet Approval**
```
┌──────────────────────────────────────────┐
│  🔐 Approve Transaction                  │
├──────────────────────────────────────────┤
│                                          │
│  Please approve in your wallet:          │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  MetaMask Notification             │ │
│  │                                    │ │
│  │  Omakh Platform                    │ │
│  │  wants to:                         │ │
│  │                                    │ │
│  │  Spend 1,010 OMK                   │ │
│  │  Gas Fee: $2.50                    │ │
│  │                                    │ │
│  │  [Reject]      [Confirm]           │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ⏳ Waiting for confirmation...          │
└──────────────────────────────────────────┘
```

**Step 3: Processing**
```
┌──────────────────────────────────────────┐
│  ⏳ Processing Investment                │
├──────────────────────────────────────────┤
│                                          │
│  ✅ Transaction submitted                │
│  ⏳ Confirming on blockchain...          │
│  ⏸️  Minting ownership NFT...            │
│  ⏸️  Updating portfolio...               │
│                                          │
│  Tx: 0xabcd...1234                       │
│  [View on Explorer]                      │
│                                          │
│  This may take 30-60 seconds...          │
└──────────────────────────────────────────┘
```

**Step 4: Success!**
```
┌──────────────────────────────────────────┐
│  🎉 Investment Successful!               │
├──────────────────────────────────────────┤
│                                          │
│  Congratulations! You now own:           │
│                                          │
│      🏠 10 Blocks                        │
│  Luxury Apartment - Dubai Marina         │
│                                          │
│  💰 Your Investment:                     │
│  • Amount: $1,000                        │
│  • Expected Monthly: $10                 │
│  • Expected Yearly: $120                 │
│  • First Payout: Dec 15, 2024           │
│                                          │
│  📜 Ownership NFT:                       │
│  NFT #1234 minted to your wallet         │
│  [View NFT]                              │
│                                          │
│  📊 What's Next?                         │
│  [View My Portfolio]                     │
│  [Invest in More Properties]            │
│  [Share My Investment 📱]                │
│                                          │
│  📧 Confirmation sent to your email      │
└──────────────────────────────────────────┘
```

---

### **PART 4: Post-Investment Experience**

#### **A. Portfolio Dashboard**

```
┌──────────────────────────────────────────┐
│  📊 My Real Estate Portfolio             │
├──────────────────────────────────────────┤
│                                          │
│  Total Invested: $1,000                  │
│  Current Value: $1,015                   │
│  Total Returns: $15 (+1.5%)              │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  🏢 Luxury Apartment - Dubai       │ │
│  │                                    │ │
│  │  Blocks: 10                        │ │
│  │  Value: $1,015                     │ │
│  │  Monthly Income: $10               │ │
│  │  Total Earned: $15                 │ │
│  │  Next Payout: 12 days              │ │
│  │                                    │ │
│  │  [View Details] [Sell Blocks]      │ │
│  └────────────────────────────────────┘ │
│                                          │
│  [+ Invest in More Properties]           │
└──────────────────────────────────────────┘
```

#### **B. Distribution Tracking**

```
┌──────────────────────────────────────────┐
│  💰 Income History                       │
├──────────────────────────────────────────┤
│                                          │
│  Nov 2024:  $10.00  ✅ Paid             │
│  Dec 2024:  $10.00  ⏳ Pending (12 days)│
│  Jan 2025:  $10.00  ⏸️  Scheduled        │
│                                          │
│  Total Earned: $15                       │
│  [Download Statement]                    │
└──────────────────────────────────────────┘
```

---

## **🔧 Technical Implementation**

### **Smart Contracts:**

```solidity
// TokenSwap.sol
contract TokenSwap {
    function swapETHForOMK(uint minOMKOut) external payable;
    function swapTokenForOMK(address token, uint amount) external;
}

// InvestmentBlocks.sol
contract InvestmentBlocks {
    function buyBlocks(
        uint256 propertyId, 
        uint256 quantity
    ) external;
    
    function getBlockOwnership(address owner) 
        external view returns (Block[] memory);
    
    function claimDistribution(uint256 blockId) external;
}

// OwnershipNFT.sol (ERC-721)
contract PropertyOwnershipNFT {
    function mintOwnership(
        address to,
        uint256 propertyId,
        uint256 blocks
    ) external returns (uint256 tokenId);
}
```

### **API Endpoints:**

```typescript
// Token purchase
POST /api/v1/tokens/quote          // Get swap quote
POST /api/v1/tokens/swap            // Execute swap
GET  /api/v1/tokens/balance         // Get user balance

// Property investment
GET  /api/v1/properties             // List properties
GET  /api/v1/properties/:id         // Property details
POST /api/v1/properties/:id/invest  // Invest in property
GET  /api/v1/investments            // User's investments
GET  /api/v1/distributions          // Distribution history
POST /api/v1/distributions/claim    // Claim distribution
```

---

## **✅ Acceptance Criteria**

1. ✅ User can swap crypto for OMK
2. ✅ Multiple payment methods work
3. ✅ Best price found across DEXs
4. ✅ Transaction preview accurate
5. ✅ Property discovery functional
6. ✅ Investment calculator works
7. ✅ Investment execution smooth
8. ✅ Ownership NFT minted
9. ✅ Portfolio updates in real-time
10. ✅ Distributions tracked accurately

---

**Estimated Time:** 3-4 weeks
**Priority:** 🔴 CRITICAL (Core Revenue Flow)

**Dependencies:**
- FPRIME-8 (Wallet connection)
- FPRIME-9 (Education system)
- DEX aggregator API
- Smart contracts deployed
- Payment gateway integration
