# ADVISORS MANAGEMENT SYSTEM

**Last Updated**: October 9, 2025, 8:15 AM  
**Contract**: `AdvisorsManager.sol`  
**Status**: ✅ Implemented & Compiled

---

## 🎯 PROBLEM SOLVED

**Old System** ❌:
- Fixed single advisor wallet at deployment
- No flexibility to add advisors later
- All 40M goes to one address

**New System** ✅:
- **Dynamic advisor addition** - Admin adds advisors anytime
- **Split 40M across 10-20 wallets** - Each advisor gets individual allocation
- **Flexible amounts** - Admin decides how much per advisor
- **Queen can propose, Admin approves** - Two-step process for security
- **Individual vesting per advisor** - Each gets 12m cliff + 18m linear

---

## 📦 HOW IT WORKS

### **Step 1: Deployment**

```javascript
// Deploy AdvisorsManager
const advisorsManager = await AdvisorsManager.deploy(
    omkToken.address,
    adminWallet.address,
    queenWallet.address
);

// AdvisorsManager receives 40M OMK from VestingManager
// Now sitting in pool, ready to allocate
```

### **Step 2: Add Advisors (Two Ways)**

#### **Option A: Queen Proposes → Admin Approves**

```solidity
// 1. Queen proposes advisor
queenAI.proposeAdvisor(
    "0xAdvisor1...",  // Advisor wallet
    2_000_000 OMK,    // 2M allocation
    "Marketing Advisor"
);

// 2. Admin reviews and approves
admin.approveProposal(proposalId);
// ✅ Advisor added, vesting starts!
```

#### **Option B: Admin Adds Directly**

```solidity
// Admin can bypass proposal system
admin.addAdvisorDirect(
    "0xAdvisor2...",
    1_500_000 OMK,
    "Tech Advisor"
);
// ✅ Immediate addition
```

### **Step 3: Advisors Claim**

```solidity
// After 12 month cliff, advisors can claim monthly
advisor.claimMyTokens();
// Tokens released according to vesting schedule
```

---

## 🔄 COMPLETE FLOW

```
40M OMK Pool
    ↓
AdvisorsManager (holds all 40M)
    ↓
Admin Adds Advisors Over Time
    ├─ Month 1: Add Marketing Advisor (2M)
    ├─ Month 3: Add Tech Advisor (1.5M)
    ├─ Month 6: Add Legal Advisor (1M)
    ├─ Month 9: Add BD Advisor (2M)
    └─ Year 2: Add more as needed...
    ↓
Each Advisor Gets Individual TokenVesting Contract
    ├─ 12 month cliff
    ├─ 18 month linear after cliff
    └─ Total: 30 months
    ↓
After Cliff, Each Advisor Claims Their Tokens
    ├─ advisor1.claimMyTokens()
    ├─ advisor2.claimMyTokens()
    └─ advisor3.claimMyTokens()
```

---

## 💡 EXAMPLE SCENARIO

### **Year 1**

**Month 0 (Launch)**:
```
Total Pool: 40M OMK
Allocated: 0
Available: 40M
Advisors: 0
```

**Month 1 - Add First Advisor**:
```javascript
admin.addAdvisorDirect(
    "0xMarketing...",
    2_000_000 OMK,
    "CMO - Marketing Strategy"
);
```
```
Allocated: 2M
Available: 38M
Advisors: 1
```

**Month 3 - Add Tech Advisor**:
```javascript
queenAI.proposeAdvisor(
    "0xTechLead...",
    3_000_000 OMK,
    "CTO - Technical Architecture"
);
admin.approveProposal(1);
```
```
Allocated: 5M
Available: 35M
Advisors: 2
```

**Month 6 - Add Legal + BD**:
```javascript
admin.addAdvisorDirect("0xLegal...", 1_500_000, "Legal Counsel");
admin.addAdvisorDirect("0xBizDev...", 2_500_000, "BD Lead");
```
```
Allocated: 9M
Available: 31M
Advisors: 4
```

### **Year 2**

**Month 13 - First Claims Start!**
```javascript
// Marketing Advisor (added month 1) reaches 12m cliff
marketingAdvisor.claimMyTokens();
// Receives: 2M ÷ 18 = ~111,111 OMK (first month)
```

**Month 15 - Tech Advisor Claims**
```javascript
// Tech Advisor (added month 3) reaches 12m cliff
techAdvisor.claimMyTokens();
// Receives: 3M ÷ 18 = 166,666 OMK (first month)
```

**Ongoing - Add More Advisors**:
```javascript
admin.addAdvisorDirect("0xAdvisor5...", 2_000_000, "Growth Lead");
admin.addAdvisorDirect("0xAdvisor6...", 1_500_000, "Security Advisor");
```

