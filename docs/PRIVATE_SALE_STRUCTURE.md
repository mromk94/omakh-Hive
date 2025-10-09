# PRIVATE SALE STRUCTURE

**Contract**: `PrivateSale.sol`  
**Total Allocation**: 100,000,000 OMK (10% of supply)  
**Management**: Queen AI + Off-Chain Portal  
**Vesting**: 12-month cliff + 18-month linear  

---

## 📊 TIER STRUCTURE

### **Tiered Pricing Model**

| Tier | Tokens | Price/Token | Total Raised | Cumulative |
|------|--------|-------------|--------------|------------|
| 0 | 10M | $0.100 | $1,000,000 | $1,000,000 |
| 1 | 10M | $0.105 | $1,050,000 | $2,050,000 |
| 2 | 10M | $0.110 | $1,100,000 | $3,150,000 |
| 3 | 10M | $0.115 | $1,150,000 | $4,300,000 |
| 4 | 10M | $0.120 | $1,200,000 | $5,500,000 |
| 5 | 10M | $0.125 | $1,250,000 | $6,750,000 |
| 6 | 10M | $0.130 | $1,300,000 | $8,050,000 |
| 7 | 10M | $0.135 | $1,350,000 | $9,400,000 |
| 8 | 10M | $0.140 | $1,400,000 | $10,800,000 |
| 9 | 10M | $0.145 | $1,450,000 | **$12,250,000** |

**Total Raised (if 100M sold)**: **$12.25 Million USD**

---

## 🐋 WHALE LIMITS

### **Per-Investor Cap**
- **Maximum**: 20M OMK per investor
- **Percentage**: 20% of private sale
- **USD Value**: $2.1M - $2.9M (depending on entry tier)

### **Rationale**
- Prevents over-concentration
- Ensures wider distribution
- Maintains community-first approach
- Allows multiple strategic investors

---

## 🔐 KYC & WHITELISTING

### **Requirements**
1. **KYC Verification** - Identity verification via partner
2. **Whitelist Approval** - Queen AI manages whitelist
3. **Accredited Status** - For regulatory compliance (if required)
4. **Geographic Restrictions** - Compliance with local laws

### **Process**
```
1. Investor submits KYC via off-chain portal
2. Third-party KYC provider verifies identity
3. Queen AI reviews and approves
4. Investor address whitelisted on-chain
5. Investor can purchase tokens
```

---

## 💰 PAYMENT TOKENS

### **Accepted Stablecoins**
- **USDC** (USD Coin) - Primary
- **USDT** (Tether) - Alternative
- **DAI** (if needed) - Additional option

### **Why Stablecoins?**
- Price stability during sale
- No forex risk
- Easy accounting
- Instant settlement
- Lower transaction costs

---

## 🔄 VESTING SCHEDULE

### **Timeline**
```
Month 0-12:  CLIFF (no tokens released)
Month 13:    25% released
Month 14-30: Remaining 75% released linearly (monthly)
```

### **Example for 10M OMK Purchase**
```
Month 0-12:   0 OMK (locked)
Month 13:     2.5M OMK (cliff release)
Month 14:     2.5M + 416,667 OMK
Month 15:     2.5M + 833,333 OMK
...
Month 30:     10M OMK (fully vested)
```

### **Rationale**
- **12-month cliff**: Ensures long-term commitment
- **25% at cliff**: Provides liquidity for early supporters
- **Linear vesting**: Smooth token release, prevents dumps
- **Total 30 months**: Reasonable timeframe for early investors

---

## 🤖 QUEEN AI MANAGEMENT

### **Queen's Role in Private Sale**

#### **1. Whitelist Management**
```solidity
// Queen can approve KYC'd investors
function setInvestorWhitelist(address investor, bool status)

// Batch whitelist for efficiency
function batchWhitelist(address[] investors, bool status)
```

#### **2. Sale Activation**
```solidity
// Start the sale when ready
function activateSale()

// Pause if issues arise
function deactivateSale()
```

#### **3. Monitoring & Analytics**
- Track tier progression
- Monitor whale participation
- Analyze geographic distribution
- Detect suspicious patterns

