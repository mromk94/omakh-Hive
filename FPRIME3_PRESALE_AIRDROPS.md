# FPRIME-3: Presale & Airdrops

## 🎯 **Overview**
Private sale portal and airdrop claim mechanisms.

---

## **📋 Features & Tasks**

### **A. PRIVATE SALE PORTAL**

#### **1. Whitelist System**
- [ ] Application form (KYC required)
- [ ] Wallet address submission
- [ ] Investment tier selection
- [ ] Whitelist status check
- [ ] Approval/rejection notifications
- [ ] Allocation display

#### **2. Private Sale Dashboard**
- [ ] Sale countdown timer
- [ ] Allocation amount display
- [ ] Contribution limits (min/max)
- [ ] Bonus structure display
- [ ] Vesting schedule preview
- [ ] Personal allocation tracker

#### **3. Investment Interface**
- [ ] Contribute form
- [ ] Payment currency options
- [ ] Contribution calculator
- [ ] Transaction confirmation
- [ ] Receipt/proof of purchase
- [ ] Referral tracking

#### **4. Post-Sale Management**
- [ ] Vesting timeline
- [ ] Token claim interface
- [ ] Distribution history
- [ ] Lockup period display
- [ ] Early unlock options (if any)

---

### **B. AIRDROP PORTAL**

#### **1. Airdrop Campaigns**
- [ ] Active campaigns list
- [ ] Campaign details pages
- [ ] Eligibility checker
- [ ] Requirements display
- [ ] Campaign countdown
- [ ] Rewards calculator

#### **2. Task System**
- [ ] Task list (social, referrals, etc.)
- [ ] Task completion tracking
- [ ] Verification system
- [ ] Points accumulation
- [ ] Leaderboard
- [ ] Bonus multipliers

#### **3. Claim Interface**
- [ ] Claimable airdrops list
- [ ] Claim amount display
- [ ] One-click claim
- [ ] Multi-claim option
- [ ] Claim history
- [ ] Gas optimization

#### **4. Referral System**
- [ ] Unique referral link
- [ ] Referral stats
- [ ] Referred users list
- [ ] Referral rewards
- [ ] Tier-based bonuses
- [ ] Social sharing

---

## **🎨 UI Components**

### **Pages:**
```
/private-sale              - Private sale home
/private-sale/apply        - Whitelist application
/private-sale/contribute   - Make contribution
/airdrop                   - Airdrop campaigns
/airdrop/campaign/[id]     - Campaign details
/airdrop/tasks             - Task center
/airdrop/claims            - Claim interface
/airdrop/referrals         - Referral dashboard
```

### **Components:**
- `WhitelistForm` - Application form
- `AllocationCard` - Allocation display
- `ContributionForm` - Investment form
- `VestingTimeline` - Vesting schedule
- `CampaignCard` - Airdrop campaign
- `TaskList` - Task tracker
- `ClaimButton` - Claim interface
- `ReferralLink` - Referral generator

---

## **🔧 Technical Implementation**

### **Smart Contracts:**
```solidity
// PrivateSale.sol
- contribute(amount)
- claimVestedTokens()
- getVestingSchedule(address)
- getAllocation(address)

// AirdropManager.sol
- registerForAirdrop(campaignId)
- claimAirdrop(campaignId)
- verifyEligibility(address, campaignId)
- trackReferral(referrer, referee)
```

### **API Endpoints:**
```
POST /api/v1/private-sale/apply
GET  /api/v1/private-sale/status
POST /api/v1/private-sale/contribute
GET  /api/v1/airdrop/campaigns
POST /api/v1/airdrop/register
POST /api/v1/airdrop/claim
GET  /api/v1/referrals/stats
```

---

## **📊 Data Models**

```typescript
interface PrivateSaleApplication {
  walletAddress: string;
  tier: 'seed' | 'strategic' | 'private';
  requestedAmount: number;
  kycStatus: string;
  status: 'pending' | 'approved' | 'rejected';
}

interface AirdropCampaign {
  id: string;
  name: string;
  description: string;
  totalReward: number;
  startDate: Date;
  endDate: Date;
  requirements: Requirement[];
  claimDate: Date;
}

interface ReferralStats {
  totalReferrals: number;
  activeReferrals: number;
  totalRewards: number;
  tier: number;
}
```

---

**Estimated Time:** 2 weeks
**Priority:** 🟡 High (Token Distribution)
