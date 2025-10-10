# 🗺️ FPRIME Complete Roadmap

## 📊 **Phase Timeline & Priority**

```
┌─────────────────────────────────────────────────────────────────┐
│  MONTH 1-2    │  MONTH 2-3    │  MONTH 3-4    │  MONTH 4-5      │
├───────────────┼───────────────┼───────────────┼─────────────────┤
│ FPRIME-1      │ FPRIME-2      │ FPRIME-7      │ FPRIME-4        │
│ User Portal   │ Investment    │ Admin Portal  │ Governance      │
│ ⏱️ 2-3 weeks  │ ⏱️ 3-4 weeks  │ ⏱️ 3-4 weeks  │ ⏱️ 2-3 weeks    │
│ 🔴 CRITICAL   │ 🔴 CRITICAL   │ 🔴 CRITICAL   │ 🟡 HIGH         │
├───────────────┴───────────────┴───────────────┴─────────────────┤
│  MONTH 3-4    │  MONTH 4      │  MONTH 4-5                      │
├───────────────┼───────────────┼─────────────────────────────────┤
│ FPRIME-3      │ FPRIME-5      │ FPRIME-6                        │
│ Presale       │ Partners      │ Institutional                   │
│ ⏱️ 2 weeks    │ ⏱️ 3 weeks    │ ⏱️ 2 weeks                      │
│ 🟡 HIGH       │ 🟢 MEDIUM     │ 🟢 MEDIUM                       │
└───────────────┴───────────────┴─────────────────────────────────┘
```

**Total Duration:** 18-22 weeks (4.5-5.5 months)

---

## 🎯 **Phase Details**

### **FPRIME-1: User Portal** 🔴 CRITICAL
**Week 1-3**
- Foundation for all other portals
- User authentication & wallet connection
- Portfolio dashboard (crypto + real estate)
- Transaction history
- Profile & settings

**Key Deliverables:**
- User registration/login
- Wallet integration (MetaMask, WalletConnect, Phantom)
- Portfolio dashboard
- KYC flow

---

### **FPRIME-2: Investment & Trading** 🔴 CRITICAL
**Week 4-7**
- Investment Blocks Marketplace
- Public Token Sale
- OTC Trading Platform

**Key Deliverables:**
- Property browsing & filtering
- Investment flow (buy blocks)
- Token purchase interface
- OTC order book & trading

---

### **FPRIME-7: Admin Portal** 🔴 CRITICAL
**Week 8-11**
- Platform management & control
- User & property administration
- Financial oversight
- Support ticketing

**Key Deliverables:**
- Admin dashboard
- User management (KYC approval)
- Property approval workflow
- Analytics & reports

---

### **FPRIME-4: Governance** 🟡 HIGH
**Week 12-14**
- DAO governance system
- Proposal creation & voting
- Treasury management

**Key Deliverables:**
- Proposal interface
- Voting mechanism
- Delegation system
- Treasury dashboard

---

### **FPRIME-3: Presale & Airdrops** 🟡 HIGH
**Week 10-12** (Can run parallel)
- Private sale portal
- Airdrop campaigns
- Referral system

**Key Deliverables:**
- Whitelist management
- Contribution interface
- Airdrop claim mechanism
- Referral tracking

---

### **FPRIME-5: Partners Portal** 🟢 MEDIUM
**Week 15-17**
- Real estate partner dashboard
- Property listing management
- Revenue tracking

**Key Deliverables:**
- Partner dashboard
- Property upload/edit
- Revenue analytics
- Investor relations

---

### **FPRIME-6: Institutional Investors** 🟢 MEDIUM
**Week 18-20**
- Advanced analytics
- Bulk investment tools
- API access

**Key Deliverables:**
- Institutional dashboard
- Advanced reporting
- API integration
- Compliance tools

---

## 🎨 **Design System**

