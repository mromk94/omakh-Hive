# Complete OTC Purchase Flow - User Journey

**Date:** October 10, 2025, 7:45 PM  
**Purpose:** End-to-end user experience for OTC token purchases  
**Status:** ✅ Fully Implemented & Integrated

---

## 🎯 Overview

Users can purchase OMK tokens directly before TGE at $0.10/token (30% cheaper than public sale).  
**Intelligent wallet integration** - connects seamlessly with MetaMask or manual entry.

---

## 📱 User Journey (Chat-Based)

### Entry Points

**Option 1: From Welcome Flow**
```
User: "I want to invest"
Queen: "Great! Would you like to..."
  - [🎯 OTC Purchase ($0.10/token)]  ← User clicks this
  - [💰 Public Sale ($0.145/token)]
  - [🏠 Browse Properties]
```

**Option 2: Direct Command**
```
User: "OTC purchase" or "Buy tokens OTC"
Queen: Shows OTC Purchase Card
```

**Option 3: From Tier Comparison**
```
User: "Show me token tiers"
Queen: Shows tier comparison
  - [💎 Join OTC Sale - $0.10]  ← User clicks
```

---

## 🔄 Step-by-Step Flow

### Step 1: Welcome & Benefits

**UI Component:** `OTCPurchaseCard` (welcome step)

```
┌─────────────────────────────────────────────┐
│ 🎯 OTC Token Purchase                       │
├─────────────────────────────────────────────┤
│                                              │
│ 📋 Private Pre-TGE Sale                     │
│                                              │
│ Purchase OMK tokens directly before TGE     │
│ at an exclusive price.                      │
│                                              │
│ Price: $0.10/OMK  |  Min: 100,000 OMK      │
│                    ($10,000 USD)            │
│                                              │
│ ✨ Exclusive Benefits:                      │
│ ✅ Early Access - Before public            │
│ ✅ Better Price - 30% cheaper              │
│ ✅ Guaranteed Allocation                    │
│ ✅ Direct Distribution at TGE               │
│                                              │
│ ⚠️  Pre-TGE Process:                        │
│ 1. Submit request                           │
│ 2. Admin reviews & approves                 │
│ 3. Wire transfer payment                    │
│ 4. Tokens sent to wallet at TGE             │
│                                              │
│ [Start OTC Purchase Request]                │
└─────────────────────────────────────────────┘
```

---

### Step 2: Wallet Connection (Intelligent)

**Smart Wallet Detection:**
- Automatically detects MetaMask/wallet extensions
- If connected → auto-populate wallet address
- If not connected → offer connection or manual entry

```
┌─────────────────────────────────────────────┐
│ 🔗 Connect Your Wallet                      │
├─────────────────────────────────────────────┤
│                                              │
│ Connect your Ethereum wallet to receive     │
│ your OMK tokens at TGE.                     │
│                                              │
│ ┌─────────────────────────────────────────┐ │
│ │ [🦊 Connect Wallet (MetaMask)]          │ │
│ └─────────────────────────────────────────┘ │
│                                              │
│ ────────────── or ──────────────            │
│                                              │
│ ┌─────────────────────────────────────────┐ │
│ │ [📝 Enter Wallet Address Manually]      │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

**If Wallet Detected & Connected:**
```
┌─────────────────────────────────────────────┐
│ ✅ Wallet Connected!                        │
│                                              │
│ Connected Address:                          │
│ 0x742d35ab9...8e529fa                      │
│                                              │
│ [Continue →]  [Disconnect]                  │
└─────────────────────────────────────────────┘
```

**Wagmi Integration:**
```typescript
const { address, isConnected } = useAccount();
const { connect } = useConnect();

