# Private Investor OTC Flow - Pre-TGE

**Date:** October 10, 2025  
**Contract:** `PrivateInvestorRegistry.sol`  
**Admin Control:** Founder wallet has complete control

---

## 🎯 Overview

Pre-TGE private investors buy OMK tokens through OTC deals (off-chain payment). At TGE, they receive their tokens automatically to their registered wallet.

**Admin Powers:**
- ✅ Register investor allocations
- ✅ Update allocations (pre-TGE only)
- ✅ Remove investors (emergency, pre-TGE only)
- ✅ Execute TGE (one-time trigger)
- ✅ Distribute tokens (post-TGE)
- ✅ Full treasury control

---

## 📋 Smart Contract Functions

### Pre-TGE (Admin Only)

**1. Register New Investor**
```solidity
function registerInvestor(
    address wallet,           // 0x123...
    uint256 allocation,       // 1,000,000 * 10**18 (1M OMK)
    uint256 amountPaid,       // 100,000 * 10**6 ($100,000 USD)
    uint256 pricePerToken,    // 100000 ($0.10 per token, 6 decimals)
    string investorId         // "INV-001"
) external onlyRole(REGISTRY_MANAGER_ROLE)
```

**2. Update Allocation**
```solidity
function updateInvestorAllocation(
    address wallet,
    uint256 newAllocation
) external onlyRole(REGISTRY_MANAGER_ROLE)
```

**3. Remove Investor (Emergency)**
```solidity
function removeInvestor(address wallet) 
    external onlyRole(DEFAULT_ADMIN_ROLE)
```

### TGE Execution (Admin Only)

**4. Execute TGE**
```solidity
function executeTGE() external onlyRole(DEFAULT_ADMIN_ROLE)
// One-time action, cannot be reversed
// Enables token distribution
```

### Post-TGE Distribution

**5. Distribute to Single Investor**
```solidity
function distributeToInvestor(address wallet) 
    external onlyRole(REGISTRY_MANAGER_ROLE)
```

**6. Batch Distribute**
```solidity
function batchDistribute(address[] wallets) 
    external onlyRole(REGISTRY_MANAGER_ROLE)
```

**7. Distribute to All**
```solidity
function distributeToAll() 
    external onlyRole(REGISTRY_MANAGER_ROLE)
// Gas intensive, use carefully
```

---

## 💬 Conversational UI Flow (Frontend)

### Phase 1: Pre-TGE Investor Registration

**Scene: Admin Dashboard → Private Investors Tab**

```
┌─────────────────────────────────────────────────────────┐
│ 👤 Private Investors (Pre-TGE)                         │
│                                                          │
│ 📊 Stats:                                               │
│   • Total Investors: 12                                 │
│   • Total Allocated: 15,000,000 OMK                    │
│   • Remaining Capacity: 85,000,000 OMK                 │
│                                                          │
│ [+ Register New Investor]                               │
│                                                          │
│ Recent Investors:                                       │
│ ┌───────────────────────────────────────────────────┐  │
│ │ INV-001 • 0x742d...35fa • 1,000,000 OMK • $100K  │  │
│ │ INV-002 • 0x8f3a...29bc • 500,000 OMK • $50K     │  │
│ │ INV-003 • 0x1c4e...88de • 2,000,000 OMK • $200K  │  │
│ └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Conversation Flow: Register New Investor

**User clicks [+ Register New Investor]**

```
╔════════════════════════════════════════════════════╗
║  Queen AI: Register Private Investor               ║
╚════════════════════════════════════════════════════╝

🐝 Queen AI:
   Hey! Let's get this investor registered. I'll need a few
   details to set them up in the system.

   First - what's their wallet address? They'll receive their
   OMK tokens here at TGE.

┌────────────────────────────────────────────────────┐
│ Wallet Address                                      │
│ ┌────────────────────────────────────────────────┐ │
│ │ 0x                                              │ │
│ └────────────────────────────────────────────────┘ │
│ Must be a valid Ethereum address                   │
└────────────────────────────────────────────────────┘

[Continue →]
```

**After entering wallet:**

```
🐝 Queen AI:
   Perfect! Now, how much OMK are they getting?

   ⚠️ Important: Current allocations = 15M OMK
             Remaining capacity = 85M OMK
             Max total = 100M OMK

┌────────────────────────────────────────────────────┐
│ OMK Allocation                                      │
│ ┌────────────────────────────────────────────────┐ │
│ │ 1,000,000                        OMK            │ │
│ └────────────────────────────────────────────────┘ │
│                                                     │
│ Quick options:                                     │
│ [100K] [500K] [1M] [2M] [5M]                      │
└────────────────────────────────────────────────────┘

[Continue →]
```

**After entering allocation:**

```
🐝 Queen AI:
   Great! Now for the payment details - how much did they
   pay in USD? (This is just for our records, not on-chain)