#### **4. Dynamic Adjustments**
- Add/remove payment tokens
- Update KYC requirements
- Modify sale parameters (pre-launch)

---

## 📱 OFF-CHAIN PORTAL

### **Portal Features**

#### **For Investors**
- **Dashboard**: View purchase history, vesting schedule
- **Buy Interface**: Select amount, see price, confirm transaction
- **Wallet Connect**: MetaMask, WalletConnect, Coinbase Wallet
- **Vesting Tracker**: Real-time vesting progress
- **Referral System**: Earn bonuses for referrals (optional)

#### **For Admin/Queen**
- **Analytics Dashboard**: Real-time sale metrics
- **KYC Management**: Approve/reject applicants
- **Tier Monitoring**: Track tier sell-through
- **Investor List**: View all participants
- **Fund Management**: Withdraw raised funds

### **Tech Stack**
```
Frontend:  Next.js + TailwindCSS + shadcn/ui
Backend:   NestJS API Gateway
Blockchain: ethers.js / viem
Database:  PostgreSQL
KYC:       Sumsub / Onfido / Jumio
Hosting:   Vercel (frontend) + GCP (backend)
```

---

## 🔗 SMART CONTRACT INTEGRATION

### **Deployment Flow**
```
1. Deploy OMKToken
2. Deploy TokenVesting (for private investors)
3. Deploy PrivateSale contract
4. Transfer 100M OMK to PrivateSale contract
5. Grant SALE_MANAGER_ROLE to Queen AI
6. Configure payment tokens (USDC, USDT)
7. Activate sale
```

### **Purchase Flow**
```
1. Investor connects wallet to portal
2. Investor selects amount to purchase
3. Portal calls PrivateSale.calculatePayment(amount)
4. Investor approves stablecoin spend
5. Investor calls PrivateSale.purchaseTokens(amount, paymentToken, maxPayment)
6. Contract checks:
   - Sale active?
   - Investor whitelisted?
   - Within whale limit?
   - Tokens available?
7. Contract transfers stablecoins to treasury
8. Contract records purchase
9. Tokens locked in vesting contract
```

### **Vesting Release Flow**
```
1. After 12-month cliff, investor can claim
2. Investor calls TokenVesting.release(beneficiary)
3. Contract calculates vested amount
4. Contract transfers OMK tokens to investor
5. Investor can sell or hold
```

---

## 📈 FUNDRAISING SCENARIOS

### **Scenario 1: Full Sellout**
- **Tokens Sold**: 100M OMK
- **Raised**: $12.25M USD
- **Average Price**: $0.1225

### **Scenario 2: 50% Sellout (5 tiers)**
- **Tokens Sold**: 50M OMK
- **Raised**: $5.375M USD
- **Average Price**: $0.1075

### **Scenario 3: 75% Sellout (7.5 tiers)**
- **Tokens Sold**: 75M OMK
- **Raised**: $8.75M USD
- **Average Price**: $0.1167

---

## 🛡️ SECURITY MEASURES

### **Smart Contract Security**
- ✅ **ReentrancyGuard**: Prevents reentrancy attacks
- ✅ **Pausable**: Emergency stop mechanism
- ✅ **AccessControl**: Role-based permissions
- ✅ **SafeERC20**: Safe token transfers
- ✅ **Whale Limits**: On-chain enforcement
- ✅ **Tier Logic**: Automatic tier advancement

### **Portal Security**
- ✅ **HTTPS Only**: Encrypted connections
- ✅ **Rate Limiting**: Prevent abuse
- ✅ **CSRF Protection**: Secure forms
- ✅ **Wallet Signatures**: Verify ownership
- ✅ **KYC Verification**: Identity checks
- ✅ **Geographic Blocking**: Compliance

### **Operational Security**
- ✅ **Multi-Sig Treasury**: Requires 2+ signatures
- ✅ **Time-Locked Withdrawals**: 24h delay for large amounts
- ✅ **Real-Time Monitoring**: Alert on anomalies
- ✅ **Audit Trail**: All actions logged

---

## 🎯 MARKETING STRATEGY

