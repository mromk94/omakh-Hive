# FPRIME-8: Authentication & Web3 Connectivity

## 🎯 **Overview**
Comprehensive authentication system with Web3-first approach, supporting both wallet and traditional login methods.

---

## **📋 Features & Tasks**

### **1. Landing & Entry Point**

#### **Initial Screen:**
- [ ] "Connect to Omakh" hero section
- [ ] "Get Started" primary CTA
- [ ] "Do you have a crypto wallet?" decision point
- [ ] Clear value proposition display
- [ ] Platform benefits showcase

#### **Decision Flow:**
```
User arrives → "Do you have a crypto wallet?"
                    ↓                      ↓
                  YES                     NO
                    ↓                      ↓
            Choose Chain            Learn & Setup
         (ETH / SOL / Both)      (Guided Tutorial)
                    ↓                      ↓
           Wallet Connect           Download Wallet
                    ↓                      ↓
              Connected!            Return to Connect
```

---

### **2. Web3 Wallet Connection (YES Path)**

#### **A. Chain Selection Interface**
- [ ] ETH button with info icon
- [ ] SOL button with info icon
- [ ] "Connect Both" option
- [ ] Info bubbles on hover/click

**ETH Info Bubble:**
```
"Ethereum Network
- Most established DeFi ecosystem
- Wide wallet support (MetaMask, Coinbase, etc.)
- Higher gas fees but more liquidity
- Recommended for large investments
[Learn More →]"
```

**SOL Info Bubble:**
```
"Solana Network
- Lightning-fast transactions
- Very low fees (< $0.01)
- Growing DeFi ecosystem
- Recommended for smaller/frequent trades
[Learn More →]"
```

#### **B. Wallet Connect Integration**
- [ ] WalletConnect v2 integration
- [ ] QR code display for mobile
- [ ] Deep linking for mobile wallets
- [ ] Desktop extension detection
- [ ] Mobile-optimized UI

**Supported Wallets:**
- **Ethereum:** MetaMask, Coinbase Wallet, Trust Wallet, Rainbow, Ledger
- **Solana:** Phantom, Solflare, Backpack, Ledger
- **Universal:** WalletConnect-compatible wallets

#### **C. Connection Flow:**
```typescript
1. User clicks "Connect Wallet"
2. Chain selection modal appears
3. User selects ETH/SOL/Both
4. Wallet list displays
5. User selects wallet
6. Wallet prompts for connection
7. User approves in wallet
8. Signature request (for authentication)
9. Connection established
10. Balance fetched
11. Profile created/loaded
```

#### **D. Multi-Wallet Support**
- [ ] Connect multiple wallets
- [ ] Primary wallet designation
- [ ] Switch between wallets
- [ ] Wallet nicknames
- [ ] Remove wallet connection

---

### **3. Balance Display System**

#### **A. Floating Balance Bubble**
**Position:** Top-center of screen (or top-right)
**Design:**
```
┌─────────────────────────────────┐
│  💎 0.5 ETH ≈ $1,250           │
│  🟡 1,000 OMK ≈ $100            │
│  [⚙️] [🔄] [👤]                 │
└─────────────────────────────────┘
```

**Features:**
- [ ] Live balance updates
- [ ] USD conversion
- [ ] Multiple token display
- [ ] Expandable on click
- [ ] Network indicator
- [ ] Quick actions (swap, send)

**Behavior:**
- Floats at top of screen (z-index: 100)
- Pushes menu button down below it
- Collapsible to icon only
- Sticky on scroll
- Smooth animations

#### **B. Balance Details (Expanded View)**
```
┌──────────────────────────────────────┐
│  Connected: 0x1234...5678           │
│  Network: Ethereum Mainnet          │
│                                      │
│  Balances:                          │
│  💎 ETH     0.5000    $1,250       │
│  🟡 OMK     1,000     $100          │
│  💵 USDT    500       $500          │
│  💵 USDC    300       $300          │
│                                      │
│  Total Portfolio: $2,150            │
│                                      │
│  [Deposit] [Swap] [Send] [More]    │
└──────────────────────────────────────┘
```

