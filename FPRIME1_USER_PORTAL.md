# FPRIME-1: User Portal

## 🎯 **Overview**
Core user dashboard for managing crypto & real estate holdings.

---

## **📋 Features & Tasks**

### **1. Authentication & Onboarding**
- [ ] Wallet connection (MetaMask, WalletConnect, Phantom)
- [ ] Email/password signup
- [ ] Social login (Google, Twitter)
- [ ] 2FA setup
- [ ] KYC verification flow
- [ ] Profile setup wizard
- [ ] Terms & conditions acceptance

###

 **2. Dashboard Home**
- [ ] Portfolio overview card
- [ ] Total holdings (crypto + real estate)
- [ ] 24h change indicators
- [ ] Quick actions (buy, sell, swap)
- [ ] Recent transactions list
- [ ] Market overview widget
- [ ] Price charts (OMK token)

### **3. Crypto Holdings**
- [ ] Token balance display
- [ ] Multi-chain support (Ethereum, Solana)
- [ ] Staking dashboard
- [ ] Yield farming positions
- [ ] Transaction history
- [ ] Send/receive tokens
- [ ] Token swap interface

### **4. Real Estate Holdings**
- [ ] Owned property blocks list
- [ ] Property details view
- [ ] Rental income tracker
- [ ] Property value appreciation
- [ ] Monthly distributions
- [ ] Property documents access
- [ ] Fractional ownership percentage

### **5. Wallet Management**
- [ ] Connected wallets display
- [ ] Multi-wallet support
- [ ] Wallet switching
- [ ] Address book
- [ ] Transaction signing
- [ ] Gas optimization

### **6. Profile & Settings**
- [ ] Personal information
- [ ] Notification preferences
- [ ] Security settings
- [ ] Language selection
- [ ] Theme toggle (dark/light)
- [ ] KYC status
- [ ] Referral code

---

## **🎨 UI Components**

### **Pages:**
```
/dashboard          - Main dashboard
/portfolio          - Detailed portfolio
/crypto             - Crypto holdings
/real-estate        - Property holdings
/transactions       - Transaction history
/wallet             - Wallet management
/profile            - User profile
/settings           - Settings
```

### **Components:**
- `DashboardCard` - Summary cards
- `PortfolioChart` - Holdings chart
- `AssetList` - Token/property list
- `TransactionRow` - Transaction display
- `PropertyCard` - Real estate card
- `WalletConnector` - Wallet button
- `KYCBadge` - Verification status

---

## **🔧 Technical Implementation**

### **State Management:**
```typescript
// stores/userStore.ts
- user: UserProfile
- wallets: WalletConnection[]
- portfolio: Portfolio
- transactions: Transaction[]
- kyc: KYCStatus
```

### **API Endpoints:**
```
GET  /api/v1/user/profile
GET  /api/v1/user/portfolio
GET  /api/v1/user/holdings/crypto
GET  /api/v1/user/holdings/real-estate
GET  /api/v1/user/transactions
POST /api/v1/user/kyc/submit
```

### **Smart Contract Calls:**
```solidity
- balanceOf()
- getStakingInfo()
- getPropertyOwnership()
- claimRewards()
```

---

## **📊 Data Models**

```typescript
interface UserProfile {
  id: string;
  email: string;
  walletAddress: string;
  kycStatus: 'pending' | 'verified' | 'rejected';
  tier: 'basic' | 'premium' | 'institutional';
  createdAt: Date;
}

interface Portfolio {
  totalValue: number;
  cryptoValue: number;
  realEstateValue: number;
  change24h: number;
  holdings: Holding[];
}

interface Holding {
  type: 'crypto' | 'real-estate';
  asset: string;
  amount: number;
  value: number;
  change24h: number;
}
```

---

## **✅ Acceptance Criteria**

1. User can connect wallet and create account
2. Dashboard displays accurate portfolio data
3. Real-time price updates
4. Transaction history loads correctly
5. KYC flow completes successfully
6. Responsive on mobile
7. Loading states for async operations
8. Error handling for failed transactions

---

**Estimated Time:** 2-3 weeks
**Priority:** 🔴 Critical (Foundation)
