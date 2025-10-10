# FPRIME-2: Investment & Trading Portals

## 🎯 **Overview**
Investment blocks, public sale, and OTC trading interfaces.

---

## **📋 Features & Tasks**

### **A. INVESTMENT BLOCKS PORTAL**

#### **1. Property Marketplace**
- [ ] Property listing grid/list view
- [ ] Advanced filters (location, APY, price, availability)
- [ ] Sort options (newest, highest APY, lowest price)
- [ ] Search functionality
- [ ] Property detail pages
- [ ] High-quality images gallery
- [ ] Virtual tours integration
- [ ] Location map integration

#### **2. Property Details**
- [ ] Property information (address, size, type)
- [ ] Investment metrics (APY, total value, min investment)
- [ ] Fractional ownership calculator
- [ ] Expected monthly returns
- [ ] Historical performance chart
- [ ] Property documents (prospectus, legal)
- [ ] Risk assessment display
- [ ] Similar properties suggestions

#### **3. Investment Flow**
- [ ] Block selection (quantity)
- [ ] Investment amount calculator
- [ ] Payment method selection (crypto/fiat)
- [ ] Transaction preview
- [ ] Smart contract execution
- [ ] Confirmation screen
- [ ] Receipt generation
- [ ] Email notifications

#### **4. My Investments**
- [ ] Invested properties list
- [ ] Performance tracking
- [ ] Monthly distribution history
- [ ] Appreciation calculator
- [ ] Sell/transfer blocks
- [ ] Download statements

---

### **B. PUBLIC SALE PORTAL**

#### **1. Token Sale Dashboard**
- [ ] Sale progress bar
- [ ] Tokens sold / Total supply
- [ ] Current price tier
- [ ] Next price tier countdown
- [ ] Your contribution tracker
- [ ] Referral bonus display
- [ ] Leaderboard (top buyers)

#### **2. Purchase Interface**
- [ ] Token amount input
- [ ] Payment currency selector (ETH, USDT, USDC, SOL)
- [ ] Dynamic price calculation
- [ ] Bonus tier display
- [ ] Gas estimation
- [ ] Slippage tolerance
- [ ] Buy button with confirmation
- [ ] Transaction status tracking

#### **3. Vesting & Claims**
- [ ] Vesting schedule display
- [ ] Claimable tokens amount
- [ ] Next unlock countdown
- [ ] Claim history
- [ ] One-click claim button
- [ ] Multi-claim (all unlocked)

---

### **C. OTC TRADING PORTAL**

#### **1. OTC Marketplace**
- [ ] Buy/sell orders list
- [ ] Order book display
- [ ] Price chart
- [ ] Trading pairs (OMK/USDT, OMK/ETH)
- [ ] Order type selector (market/limit)
- [ ] Advanced trading view

#### **2. Create Order**
- [ ] Order form (buy/sell)
- [ ] Amount input
- [ ] Price input (for limit orders)
- [ ] Total calculation
- [ ] Fee display
- [ ] Order preview
- [ ] Submit order
- [ ] Order confirmation

#### **3. Order Management**
- [ ] Active orders list
- [ ] Order history
- [ ] Cancel order functionality
- [ ] Edit order (if unfilled)
- [ ] Order status tracking
- [ ] Filled orders archive

#### **4. Trade History**
- [ ] Personal trade history
- [ ] Market trade feed
- [ ] Trade details modal
- [ ] Export to CSV
- [ ] Filter by date/pair
- [ ] P&L calculation

---

## **🎨 UI Components**

### **Pages:**
```
/invest                     - Investment home
/invest/properties          - Property marketplace
/invest/property/[id]       - Property details
/invest/my-investments      - User's investments
/public-sale                - Token sale dashboard
/public-sale/purchase       - Buy tokens
/public-sale/claims         - Vesting & claims
/otc                        - OTC trading
/otc/order/[id]            - Order details
```

### **Components:**
- `PropertyCard` - Property listing card
- `PropertyGallery` - Image slider
- `InvestmentCalculator` - ROI calculator
- `SaleProgress` - Progress indicator
- `PurchaseForm` - Token purchase form
- `VestingSchedule` - Timeline display
- `OrderBook` - Trading book
- `TradingChart` - Price chart
- `OrderForm` - Create order form

---

## **🔧 Technical Implementation**

### **State Management:**
```typescript
// stores/investmentStore.ts
- properties: Property[]
- investments: Investment[]
- filters: PropertyFilters
- selectedProperty: Property | null

// stores/saleStore.ts
- saleInfo: PublicSale
- userContribution: number
- vestingSchedule: VestingPeriod[]
- claimableAmount: number

// stores/otcStore.ts
- orderBook: Order[]
- userOrders: Order[]
- tradeHistory: Trade[]
- selectedPair: TradingPair
```

### **API Endpoints:**
```
GET  /api/v1/properties
GET  /api/v1/properties/:id
POST /api/v1/invest
GET  /api/v1/investments
GET  /api/v1/sale/info
POST /api/v1/sale/purchase
GET  /api/v1/sale/vesting
POST /api/v1/sale/claim
GET  /api/v1/otc/orders
POST /api/v1/otc/order/create
DELETE /api/v1/otc/order/:id
```

### **Smart Contracts:**
```solidity
// InvestmentBlocks.sol
- buyBlocks(propertyId, quantity)
- getPropertyInfo(propertyId)
- getUserInvestments(address)
- claimDistributions()

// PublicSale.sol
- buyTokens(amount)
- claimVestedTokens()
- getVestingSchedule(address)

// OTCMarket.sol
- createOrder(type, amount, price)
- fillOrder(orderId)
- cancelOrder(orderId)
```

---

## **📊 Data Models**

```typescript
interface Property {
  id: string;
  name: string;
  location: string;
  type: 'residential' | 'commercial';
  totalValue: number;
  blockPrice: number;
  totalBlocks: number;
  availableBlocks: number;
  apy: number;
  images: string[];
  description: string;
  amenities: string[];
  documents: Document[];
}

interface Investment {
  id: string;
  propertyId: string;
  blocks: number;
  investmentAmount: number;
  purchaseDate: Date;
  currentValue: number;
  totalReturns: number;
  monthlyIncome: number;
}

interface PublicSale {
  startTime: Date;
  endTime: Date;
  tokenPrice: number;
  totalSupply: number;
  soldAmount: number;
  hardCap: number;
  minPurchase: number;
  maxPurchase: number;
  bonusTiers: BonusTier[];
}

interface Order {
  id: string;
  type: 'buy' | 'sell';
  orderType: 'market' | 'limit';
  pair: string;
  amount: number;
  price: number;
  filled: number;
  status: 'pending' | 'partial' | 'filled' | 'cancelled';
  createdAt: Date;
}
```

---

## **✅ Acceptance Criteria**

### **Investment Blocks:**
1. Users can browse and filter properties
2. Investment calculator works accurately
3. Purchase flow completes successfully
4. Portfolio updates in real-time

### **Public Sale:**
1. Sale progress displays correctly
2. Token purchase with multiple currencies
3. Vesting schedule visible
4. Claim mechanism works

### **OTC:**
1. Order book updates in real-time
2. Orders can be created and cancelled
3. Trade execution works
4. History tracking accurate

---

**Estimated Time:** 3-4 weeks
**Priority:** 🔴 Critical (Revenue Generator)