### **Color Palette:**
```css
/* Primary */
--black: #000000;
--near-black: #0A0A0A;

/* Gold Gradients */
--gold-primary: #FFD700;
--gold-secondary: #F5A623;
--gold-tertiary: #D4AF37;
--amber: #FFA500;

/* Text */
--text-primary: #E7E5E4;    /* Stone-200 */
--text-secondary: #D6D3D1;  /* Stone-300 */
--text-muted: #A8A29E;      /* Stone-400 */

/* Backgrounds */
--bg-card: #1A1A1A;
--bg-hover: #2A2A2A;
--bg-input: #141414;

/* Borders */
--border: rgba(255, 215, 0, 0.2);
--border-hover: rgba(255, 215, 0, 0.4);
```

### **Typography:**
```css
/* Headings */
font-family: 'Inter', 'SF Pro Display', -apple-system, sans-serif;
font-weight: 700-900 (bold-black);

/* Body */
font-family: 'Inter', -apple-system, sans-serif;
font-weight: 400-600;

/* Size Scale */
text-xs: 0.75rem;
text-sm: 0.875rem;
text-base: 1rem;
text-lg: 1.125rem;
text-xl: 1.25rem;
text-2xl: 1.5rem;
text-3xl: 1.875rem;
text-4xl: 2.25rem;
```

### **Components Library:**
Use **Shadcn/UI** components styled with luxury theme:
- Button (gold gradient primary, outline secondary)
- Card (black bg with gold border)
- Table (dark with gold accents)
- Form (gold focus states)
- Modal/Dialog (dark overlay, gold borders)
- Charts (Recharts with gold theme)

---

## 🏗️ **Tech Stack**

### **Frontend:**
```json
{
  "framework": "Next.js 14 (App Router)",
  "language": "TypeScript",
  "styling": "TailwindCSS",
  "ui": "Shadcn/UI",
  "animation": "Framer Motion",
  "icons": "Lucide React",
  "state": "Zustand",
  "forms": "React Hook Form + Zod",
  "charts": "Recharts",
  "tables": "TanStack Table"
}
```

### **Web3:**
```json
{
  "wallet": "RainbowKit / ConnectKit",
  "ethereum": "Wagmi + Viem",
  "solana": "@solana/wallet-adapter",
  "signing": "ethers.js / @solana/web3.js"
}
```

### **Backend Integration:**
```json
{
  "api": "Queen AI (localhost:8001)",
  "http": "Axios / Fetch",
  "realtime": "WebSocket (future)",
  "storage": "IPFS (documents)"
}
```

---

## 📁 **Project Structure**

```
omk-frontend/
├── app/
│   ├── (auth)/              # Authentication pages
│   │   ├── login/
│   │   └── register/
│   ├── (user)/              # FPRIME-1
│   │   ├── dashboard/
│   │   ├── portfolio/
│   │   ├── crypto/
│   │   └── real-estate/
│   ├── (invest)/            # FPRIME-2
│   │   ├── properties/
│   │   ├── public-sale/
│   │   └── otc/
│   ├── (presale)/           # FPRIME-3
│   │   ├── private-sale/
│   │   └── airdrop/
│   ├── (governance)/        # FPRIME-4
│   │   ├── proposals/
│   │   └── treasury/
│   ├── (partners)/          # FPRIME-5
│   │   └── dashboard/
│   ├── (institutional)/     # FPRIME-6
│   │   └── dashboard/
│   └── (admin)/             # FPRIME-7
│       ├── dashboard/
│       ├── users/
│       └── properties/
├── components/
│   ├── ui/                  # Shadcn components
│   ├── shared/              # Shared components
│   ├── charts/              # Chart components
│   └── web3/                # Wallet connectors
├── lib/
│   ├── api/                 # API clients
│   ├── contracts/           # Smart contract ABIs
│   └── utils/               # Utilities
├── hooks/                   # Custom hooks
├── stores/                  # Zustand stores
├── styles/                  # Global styles
└── types/                   # TypeScript types
```

---

## 🔌 **API Integration Strategy**