### **Phase 1: Pre-Launch (2 weeks)**
- Announce private sale details
- Open KYC portal
- Share tier structure
- Highlight Queen AI innovation

### **Phase 2: Early Bird (Week 1)**
- Target Tier 0-2 ($0.100-$0.110)
- Focus on strategic investors
- Emphasize best price
- Limited time messaging

### **Phase 3: Main Sale (Weeks 2-4)**
- Open to wider community
- Tier progression updates
- Scarcity messaging ("Only X tiers left!")
- Referral bonuses

### **Phase 4: Final Push (Week 5-6)**
- Final tier urgency
- Last chance messaging
- Community celebration
- Prepare for TGE

---

## 📊 SUCCESS METRICS

### **Hard Cap**: $12.25M (100M tokens)
### **Soft Cap**: $5M (minimum viable)

### **KPIs**
- **Total Raised**: Target $8M-$12M
- **Unique Investors**: Target 500-1,000
- **Average Investment**: $10K-$25K
- **Tier Velocity**: 1 tier per 3-5 days
- **Geographic Diversity**: 20+ countries
- **Whale Participation**: <30% of total

---

## 🚀 POST-SALE ACTIONS

### **Immediate (Day 1)**
1. Announce total raised
2. Thank investors
3. Share distribution stats
4. Prepare for TGE

### **Week 1**
1. Transfer funds to treasury
2. Begin treasury allocation
3. Start marketing campaigns
4. Prepare DEX listings

### **Month 1-12 (Cliff)**
1. Build community
2. Product development
3. Marketing execution
4. Prepare for cliff release

### **Month 13+ (Vesting)**
1. Enable token claims
2. Monitor sell pressure
3. Provide liquidity support
4. Community rewards

---

## 🔧 TECHNICAL INTEGRATION

### **Frontend Code Example**
```typescript
// Purchase tokens via portal
async function purchaseTokens(amount: string, paymentToken: string) {
  const privateSale = new ethers.Contract(PRIVATE_SALE_ADDR, ABI, signer);
  
  // 1. Calculate payment required
  const payment = await privateSale.calculatePayment(ethers.utils.parseEther(amount));
  
  // 2. Approve payment token
  const stablecoin = new ethers.Contract(paymentToken, ERC20_ABI, signer);
  await stablecoin.approve(PRIVATE_SALE_ADDR, payment);
  
  // 3. Purchase tokens
  const maxPayment = payment.mul(105).div(100); // 5% slippage tolerance
  await privateSale.purchaseTokens(
    ethers.utils.parseEther(amount),
    paymentToken,
    maxPayment
  );
  
  alert("Purchase successful! Tokens will vest over 30 months.");
}
```

### **Backend Code Example**
```python
# Queen AI monitors sale progress
class PrivateSaleMonitor:
    async def check_sale_status(self):
        status = await self.contract.getSaleStatus()
        
        # Alert if tier is about to complete
        if status.remainingInTier < 1_000_000:
            await self.alert("Tier almost complete!", status)
        
        # Track velocity
        velocity = await self.calculate_tier_velocity()
        if velocity < expected:
            await self.suggest_marketing_boost()
```

---

## ✅ CHECKLIST

### **Pre-Launch**
- [ ] Deploy PrivateSale contract
- [ ] Transfer 100M OMK to contract
- [ ] Configure payment tokens
- [ ] Grant Queen AI SALE_MANAGER_ROLE
- [ ] Set up KYC provider
- [ ] Build off-chain portal
- [ ] Security audit
- [ ] Legal review
- [ ] Marketing materials
- [ ] Community announcement

### **Launch**
- [ ] Activate sale
- [ ] Open KYC submissions
- [ ] Monitor first purchases
- [ ] Track tier progression
- [ ] Provide investor support
- [ ] Regular updates

### **Post-Sale**
- [ ] Deactivate sale
- [ ] Announce results
- [ ] Transfer funds to treasury
- [ ] Begin vesting countdown
- [ ] Prepare TGE

---

**Last Updated**: October 9, 2025  
**Version**: 1.0  
**Status**: Specification Complete, Implementation Ready
