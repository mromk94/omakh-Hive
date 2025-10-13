# 🎯 EXP Points, Community Tasks & Airdrop System - TODO

**Status:** ⏳ AWAITING APPROVAL  
**Date:** October 10, 2025, 9:00 PM

---

## 📋 SYSTEM OVERVIEW

### Core Concept
**EXP Points** = Platform experience/reputation points that determine:
- Airdrop allocation amounts
- Community benefits
- Platform privileges
- Governance weight (future)

### How Users Earn EXP
1. **Property Slot Ownership** - Passive EXP per slot owned
2. **Community Tasks** - Active EXP for completing tasks
3. **Referrals** - EXP for bringing new users
4. **Platform Engagement** - Daily login streaks, etc.

---

## 🏗️ ARCHITECTURE

### 1. Smart Contracts

#### PropertySlotRegistry.sol (NEW)
```solidity
// Track property slot ownership and EXP
mapping(address => uint256) public userSlots;
mapping(address => uint256) public slotEXP;

uint256 public constant EXP_PER_SLOT_PER_DAY = 10;

function calculateSlotEXP(address user) returns (uint256)
```

#### CommunityTasksContract.sol (NEW)
```solidity
struct Task {
    uint256 taskId;
    string description;
    uint256 expReward;
    uint256 deadline;
    bool active;
}

mapping(address => mapping(uint256 => bool)) public taskCompleted;
mapping(address => uint256) public taskEXP;
```

#### AirdropDistributor.sol (NEW)
```solidity
// EXP-weighted airdrop distribution
mapping(address => uint256) public totalEXP;
mapping(uint256 => AirdropRound) public airdrops;

function calculateAirdropShare(address user, uint256 roundId) 
    returns (uint256)
```

#### EXPToken.sol (NEW - Non-transferable)
```solidity
// Soul-bound EXP token (cannot be transferred)
mapping(address => uint256) public balanceOf;

function mint(address to, uint256 amount) onlyAuthorized
function burn(address from, uint256 amount) onlyAuthorized
// NO transfer function - EXP is earned, not bought
```

---

### 2. Backend (Queen AI)

#### CommunityTasksBee.py (NEW)
```python
class CommunityTasksBee(BaseBee):
    """
    Manages community tasks, verification, and EXP awards
    """
    
    async def create_task(...)
    async def verify_task_completion(...)
    async def award_exp(...)
    async def get_user_tasks(...)
    async def get_leaderboard(...)
```

#### AirdropBee.py (NEW)
```python
class AirdropBee(BaseBee):
    """
    Calculates airdrop distributions based on EXP
    """
    
    async def calculate_distribution(...)
    async def get_user_allocation(...)
    async def execute_airdrop(...)
    async def get_airdrop_history(...)
```

#### EXPTrackerBee.py (NEW)
```python
class EXPTrackerBee(BaseBee):
    """
    Tracks all EXP sources and maintains user totals
    """
    
    async def track_slot_exp(...)
    async def track_task_exp(...)
    async def get_user_exp_breakdown(...)
    async def sync_exp_to_chain(...)
```

---

### 3. Frontend Components

#### TasksPage.tsx (NEW)
- List of available tasks
- Task completion UI
- Progress tracking
- EXP rewards display

#### AirdropDashboard.tsx (NEW)
- Upcoming airdrops
- User's expected allocation
- Historical airdrops
- Claim interface

#### EXPDashboard.tsx (NEW)
- Total EXP display
- EXP breakdown by source
- Leaderboard position
- EXP history timeline

#### CommunityHub.tsx (NEW)
- Tasks + Airdrops + EXP in one place
- Community announcements
- Task discussions

---

## 📝 DETAILED TODO LIST

### Phase 1: Smart Contracts (2 weeks)