---

## 📊 KEY FEATURES

### ✅ **Flexibility**
- Add advisors anytime during project lifecycle
- Not limited to deployment time
- Adjust allocations per advisor

### ✅ **Control**
- Admin has final approval
- Can reject bad proposals
- Can remove advisors in emergency

### ✅ **Queen Integration**
- Queen can propose advisors
- Leverages AI decision-making
- Admin maintains oversight

### ✅ **Individual Vesting**
- Each advisor has own TokenVesting contract
- Same schedule: 12m cliff + 18m linear
- Independent claim functions

### ✅ **Transparency**
- All proposals logged on-chain
- Pool stats publicly viewable
- Track allocated vs available

### ✅ **Security**
- Two-step proposal system
- Admin emergency removal
- Pool exhaustion protection

---

## 🔍 CONTRACT FUNCTIONS

### **For Admin**

```solidity
// Add advisor directly (bypass proposal)
addAdvisorDirect(address wallet, uint256 allocation, string role)

// Approve Queen's proposal
approveProposal(uint256 proposalId)

// Reject proposal
rejectProposal(uint256 proposalId, string reason)

// Emergency remove advisor
removeAdvisor(uint256 advisorId, string reason)

// Release tokens for specific advisor
releaseAdvisorTokens(uint256 advisorId)
```

### **For Queen AI**

```solidity
// Propose new advisor
proposeAdvisor(address wallet, uint256 allocation, string role)
```

### **For Advisors**

```solidity
// Claim own vested tokens
claimMyTokens()
```

### **View Functions**

```solidity
// Get pool stats
getPoolStats() → (totalPool, allocated, available, activeCount)

// Get advisor details
getAdvisor(advisorId) → (wallet, allocation, vestingContract, addedAt, active, role)

// Get advisor vesting info
getAdvisorVestingInfo(advisorId) → (total, released, releasable, vested)

// Get all active advisors
getActiveAdvisors() → uint256[] advisorIds

// Get proposal details
getProposal(proposalId) → (proposer, wallet, allocation, role, approved, rejected)
```

---

## 🎯 ADVANTAGES OVER OLD SYSTEM

| Feature | Old System ❌ | New System ✅ |
|---------|--------------|--------------|
| **When advisors added** | Only at deployment | Anytime |
| **Number of advisors** | 1 wallet | 10-20+ wallets |
| **Allocation flexibility** | Fixed 40M to one | Variable per advisor |
| **Add new advisors** | Impossible | Easy |
| **Queen involvement** | None | Can propose |
| **Individual tracking** | No | Yes |
| **Adjust later** | No | Yes (add more) |

---

## 📝 DEPLOYMENT CHECKLIST

### Deployment Order

1. ✅ Deploy `OMKToken`
2. ✅ Deploy `AdvisorsManager` (pass admin + queen addresses)
3. ✅ Deploy `VestingManager` (pass advisorsManager address)
4. ✅ `VestingManager.fundVestingContracts()` - Transfers 40M to AdvisorsManager
5. ⏳ Admin adds advisors as they join the project

### Post-Deployment

```javascript
// Verify pool funded
await advisorsManager.getPoolStats();
// Should show: totalPool = 40M, available = 40M

// Add first advisor
await advisorsManager.addAdvisorDirect(
    advisor1.address,
    ethers.utils.parseEther("2000000"),
    "Marketing Lead"
);

// Verify advisor added
const advisor = await advisorsManager.getAdvisor(0);
console.log(`Advisor: ${advisor.wallet}`);
console.log(`Allocation: ${advisor.allocation}`);
console.log(`Role: ${advisor.role}`);
```

---

## 🔐 SECURITY CONSIDERATIONS

1. **Admin Control**: Only admin can approve/add advisors
2. **Pool Protection**: Cannot allocate more than available
3. **Minimum Reserve**: Prevents pool exhaustion
4. **Individual Vesting**: Each advisor independently secured
5. **Removal Option**: Admin can remove in emergency
6. **Proposal System**: Two-step process for important decisions
7. **Event Logging**: All actions logged on-chain

---

## 🎉 SUMMARY

**The new AdvisorsManager system gives you:**
- ✅ Complete flexibility to add advisors over time
- ✅ Split 40M across as many advisors as needed
- ✅ Each advisor gets fair vesting (12m + 18m)
- ✅ Queen AI can propose, you approve
- ✅ Individual tracking and claiming
- ✅ Full admin control maintained

**No more fixed wallet at deployment!** 🚀

You can now:
1. Launch the project
2. Add advisors as you find them
3. Allocate different amounts based on contribution
4. Have Queen AI suggest advisors
5. Maintain full transparency and control

This is **exactly** what you need for a growing project! 🎯