#### **C. Menu Button Repositioning**
- Current position: `fixed top-6 right-6`
- New position when balance shown: `fixed top-20 right-6`
- Smooth transition animation
- Maintains functionality

---

### **4. Traditional Auth (NO Path - Alternative)**

#### **Email/Social Login:**
- [ ] Email + password
- [ ] Google OAuth
- [ ] Twitter/X OAuth
- [ ] Apple Sign In
- [ ] Phone number (SMS)

**Note:** Even traditional users should be encouraged to create a wallet later for full platform access.

---

### **5. Security & Verification**

#### **A. Signature Authentication**
```typescript
// User signs a message to prove wallet ownership
const message = `Welcome to Omakh!

Sign this message to authenticate.
This won't cost gas.

Nonce: ${nonce}
Timestamp: ${timestamp}`;

const signature = await signer.signMessage(message);
```

#### **B. Session Management**
- [ ] JWT token generation
- [ ] Refresh token mechanism
- [ ] Session expiry (24 hours)
- [ ] Auto-reconnect on page load
- [ ] Remember me option

#### **C. Security Features**
- [ ] Anti-phishing code display
- [ ] Transaction simulation
- [ ] Spending limits
- [ ] Suspicious activity detection
- [ ] 2FA for sensitive operations

---

### **6. Onboarding After Connection**

#### **First-Time User Flow:**
```
1. Welcome modal
2. Quick platform tour (optional)
3. Set profile preferences
4. Enable notifications
5. Set up 2FA (recommended)
6. Complete KYC (for large investments)
7. Explore dashboard
```

#### **Welcome Modal:**
```
┌─────────────────────────────────────────┐
│  🎉 Welcome to Omakh!                   │
│                                         │
│  You're connected with:                 │
│  0x1234...5678                          │
│                                         │
│  Get started with:                      │
│  ✓ Browse Properties                    │
│  ✓ Buy OMK Tokens                      │
│  ✓ Start Earning Passive Income        │
│                                         │
│  [Take a Quick Tour] [Skip to Dashboard]│
└─────────────────────────────────────────┘
```

---

## **🎨 UI Components**

### **Pages:**
```
/connect                   - Main connect page
/connect/wallet            - Wallet selection
/connect/email             - Email signup
/connect/learn             - Learn about wallets
/auth/callback             - OAuth callback
```

### **Components:**
```typescript
// WalletConnect Button
<WalletConnectButton 
  chains={['ethereum', 'solana']}
  onConnect={(wallet) => handleConnect(wallet)}
/>

// Balance Bubble
<BalanceBubble 
  wallets={connectedWallets}
  position="top-center"
  collapsible
/>

// Chain Selector
<ChainSelector 
  onSelect={(chain) => setSelectedChain(chain)}
  showInfo
/>

// Info Bubble
<InfoBubble 
  title="Ethereum Network"
  content={ethInfo}
  trigger="hover"
/>

// Wallet List
<WalletList 
  chain={selectedChain}
  onSelect={(wallet) => connectWallet(wallet)}
/>
```

---

## **🔧 Technical Implementation**

### **State Management:**
```typescript
// stores/authStore.ts
interface AuthState {
  isConnected: boolean;
  primaryWallet: Wallet | null;
  connectedWallets: Wallet[];
  balances: Record<string, Balance>;
  user: UserProfile | null;
  sessionToken: string | null;
}

// stores/walletStore.ts
interface WalletState {
  selectedChain: 'ethereum' | 'solana' | 'both';
  provider: any;
  signer: any;
  address: string | null;
  networkId: number | null;
}
```

### **Web3 Integration:**