┌────────────────────────────────────────────────────┐
│ Amount Paid (USD)                                   │
│ ┌────────────────────────────────────────────────┐ │
│ │ $100,000.00                                     │ │
│ └────────────────────────────────────────────────┘ │
│                                                     │
│ Price per token: $0.10                             │
│ (Calculated: $100,000 ÷ 1,000,000 OMK)            │
└────────────────────────────────────────────────────┘

[Continue →]
```

**After entering payment:**

```
🐝 Queen AI:
   Almost done! Last thing - give them an investor ID for
   your records. Something like "INV-004" or their company
   name.

┌────────────────────────────────────────────────────┐
│ Investor ID (Reference)                             │
│ ┌────────────────────────────────────────────────┐ │
│ │ INV-004                                         │ │
│ └────────────────────────────────────────────────┘ │
│ Examples: INV-001, ACME-CORP, INVESTOR-JOHN        │
└────────────────────────────────────────────────────┘

[Register Investor]
```

**Review & Confirm:**

```
╔════════════════════════════════════════════════════╗
║  Confirm Registration                               ║
╚════════════════════════════════════════════════════╝

🐝 Queen AI:
   Here's what we're registering:

   📋 Investor Details:
      • Wallet: 0x742d35ab9...529fa
      • Allocation: 1,000,000 OMK
      • Paid: $100,000.00 USD
      • Price: $0.10 per OMK
      • ID: INV-004

   📊 Updated Totals:
      • Total Investors: 12 → 13
      • Total Allocated: 15M → 16M OMK
      • Remaining: 85M → 84M OMK

   ⛽ Gas: ~0.02 ETH ($50)

   Everything look good?

[✓ Confirm & Register]  [✗ Cancel]
```

**After clicking Confirm:**

```
🐝 Queen AI:
   Signing transaction... Please approve in your wallet.

   ⏳ Waiting for wallet approval...

   [View in Wallet]
```

**Success:**

```
✅ Investor Registered!

🐝 Queen AI:
   Done! INV-004 is now in the system.

   They'll automatically receive their 1,000,000 OMK tokens
   to 0x742d...29fa when you execute TGE.

   Transaction: 0x8a3f...92bc

[View Investor] [Register Another] [Back to Dashboard]
```

---

### Phase 2: TGE Execution

**Scene: Admin Dashboard → TGE Control**

```
┌─────────────────────────────────────────────────────────┐
│ 🚀 Token Generation Event (TGE)                        │
│                                                          │
│ Status: ⏸️  NOT EXECUTED                                │
│                                                          │
│ 📊 Ready for TGE:                                       │
│   • 13 Private Investors Registered                    │
│   • 16,000,000 OMK Allocated                           │
│   • Contract Balance: 100,000,000 OMK ✅               │
│                                                          │
│ ⚠️  WARNING: This action is IRREVERSIBLE                │
│   Once TGE is executed, you cannot add/remove          │
│   investors. Only distribution will be possible.        │
│                                                          │
│ [Execute TGE] [View Investors]                          │
└─────────────────────────────────────────────────────────┘
```

**Clicking [Execute TGE]:**

```
╔════════════════════════════════════════════════════╗
║  ⚠️  Execute Token Generation Event                 ║
╚════════════════════════════════════════════════════╝

🐝 Queen AI:
   Whoa - this is a big moment! Let me walk you through
   what's about to happen.

   📋 What TGE Does:
      ✓ Locks the investor list (no more changes)
      ✓ Enables token distribution
      ✓ Records TGE timestamp on-chain
      ✓ Opens distribution to all 13 investors

   ❌ What You CAN'T Do After TGE:
      • Add new investors to this registry
      • Modify allocations
      • Remove investors

   ✅ What You CAN Do After TGE:
      • Distribute tokens to investors
      • Check distribution status
      • Set up vesting (optional)

   Are you absolutely sure you're ready?

   Type "EXECUTE TGE" to confirm:

┌────────────────────────────────────────────────────┐
│ ┌────────────────────────────────────────────────┐ │
│ │                                                 │ │
│ └────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────┘

[Cancel]
```

**After typing "EXECUTE TGE":**

```
🐝 Queen AI:
   Alright, let's do this! 🚀

   Executing TGE...

   ⏳ Broadcasting transaction...

   [View in Wallet]
```

**Success:**

```
✅ TGE Executed Successfully!

🐝 Queen AI:
   🎉 Congratulations! The Token Generation Event is live!

   📊 TGE Details:
      • Timestamp: Oct 10, 2025 6:50 PM UTC
      • Total Investors: 13
      • Total Allocated: 16,000,000 OMK
      • Status: ACTIVE ✅

   🎯 Next Steps:
      1. Distribute tokens to investors
      2. They can start receiving their OMK

   Want to start distributing now?