**Week 1:**
- [ ] Design EXPToken contract (soul-bound)
- [ ] Design PropertySlotRegistry with EXP tracking
- [ ] Write unit tests for EXP calculation logic
- [ ] Implement slot purchase → EXP minting flow
- [ ] Add 90% USDT / 10% OMK stake logic to slot purchase

**Week 2:**
- [ ] Design CommunityTasksContract
- [ ] Design AirdropDistributor contract
- [ ] Implement task verification system
- [ ] Implement EXP-weighted airdrop calculation
- [ ] Write comprehensive tests
- [ ] Security audit preparation
- [ ] Deploy to testnet

---

### Phase 2: Backend (Queen AI) (2 weeks)

**Week 3:**
- [ ] Create CommunityTasksBee
  - [ ] Task CRUD operations
  - [ ] Task verification logic (screenshot upload, link verification, etc.)
  - [ ] EXP award automation
  - [ ] Task templates (Twitter follow, Discord join, etc.)
  
- [ ] Create EXPTrackerBee
  - [ ] Real-time EXP tracking
  - [ ] EXP breakdown by source
  - [ ] Leaderboard generation
  - [ ] EXP history logging

**Week 4:**
- [ ] Create AirdropBee
  - [ ] Airdrop round management
  - [ ] Distribution calculation (EXP-weighted)
  - [ ] Airdrop execution
  - [ ] Claim tracking
  
- [ ] Integration
  - [ ] Connect TasksBee ↔ EXPTracker ↔ Blockchain
  - [ ] Connect AirdropBee ↔ EXPTracker ↔ Blockchain
  - [ ] API endpoints for frontend
  - [ ] Event listeners for blockchain events

---

### Phase 3: Frontend (2 weeks)

**Week 5:**
- [ ] TasksPage
  - [ ] Task list with filters (active, completed, expired)
  - [ ] Task detail modal
  - [ ] Task completion UI (upload proof, submit links)
  - [ ] Real-time EXP updates
  - [ ] Task progress bars
  
- [ ] EXPDashboard
  - [ ] Total EXP display (animated counter)
  - [ ] EXP breakdown chart (pie/bar chart)
  - [ ] EXP sources timeline
  - [ ] Rank badge display

**Week 6:**
- [ ] AirdropDashboard
  - [ ] Upcoming airdrops list
  - [ ] User allocation calculator
  - [ ] Airdrop countdown timers
  - [ ] Claim button + transaction flow
  - [ ] Historical airdrops table
  
- [ ] CommunityHub
  - [ ] Unified dashboard
  - [ ] Announcements section
  - [ ] Task discussions/comments
  - [ ] Leaderboard widget

---

### Phase 4: Task Types & Automation (1 week)

**Week 7:**
- [ ] Social Media Tasks
  - [ ] Twitter follow verification (Twitter API)
  - [ ] Twitter retweet verification
  - [ ] Discord join verification (Discord API)
  - [ ] Telegram join verification
  
- [ ] Platform Tasks
  - [ ] Daily login streak
  - [ ] First property slot purchase
  - [ ] Refer a friend
  - [ ] Complete profile
  
- [ ] Content Tasks
  - [ ] Write review
  - [ ] Submit feedback
  - [ ] Create content (blog, video)
  - [ ] Share on social media

---

## 🔄 SYSTEM FLOW

### Property Slot Purchase Flow
```
User buys property slot with OMK
  ↓
Smart Contract:
  - 90% OMK → Convert to USDT
  - 10% OMK → Stake in staking contract
  - Mint property slot NFT
  - Award EXP (PropertySlotRegistry)
  ↓
EXPTrackerBee:
  - Detect SlotPurchased event
  - Update user's total EXP
  - Log EXP transaction
  ↓
Frontend:
  - Show +X EXP notification
  - Update EXP dashboard
```