**Ethereum (Wagmi + Viem):**
```typescript
import { WagmiConfig, createConfig } from 'wagmi';
import { mainnet, sepolia } from 'wagmi/chains';
import { createPublicClient, http } from 'viem';

const config = createConfig({
  chains: [mainnet, sepolia],
  transports: {
    [mainnet.id]: http(),
    [sepolia.id]: http(),
  },
});
```

**Solana:**
```typescript
import { useWallet } from '@solana/wallet-adapter-react';
import { WalletModalProvider } from '@solana/wallet-adapter-react-ui';

const { 
  publicKey, 
  connected, 
  connect, 
  disconnect 
} = useWallet();
```

**Multi-Chain Abstraction:**
```typescript
// lib/web3/connector.ts
class MultiChainConnector {
  async connect(chain: 'ethereum' | 'solana') {
    if (chain === 'ethereum') {
      return this.connectEthereum();
    } else {
      return this.connectSolana();
    }
  }
  
  async getBalance(address: string, chain: string) {
    // Fetch balance for specific chain
  }
  
  async signMessage(message: string, chain: string) {
    // Sign message on specific chain
  }
}
```

---

## **📊 Data Models**

```typescript
interface Wallet {
  id: string;
  address: string;
  chain: 'ethereum' | 'solana';
  type: 'metamask' | 'phantom' | 'walletconnect' | string;
  nickname?: string;
  isPrimary: boolean;
  connectedAt: Date;
}

interface Balance {
  token: string;
  symbol: string;
  amount: number;
  decimals: number;
  usdValue: number;
  chain: string;
}

interface ConnectionSession {
  userId: string;
  walletAddress: string;
  sessionToken: string;
  expiresAt: Date;
  device: string;
  ipAddress: string;
}
```

---

## **🔐 Security Considerations**

### **1. Anti-Phishing:**
- Display user's anti-phishing code
- Verify contract addresses
- Warn about suspicious transactions

### **2. Transaction Safety:**
- Simulate transactions before signing
- Display clear transaction details
- Gas estimation
- Slippage protection

### **3. Session Security:**
- Encrypted session storage
- Auto-logout on inactivity
- Detect wallet changes
- IP verification

---

## **📱 Mobile Optimization**

### **Mobile-Specific Features:**
- [ ] Deep linking to mobile wallets
- [ ] QR code scanning
- [ ] Touch-optimized buttons
- [ ] Simplified balance view
- [ ] Swipe gestures
- [ ] Bottom sheet modals

### **WalletConnect Mobile Flow:**
```
1. User clicks "Connect Wallet"
2. QR code displayed
3. User scans with wallet app
4. Wallet app prompts approval
5. User approves
6. Connection established
7. Redirected back to Omakh
```

---

## **✅ Acceptance Criteria**

1. ✅ User can connect Ethereum wallet
2. ✅ User can connect Solana wallet
3. ✅ User can connect both chains
4. ✅ Balance displays correctly
5. ✅ Balance bubble floats at top
6. ✅ Menu button repositions when balance shown
7. ✅ Info bubbles work on ETH/SOL buttons
8. ✅ WalletConnect works on mobile
9. ✅ Session persists across page reloads
10. ✅ Multi-wallet support functional
11. ✅ Security features operational

---

## **🧪 Testing Checklist**

- [ ] Test MetaMask connection
- [ ] Test Phantom connection
- [ ] Test WalletConnect with mobile wallet
- [ ] Test balance updates
- [ ] Test chain switching
- [ ] Test multi-wallet connection
- [ ] Test session persistence
- [ ] Test on mobile devices
- [ ] Test disconnection flow
- [ ] Test error scenarios (rejected connection, etc.)

---

**Estimated Time:** 2 weeks
**Priority:** 🔴 CRITICAL (Foundation for Web3 features)

**Dependencies:**
- Wagmi/Viem setup
- Solana wallet adapter
- WalletConnect v2
- Backend authentication API