[Distribute Tokens] [View Dashboard]
```

---

### Phase 3: Token Distribution (Post-TGE)

**Scene: Admin Dashboard → Distribution**

```
┌─────────────────────────────────────────────────────────┐
│ 📦 Token Distribution                                   │
│                                                          │
│ TGE Status: ✅ EXECUTED (Oct 10, 2025)                 │
│                                                          │
│ 📊 Distribution Progress:                               │
│   ████████░░░░░░░░ 62% (8 of 13 investors)             │
│                                                          │
│   • Distributed: 10,000,000 OMK                        │
│   • Pending: 6,000,000 OMK                             │
│                                                          │
│ Actions:                                                │
│ [Distribute All Pending] [Distribute Single]            │
│                                                          │
│ Investor Status:                                        │
│ ┌───────────────────────────────────────────────────┐  │
│ │ ✅ INV-001 • 1,000,000 OMK • Distributed          │  │
│ │ ✅ INV-002 • 500,000 OMK • Distributed            │  │
│ │ ⏳ INV-003 • 2,000,000 OMK • Pending [Distribute] │  │
│ │ ⏳ INV-004 • 1,000,000 OMK • Pending [Distribute] │  │
│ └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Clicking [Distribute All Pending]:**

```
╔════════════════════════════════════════════════════╗
║  Distribute to All Pending Investors                ║
╚════════════════════════════════════════════════════╝

🐝 Queen AI:
   About to distribute to 5 pending investors:

   📋 Distribution Summary:
      • INV-003: 2,000,000 OMK → 0x1c4e...88de
      • INV-004: 1,000,000 OMK → 0x742d...29fa
      • INV-005: 500,000 OMK → 0x9a2f...44ec
      • INV-006: 1,500,000 OMK → 0x5b8c...77ad
      • INV-007: 1,000,000 OMK → 0x3d1a...99bf

   Total: 6,000,000 OMK

   ⚠️  This will execute in a single transaction.
       Gas estimate: ~0.05 ETH

[Distribute All] [Cancel]
```

**Success:**

```
✅ Distribution Complete!

🐝 Queen AI:
   All done! All 13 investors have received their tokens.

   📊 Final Stats:
      • Total Distributed: 16,000,000 OMK
      • Recipients: 13 investors
      • Status: 100% Complete ✅

   Everyone should see their OMK in their wallets now!

[View Full Report] [Back to Dashboard]
```

---

## 🎨 UI Design Principles (Matching Website Style)

### Conversational Tone
✅ "Hey! Let's get this investor registered"  
✅ "Perfect! Now, how much OMK are they getting?"  
✅ "Almost done! Last thing..."  
✅ "Whoa - this is a big moment!"  

### Clean & Minimal
- No clutter, focus on one task at a time
- Progress indicators (step 1 of 4)
- Clear next actions
- Emoji for personality, not noise

### Chat-Based Flow
- Queen AI guides you through each step
- One question at a time
- Conversational explanations
- Friendly but professional

### No Excessive Events/Notifications
- Silent background processing
- Status shown in-context
- No pop-ups unless critical
- Ethereum transactions shown in wallet only

---

## 📱 Mobile-Responsive Design

```
┌─────────────────────────┐
│ 👤 Private Investors   │
│                         │
│ 📊 13 investors         │
│ 📦 16M OMK allocated   │
│                         │
│ [+ Add Investor]        │
│                         │
│ INV-001                 │
│ 1M OMK • $100K         │
│ ✅ Distributed          │
│ ───────────────────     │
│ INV-002                 │
│ 500K OMK • $50K        │
│ ⏳ Pending              │
│ [Distribute]            │
└─────────────────────────┘
```

---

## 🔒 Admin Security

**Role Requirements:**
- `REGISTRY_MANAGER_ROLE`: Register, update, distribute
- `DEFAULT_ADMIN_ROLE`: Remove investors, execute TGE, emergency functions

**Founder Wallet Control:**
```solidity
constructor(address _admin) {
    _grantRole(DEFAULT_ADMIN_ROLE, _admin);
    _grantRole(REGISTRY_MANAGER_ROLE, _admin);
}
```

**Only your wallet can:**
- ✅ Register investors
- ✅ Update allocations (pre-TGE)
- ✅ Execute TGE
- ✅ Distribute tokens
- ✅ Emergency withdrawals

---

## 📊 Data Tracking

**On-Chain (Immutable):**
- Wallet addresses
- OMK allocations
- Distribution status
- TGE timestamp

**Off-Chain (Database - Optional):**
- Investor names/companies
- Email addresses
- KYC documents
- Wire transfer receipts
- Communication history

---

## ✅ Implementation Checklist

### Smart Contract
- [x] PrivateInvestorRegistry.sol created
- [x] Admin-only functions
- [x] TGE execution
- [x] Token distribution
- [x] Emergency controls

### Frontend (Next Steps)
- [ ] Admin dashboard UI
- [ ] Investor registration flow (conversational)
- [ ] TGE execution interface
- [ ] Distribution management
- [ ] Status tracking

### Integration
- [ ] Connect to deployed contract
- [ ] Wallet integration (admin wallet)
- [ ] Transaction status tracking
- [ ] Gas estimation

---

**Contract Created:** ✅ `PrivateInvestorRegistry.sol`  
**UI Flow Designed:** ✅ Conversational chat-based  
**Admin Control:** ✅ Complete (founder wallet)  
**Ready for:** Frontend implementation