### Community Task Completion Flow
```
User sees task: "Follow @OmakhIO on Twitter"
  ↓
User clicks "Complete Task"
  ↓
TasksPage shows:
  - "Follow the account"
  - "Upload screenshot as proof"
  ↓
User uploads screenshot
  ↓
Frontend → Backend API:
  POST /api/tasks/submit
  { taskId, proof: base64Image }
  ↓
CommunityTasksBee:
  - Receive submission
  - Analyze screenshot (Gemini Vision!)
  - Verify follow action visible
  - Mark task as completed
  - Award EXP via smart contract
  ↓
Smart Contract (CommunityTasksContract):
  - Verify bee signature
  - Mint EXP tokens to user
  - Emit TaskCompleted event
  ↓
EXPTrackerBee:
  - Detect TaskCompleted event
  - Update user's total EXP
  ↓
Frontend:
  - Show "✅ Task Verified! +50 EXP"
  - Update task status
  - Update EXP dashboard
```

### Airdrop Distribution Flow
```
Admin creates airdrop: "1,000,000 OMK Airdrop"
  ↓
AirdropBee calculates:
  - Total platform EXP = sum of all users
  - User A has 10,000 EXP (10% of total)
  - User B has 5,000 EXP (5% of total)
  - ...
  ↓
Distribution:
  - User A gets 10% of 1M = 100,000 OMK
  - User B gets 5% of 1M = 50,000 OMK
  ↓
Smart Contract (AirdropDistributor):
  - Store allocations on-chain
  - Enable claiming
  ↓
Frontend (AirdropDashboard):
  - Shows "You're eligible for 100,000 OMK!"
  - "Claim Now" button
  ↓
User clicks claim
  ↓
Transaction sent:
  - AirdropDistributor.claim(roundId)
  - Transfers OMK to user
  - Emits AirdropClaimed event
  ↓
Frontend:
  - Show success notification
  - Update claimed status
```

---

## 🎮 TASK EXAMPLES

### Daily Tasks
| Task | EXP Reward | Verification |
|------|-----------|--------------|
| Login to platform | 10 EXP | Auto (session tracking) |
| Check properties page | 5 EXP | Auto (page visit) |
| Chat with Queen | 5 EXP | Auto (message sent) |

### Social Tasks
| Task | EXP Reward | Verification |
|------|-----------|--------------|
| Follow @OmakhIO | 50 EXP | Screenshot + Gemini Vision |
| Retweet announcement | 30 EXP | Link verification |
| Join Discord server | 50 EXP | Discord API |
| Join Telegram | 50 EXP | Telegram API |

### Investment Tasks
| Task | EXP Reward | Verification |
|------|-----------|--------------|
| Buy first property slot | 200 EXP | Blockchain event |
| Stake OMK tokens | 100 EXP | Blockchain event |
| Refer a friend | 500 EXP | Referral code |

---

## 💰 AIRDROP TYPES

### 1. Regular Community Airdrops
- **Frequency:** Monthly
- **Amount:** 500,000 - 1,000,000 OMK
- **Distribution:** EXP-weighted
- **Eligibility:** Min 100 EXP

### 2. Event Airdrops
- **Trigger:** Platform milestones (10k users, $1M TVL, etc.)
- **Amount:** Variable
- **Distribution:** EXP-weighted
- **Bonus:** Extra rewards for top EXP holders

### 3. Task-Specific Airdrops
- **Trigger:** Special campaigns
- **Amount:** 100,000 - 500,000 OMK
- **Distribution:** Only users who completed specific tasks
- **Example:** "NFT Launch Airdrop" for users with 500+ EXP

---

## 🔐 SECURITY CONSIDERATIONS

### Anti-Gaming Measures
1. **Sybil Resistance:**
   - Require wallet funding (>$10) before EXP
   - KYC verification for high-value airdrops
   - Social proof (Twitter age, followers)

2. **Task Verification:**
   - Gemini Vision for screenshot analysis
   - API verification where possible
   - Manual review for high-value tasks
   - Cooldown periods between similar tasks

3. **EXP Inflation Control:**
   - Max daily EXP from tasks
   - Diminishing returns for repeated actions
   - EXP decay for inactive users (optional)