### **Queen AI Backend:**
```typescript
// lib/api/queen.ts
const QUEEN_API = 'http://localhost:8001/api/v1';

export const queenApi = {
  // User endpoints
  getProfile: () => axios.get(`${QUEEN_API}/user/profile`),
  getPortfolio: () => axios.get(`${QUEEN_API}/user/portfolio`),
  
  // Investment endpoints
  getProperties: () => axios.get(`${QUEEN_API}/properties`),
  investInProperty: (data) => axios.post(`${QUEEN_API}/invest`, data),
  
  // Governance endpoints
  getProposals: () => axios.get(`${QUEEN_API}/governance/proposals`),
  vote: (data) => axios.post(`${QUEEN_API}/governance/vote`, data),
  
  // Admin endpoints
  adminGetUsers: () => axios.get(`${QUEEN_API}/admin/users`),
  adminApproveKYC: (userId) => axios.post(`${QUEEN_API}/admin/users/${userId}/verify`),
};
```

### **Smart Contracts:**
```typescript
// lib/contracts/index.ts
import { Contract } from 'ethers';

export const contracts = {
  // Investment Blocks
  investmentBlocks: new Contract(
    INVESTMENT_BLOCKS_ADDRESS,
    InvestmentBlocksABI,
    provider
  ),
  
  // Token
  omk: new Contract(OMK_TOKEN_ADDRESS, ERC20_ABI, provider),
  
  // Governance
  governor: new Contract(GOVERNOR_ADDRESS, GovernorABI, provider),
  
  // Treasury
  treasury: new Contract(TREASURY_ADDRESS, TreasuryABI, provider),
};
```

---

## 🚀 **Implementation Workflow**

### **Phase 1: Foundation (Week 1-3)**
1. Set up Next.js 14 project structure
2. Install dependencies (Shadcn, TailwindCSS, etc.)
3. Configure luxury black & gold theme
4. Set up Zustand stores
5. Create design system components
6. Implement authentication (wallet + email)
7. Build user dashboard
8. Integrate with Queen API

### **Phase 2: Investment Platform (Week 4-7)**
1. Property marketplace UI
2. Investment flow implementation
3. Public sale interface
4. OTC trading platform
5. Smart contract integration
6. Transaction handling

### **Phase 3: Admin Tools (Week 8-11)**
1. Admin dashboard
2. User management system
3. Property approval workflow
4. Financial oversight tools
5. Support ticketing
6. Analytics & reports

### **Phases 4-7: Extended Features (Week 12-20)**
- Governance portal
- Presale & airdrops
- Partner portal
- Institutional portal

---

## ✅ **Success Criteria**

### **FPRIME-1 (User Portal):**
- [ ] User can connect wallet
- [ ] Dashboard shows accurate data
- [ ] Portfolio updates in real-time
- [ ] Transaction history loads
- [ ] KYC flow works

### **FPRIME-2 (Investment):**
- [ ] Properties display correctly
- [ ] Investment flow completes
- [ ] Token purchase works
- [ ] OTC trading functional

### **FPRIME-7 (Admin):**
- [ ] All platform data visible
- [ ] User management works
- [ ] Property approvals functional
- [ ] Analytics accurate

### **Overall:**
- [ ] Responsive on all devices
- [ ] Dark/light theme toggle
- [ ] Performance optimized (< 3s load)
- [ ] Accessibility (WCAG 2.1 AA)
- [ ] SEO optimized
- [ ] Error handling comprehensive

---

## 📝 **Next Steps**

1. **Review this roadmap** - Confirm priorities and timeline
2. **Start FPRIME-1** - User Portal implementation
3. **Set up project structure** - Initialize Next.js app with proper architecture
4. **Design system** - Build Shadcn components with luxury theme
5. **Backend sync** - Fix Queen AI connection (parallel task)

---

## 🔧 **Backend Connection Fix** (To address later)

Current issue: Frontend uses mock responses instead of Queen AI.

**Fix required in:** `/omk-frontend/app/chat/page.tsx`
- Replace mock `addMessage` responses
- Connect to Queen API properly
- Handle loading states
- Implement error handling

**File:** `BACKEND_CONNECTION_FIX.md` (to be created)

---

**Ready to start building! 🚀**