// Auto-populate when connected
useEffect(() => {
  if (isConnected && address) {
    setFormData(prev => ({ ...prev, wallet: address }));
    setStep('amount'); // Auto-advance to next step
  }
}, [isConnected, address]);
```

---

### Step 3: Amount Selection

```
┌─────────────────────────────────────────────┐
│ 💰 How Much OMK?                            │
├─────────────────────────────────────────────┤
│                                              │
│ Tokens will be sent to:                     │
│ 0x742d35...529fa                            │
│                                              │
│ OMK Token Amount *                          │
│ ┌─────────────────────────────────────────┐ │
│ │ 1000000                                  │ │
│ └─────────────────────────────────────────┘ │
│                                              │
│ Quick options:                              │
│ [100K] [250K] [500K] [1M] [2M]             │
│                                              │
│ ┌─────────────────────────────────────────┐ │
│ │ Total OMK Tokens: 1,000,000             │ │
│ │ Total Cost (USD): $100,000              │ │
│ │ @ $0.10 per OMK                         │ │
│ └─────────────────────────────────────────┘ │
│                                              │
│ [Continue →]                                │
└─────────────────────────────────────────────┘
```

**Real-Time Calculation:**
```typescript
const calculatePrice = (allocation: string) => {
  const tokens = parseFloat(allocation) || 0;
  const price = 0.10;
  return (tokens * price).toLocaleString('en-US', { 
    style: 'currency', 
    currency: 'USD'
  });
};
```

**Validation:**
- Minimum: 100,000 OMK ($10,000)
- Real-time price calculation
- Error message if below minimum

---

### Step 4: Contact Information

```
┌─────────────────────────────────────────────┐
│ 📧 Contact Information                      │
├─────────────────────────────────────────────┤
│                                              │
│ We'll use this to contact you about         │
│ payment details and confirm your purchase.  │
│                                              │
│ Full Name *                                 │
│ ┌─────────────────────────────────────────┐ │
│ │ John Doe                                 │ │
│ └─────────────────────────────────────────┘ │
│                                              │
│ Email Address *                             │
│ ┌─────────────────────────────────────────┐ │
│ │ john@example.com                         │ │
│ └─────────────────────────────────────────┘ │
│                                              │
│ [Review Purchase →]                         │
└─────────────────────────────────────────────┘
```

---

### Step 5: Review & Submit

```
┌─────────────────────────────────────────────┐
│ 📋 Review Your Request                      │
├─────────────────────────────────────────────┤
│                                              │
│ Purchase Summary                            │
│ ────────────────────────────────────        │
│ OMK Tokens:              1,000,000          │
│ Price per Token:         $0.10              │
│ ────────────────────────────────────        │
│ Total Cost:              $100,000           │
│                                              │
│ Your Information                            │
│ ────────────────────────────────────        │
│ Name:     John Doe                          │
│ Email:    john@example.com                  │
│ Wallet:   0x742d35ab9...8e529fa            │
│                                              │
│ ⚠️  Next Steps:                              │
│ 1. Admin review (24 hours)                  │
│ 2. Payment instructions via email           │
│ 3. Complete wire transfer                   │
│ 4. Tokens distributed at TGE                │
│                                              │
│ [← Back]  [Submit Request]                  │
└─────────────────────────────────────────────┘
```

---

### Step 6: Confirmation

```
┌─────────────────────────────────────────────┐
│         ✅ Request Submitted! 🎉            │
├─────────────────────────────────────────────┤
│                                              │
│ We've received your OTC purchase request    │
│ for 1,000,000 OMK tokens.                   │
│                                              │
│ What Happens Next?                          │
│                                              │
│ 1️⃣  Admin Review                            │
│     Our team reviews your request within    │
│     24 hours                                 │
│                                              │
│ 2️⃣  Payment Instructions                    │
│     You'll receive wire transfer details    │
│     via email                                │
│                                              │
│ 3️⃣  Complete Payment                        │
│     Send wire transfer to secure your       │
│     allocation                               │
│                                              │
│ 4️⃣  TGE Distribution                        │
│     Tokens automatically sent to your       │
│     wallet at TGE                            │
│                                              │
│ Confirmation sent to:                       │
│ john@example.com                            │
│                                              │
│ [Close]                                     │
└─────────────────────────────────────────────┘
```

**Queen AI Follow-Up:**
```
Queen: "✅ Your OTC purchase request has been submitted!

🎯 Allocation: 1,000,000 OMK
💰 Total: $100,000

Our team will review your request and contact you 
at john@example.com within 24 hours with payment 
instructions."

Options:
[📊 View Dashboard] [🏠 Browse Properties]
```

---

## 🔌 Technical Integration

### Component Structure

```typescript
<OTCPurchaseCard
  onSubmit={(data) => {
    // Data includes:
    // - wallet: string
    // - allocation: string
    // - amountUSD: string
    // - email: string
    // - name: string
    // - pricePerToken: number
    
    // Send to backend API
    await api.submitOTCRequest(data);
    
    // Show confirmation in chat
    addMessage('ai', 'Request submitted...');
  }}
  onClose={() => {
    // Return to chat
  }}
/>
```

### Wallet Connection Intelligence

**Auto-Detection:**
```typescript
// 1. Check if wallet is already connected
const { isConnected, address } = useAccount();

// 2. If connected, auto-populate
useEffect(() => {
  if (isConnected && address && step === 'wallet') {
    setFormData(prev => ({ ...prev, wallet: address }));
    setStep('amount'); // Skip to next step automatically
  }
}, [isConnected, address, step]);

// 3. Connect on demand
const handleConnectWallet = () => {
  connect({ connector: injected() }); // MetaMask
};
```

**Fallback Options:**
- If no wallet extension → Manual entry
- If connection fails → Manual entry with explanation
- If wrong network → Show network switch prompt

### Data Flow

```
User Input (Frontend)
        ↓
OTCPurchaseCard State
        ↓
Form Validation
        ↓
Submit Handler (Chat Component)
        ↓
Backend API (/api/otc-requests)
        ↓
Database (pending status)
        ↓
Admin Notification Email
        ↓
Admin Reviews in Dashboard
        ↓