4. **Airdrop Protection:**
   - Snapshot mechanism (can't game last minute)
   - Vesting for large allocations
   - Claim deadline to prevent dust

---

## 📊 METRICS TO TRACK

### User Engagement
- Daily active tasks completed
- Average EXP per user
- Task completion rate
- Most popular tasks

### Platform Growth
- New users from referrals
- Total EXP minted
- Task participation trend
- Airdrop claim rate

### Economic
- EXP to airdrop ratio
- Task completion ROI
- Sybil detection rate
- Cost per acquired user

---

## 🚀 LAUNCH STRATEGY

### MVP (Minimum Viable Product)
**Launch with:**
- 5 social media tasks
- 3 platform engagement tasks
- 1 investment task
- Basic EXP tracking
- Simple airdrop (manual distribution)

### V2 (Enhanced)
**Add:**
- Automated task verification
- Gemini Vision for screenshots
- Leaderboards
- Daily/weekly tasks rotation
- Task marketplace (community-created)

### V3 (Advanced)
**Add:**
- Governance integration (EXP → voting power)
- NFT rewards for top contributors
- Task bounties (community funds tasks)
- Cross-platform EXP (partner protocols)

---

## ⚠️ RISKS & MITIGATION

| Risk | Impact | Mitigation |
|------|--------|------------|
| Sybil attacks | High | KYC, wallet funding requirement |
| Task gaming | Medium | Gemini Vision, API verification |
| EXP inflation | Medium | Caps, decay, dynamic rewards |
| Low participation | High | Attractive rewards, easy tasks |
| Airdrop farming | High | Snapshots, vesting, minimums |
| Bee overload | Medium | Task queues, rate limiting |
| Gemini API costs | Low | Caching, batch processing |

---

## 📦 DELIVERABLES

### Contracts
- [ ] EXPToken.sol
- [ ] PropertySlotRegistry.sol
- [ ] CommunityTasksContract.sol
- [ ] AirdropDistributor.sol
- [ ] Full test suite
- [ ] Deployment scripts

### Backend
- [ ] CommunityTasksBee
- [ ] AirdropBee
- [ ] EXPTrackerBee
- [ ] API endpoints (/tasks, /airdrops, /exp)
- [ ] Task verification system
- [ ] Event listeners

### Frontend
- [ ] TasksPage
- [ ] AirdropDashboard
- [ ] EXPDashboard
- [ ] CommunityHub
- [ ] Integration with existing chat

### Documentation
- [ ] User guide (how to earn EXP)
- [ ] Task creation guide (for admins)
- [ ] API documentation
- [ ] Contract documentation

---

## ⏱️ TIMELINE ESTIMATE

**Total: 7-8 weeks**

- Contracts: 2 weeks
- Backend: 2 weeks
- Frontend: 2 weeks
- Tasks & Automation: 1 week
- Testing & QA: 1 week
- Documentation: Ongoing

---

## 💵 COST ESTIMATE

### Development
- Smart contracts: $15,000
- Backend development: $12,000
- Frontend development: $10,000
- Gemini Vision integration: $3,000
- Testing & QA: $5,000
- **Total Dev:** $45,000

### Operations (Monthly)
- Gemini API: $500-1,000
- Server costs: $200
- Airdrop budget: $5,000-10,000
- **Total Monthly:** $5,700-11,200

---

## ✅ APPROVAL CHECKLIST

Before implementation, please confirm:

- [ ] System architecture approved
- [ ] Task types approved
- [ ] EXP rewards amounts approved
- [ ] Airdrop distribution logic approved
- [ ] Security measures approved
- [ ] Timeline acceptable
- [ ] Budget approved
- [ ] Gemini Vision usage approved

---

**Status:** ⏳ **AWAITING YOUR APPROVAL TO PROCEED**

Please review and approve/modify before implementation begins!