Admin Registers in PrivateInvestorRegistry Contract
        ↓
User Email (payment instructions)
        ↓
Wire Transfer
        ↓
Admin Executes TGE
        ↓
Tokens Distributed to User Wallet ✅
```

---

## 🔐 Security & Validation

### Frontend Validation

```typescript
// Wallet address
const isValidAddress = /^0x[a-fA-F0-9]{40}$/.test(wallet);

// Minimum allocation
const minAllocation = 100000; // 100K OMK
const isValidAmount = parseFloat(allocation) >= minAllocation;

// Email format
const isValidEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

// All fields required
const isComplete = wallet && allocation && email && name;
```

### Backend Processing

```typescript
// POST /api/otc-requests
export async function POST(req: Request) {
  const data = await req.json();
  
  // Validate
  if (!isValidEthAddress(data.wallet)) {
    return Response.json({ error: 'Invalid wallet' }, { status: 400 });
  }
  
  if (parseFloat(data.allocation) < 100000) {
    return Response.json({ error: 'Below minimum' }, { status: 400 });
  }
  
  // Save to database
  const request = await db.otcRequests.create({
    data: {
      wallet: data.wallet,
      allocation: data.allocation,
      email: data.email,
      name: data.name,
      status: 'pending',
      pricePerToken: 0.10,
      createdAt: new Date()
    }
  });
  
  // Notify admin
  await sendAdminNotification(request);
  
  // Confirm to user
  await sendUserConfirmation(data.email, request);
  
  return Response.json({ success: true, requestId: request.id });
}
```

---

## 🎨 UX Features

### Intelligent Progression
- ✅ Auto-detects connected wallet
- ✅ Auto-advances steps when possible
- ✅ Real-time price calculation
- ✅ Validates before allowing progression
- ✅ Clear error messages

### Responsive Design
- ✅ Works on mobile & desktop
- ✅ Touch-friendly buttons
- ✅ Readable text sizes
- ✅ Accessible color contrast

### User Feedback
- ✅ Loading states during submission
- ✅ Success confirmation with details
- ✅ Error handling with helpful messages
- ✅ Progress indicators (step 1 of 4)

---

## 📊 Admin Dashboard Integration

**Admin sees the request:**

```
┌─────────────────────────────────────────────┐
│ 📥 New OTC Request                          │
├─────────────────────────────────────────────┤
│                                              │
│ Request ID: #1234                           │
│ Status: ⏳ Pending Review                    │
│ Submitted: Oct 10, 2025 7:30 PM            │
│                                              │
│ Investor Information:                       │
│ Name: John Doe                              │
│ Email: john@example.com                     │
│ Wallet: 0x742d35ab9...8e529fa              │
│                                              │
│ Purchase Details:                           │
│ Allocation: 1,000,000 OMK                   │
│ Price: $0.10/token                          │
│ Total: $100,000 USD                         │
│                                              │
│ [✅ Approve] [❌ Reject] [💬 Contact]       │
└─────────────────────────────────────────────┘
```

**Admin actions:**
1. **Approve** → Sends payment instructions to user
2. **Reject** → Sends rejection email with reason
3. **Contact** → Opens email client with user email

**After payment received:**
```
Admin registers investor in contract:

registry.registerInvestor(
  0x742d35ab9...8e529fa,  // wallet
  1000000 * 10**18,        // allocation
  100000 * 10**6,          // payment ($100K)
  100000,                  // price ($0.10)
  "OTC-1234"              // reference ID
);
```

---

## ✅ Complete Feature List

**User Features:**
- ✅ Chat-based conversational interface
- ✅ Intelligent wallet detection & connection
- ✅ Real-time price calculation
- ✅ Multi-step form with validation
- ✅ Clear confirmation & next steps
- ✅ Mobile responsive

**Admin Features:**
- ✅ Request management dashboard
- ✅ Approve/reject workflows
- ✅ Direct contract integration
- ✅ Email notifications
- ✅ Payment tracking

**Smart Contract:**
- ✅ PrivateInvestorRegistry integration
- ✅ Exact allocation tracking
- ✅ TGE execution & distribution
- ✅ Math verification (no precision loss)

---

## 🚀 How to Use

### For Users:
1. Open chat interface
2. Say "OTC purchase" or click related button
3. Follow the conversational flow
4. Connect wallet or enter manually
5. Select amount
6. Provide contact info
7. Review & submit
8. Wait for admin approval
9. Receive payment instructions
10. Complete payment
11. Receive tokens at TGE

### For Admin:
1. Receive email notification
2. Review request in dashboard
3. Approve or reject
4. Send payment instructions (if approved)
5. Verify payment received
6. Register investor in contract
7. Execute TGE when ready
8. Tokens automatically distributed

---

**Implementation Status:** ✅ COMPLETE  
**Wallet Integration:** ✅ INTELLIGENT  
**User Experience:** ✅ SEAMLESS  
**Admin Control:** ✅ FULL  

**Ready for production!** 🚀
