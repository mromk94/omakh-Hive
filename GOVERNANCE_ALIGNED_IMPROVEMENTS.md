# Governance-Aligned Contract Improvements

**Date:** October 10, 2025  
**Based On:** CONTRACTS_AUDIT_REPORT.md  
**Focus:** Improvements that strengthen admin control + DAO governance + Security Council

---

## ✅ ALREADY IMPLEMENTED

### Critical Fixes (1-5)
- [x] Reentrancy protection (OMKToken)
- [x] Price precision (PrivateSale)
- [x] Limited admin privilege (TokenVesting)
- [x] Nonce validation (OMKBridge)
- [x] Month calculation (TreasuryVault)

### Governance Framework
- [x] SecurityCouncil contract (7-member with founder permanent)
- [x] Time-limited veto (expires Dec 31, 2027)
- [x] Full documentation and transparency

---

## 🎯 PRIORITY 1: Governance-Critical Improvements

### #8. Add Pause Check to PrivateSale Vesting Setup ⭐
**Alignment:** SecurityCouncil emergency powers  
**Effort:** 5 minutes  
**Impact:** Consistency + security

**Implementation:**
```solidity
function setupVestingForInvestor(address investor) 
    external
    onlyRole(SALE_MANAGER_ROLE)
    whenNotPaused  // ✅ Add this
{
    // ... existing code
}

function batchSetupVesting(address[] calldata investors)
    external
    onlyRole(SALE_MANAGER_ROLE)
    whenNotPaused  // ✅ Add this
{
    // ... existing code
}
```

**Why This Matters:**
- SecurityCouncil can pause ALL operations during emergency
- Prevents vesting setup during exploit
- Consistent with other contract functions

---

### #9. Implement Timelock Controller ⭐⭐⭐
**Alignment:** Founder → DAO transition  
**Effort:** 2-3 hours  
**Impact:** HIGH - Transparency + security

**Implementation:**
```solidity
// Deploy OpenZeppelin TimelockController
import "@openzeppelin/contracts/governance/TimelockController.sol";

TimelockController public timelock;

constructor(...) {
    // Create timelock with 48-hour delay
    address[] memory proposers = new address[](2);
    proposers[0] = founder;
    proposers[1] = address(securityCouncil);
    
    address[] memory executors = new address[](3);
    executors[0] = founder;
    executors[1] = address(securityCouncil);
    executors[2] = address(daoGovernance);
    
    timelock = new TimelockController(
        2 days,      // Minimum delay
        proposers,   // Who can propose
        executors,   // Who can execute
        address(0)   // No admin (self-administered)
    );
    
    // Grant DEFAULT_ADMIN_ROLE to timelock (not directly to founder)
    _grantRole(DEFAULT_ADMIN_ROLE, address(timelock));
}
```

**Benefits:**
- 48-hour notice before any admin action
- Community can exit if they disagree
- Legally defensible ("gave users time to react")
- Industry standard (Compound, Uniswap, Aave use this)

**What Gets Timelocked:**
- Parameter changes
- Role grants/revokes
- Treasury allocations >$100K
- Contract upgrades

**What Bypasses Timelock:**
- Emergency pause (SecurityCouncil 3-of-7)
- Queen AI daily operations
- Normal user transactions

---

### #12. Add Proposal Expiration to TreasuryVault ⭐⭐
**Alignment:** DAO governance quality  
**Effort:** 30 minutes  
**Impact:** MEDIUM - Prevents stale proposals

**Implementation:**
```solidity
struct Proposal {
    // ... existing fields
    uint256 createdAt;
    uint256 expiresAt;  // ✅ Add this
    bool expired;       // ✅ Add this
}

uint256 public constant PROPOSAL_LIFETIME = 30 days;

function createProposal(...) external returns (uint256) {
    uint256 proposalId = proposalCount++;
    
    proposals[proposalId] = Proposal({
        // ... existing fields
        createdAt: block.timestamp,
        expiresAt: block.timestamp + PROPOSAL_LIFETIME,  // ✅ Set expiration
        expired: false
    });
    
    return proposalId;
}

function executeProposal(uint256 proposalId) external {
    Proposal storage prop = proposals[proposalId];
    
    // ✅ Check expiration
    require(block.timestamp <= prop.expiresAt, "TreasuryVault: Proposal expired");
    require(!prop.expired, "TreasuryVault: Proposal marked expired");
    
    // ... rest of execution
}

// Allow marking expired proposals
function expireProposal(uint256 proposalId) external {
    Proposal storage prop = proposals[proposalId];
    require(block.timestamp > prop.expiresAt, "TreasuryVault: Not yet expired");
    prop.expired = true;
    emit ProposalExpired(proposalId);
}
```

**Benefits:**
- Prevents execution of forgotten proposals
- Forces re-approval if circumstances changed
- Cleaner governance (no ancient proposals)

---

## 🛡️ PRIORITY 2: Security Council Features

### #18. Implement Circuit Breaker Pattern ⭐⭐⭐
**Alignment:** SecurityCouncil emergency powers  
**Effort:** 1-2 hours  
**Impact:** HIGH - Automatic protection

**Implementation:**
```solidity
// Add to OMKToken.sol, OMKBridge.sol, PrivateSale.sol

uint256 public maxDailyVolume = 50_000_000 * 10**18;  // 50M OMK/day
uint256 public dailyVolume;
uint256 public lastVolumeReset;

// SecurityCouncil can adjust limits
function setMaxDailyVolume(uint256 newMax) 
    external 
    onlyRole(SECURITY_COUNCIL_ROLE) 
{
    maxDailyVolume = newMax;
    emit MaxDailyVolumeUpdated(newMax);
}

modifier circuitBreaker(uint256 amount) {
    // Reset daily counter
    uint256 currentDay = block.timestamp / 1 days;
    uint256 lastDay = lastVolumeReset / 1 days;
    
    if (currentDay > lastDay) {
        dailyVolume = 0;
        lastVolumeReset = currentDay * 1 days;
    }
    
    // Check circuit breaker
    require(
        dailyVolume + amount <= maxDailyVolume,
        "Circuit breaker: Daily volume limit exceeded"
    );
    
    dailyVolume += amount;
    _;
}

// Apply to critical functions
function transfer(address to, uint256 amount) 
    public 
    override 
    circuitBreaker(amount)  // ✅ Add this
    returns (bool) 
{
    return super.transfer(to, amount);
}

function bridgeTokens(uint256 amount) 
    external 
    circuitBreaker(amount)  // ✅ Add this
{
    // ... bridge logic
}
```

**Benefits:**
- Automatic protection against massive exploits
- SecurityCouncil can pause if circuit breaker trips
- Limits damage before manual intervention

**Parameters (Recommended):**
- OMKToken: 50M OMK/day (5% of supply)
- OMKBridge: 10M OMK/day (1% of supply)
- PrivateSale: 20M OMK/day (whale limit per day)

---

### #17. Add Slippage Protection to Bridge ⭐⭐
**Alignment:** User protection (founder responsibility)  
**Effort:** 30 minutes  
**Impact:** MEDIUM - Protects users

**Implementation:**
```solidity
// Add to OMKBridge.sol

function bridgeTokens(
    uint256 amount,
    uint256 minAmountOut  // ✅ Add slippage protection
) external nonReentrant whenNotPaused {
    // ... existing checks
    
    // Calculate fee
    uint256 fee = (amount * bridgeFeePercent) / 10000;
    uint256 amountAfterFee = amount - fee;
    
    // ✅ Check slippage
    require(
        amountAfterFee >= minAmountOut,
        "OMKBridge: Slippage tolerance exceeded"
    );
    
    // ... rest of bridge logic
}
```

---

## 📊 PRIORITY 3: Transparency & Governance Quality

### #19. Add Events for All State Changes ⭐⭐
**Alignment:** Transparency (governance principle)  
**Effort:** 1 hour  
**Impact:** MEDIUM - Better monitoring

**Add Missing Events:**

**OMKToken.sol:**
```solidity
event QueenRateLimitUpdated(uint256 oldLimit, uint256 newLimit);
event QueenRateLimitEnabled(bool enabled);

function setQueenDailyLimit(uint256 newLimit) external onlyRole(DEFAULT_ADMIN_ROLE) {
    uint256 oldLimit = MAX_QUEEN_DAILY_TRANSFER;
    MAX_QUEEN_DAILY_TRANSFER = newLimit;
    emit QueenRateLimitUpdated(oldLimit, newLimit);  // ✅ Add event
}
```

**TreasuryVault.sol:**
```solidity
event MonthlyLimitUpdated(Category indexed category, uint256 oldLimit, uint256 newLimit);
event RequiredApprovalsUpdated(uint256 oldRequired, uint256 newRequired);

function setMonthlyLimit(Category category, uint256 newLimit) 
    external 
    onlyRole(DEFAULT_ADMIN_ROLE) 
{
    uint256 oldLimit = monthlyLimits[category];
    monthlyLimits[category] = newLimit;
    emit MonthlyLimitUpdated(category, oldLimit, newLimit);  // ✅ Add event
}
```

**SecurityCouncil.sol:**
```solidity
event EmergencyThresholdChanged(uint256 oldThreshold, uint256 newThreshold);
event CouncilSizeChanged(uint256 oldSize, uint256 newSize);
```

---

### #10. Add Supply Verification Check ⭐
**Alignment:** Transparency + correctness  
**Effort:** 10 minutes  
**Impact:** LOW - Sanity check

**Implementation:**
```solidity
// Add to OMKToken.sol constructor

constructor(...) {
    // ... existing code
    
    // ✅ Verify total supply matches allocation
    uint256 expectedDistribution = 
        FOUNDERS_AMOUNT +
        PRIVATE_INVESTORS_AMOUNT +
        ECOSYSTEM_AMOUNT +
        ADVISORS_AMOUNT +
        BREAKSWITCH_AMOUNT +
        TREASURY_AMOUNT +
        PUBLIC_ACQUISITION_AMOUNT;
    
    require(
        expectedDistribution == TOTAL_SUPPLY,
        "OMKToken: Supply allocation mismatch"
    );
    
    emit SupplyVerified(TOTAL_SUPPLY, expectedDistribution);
}
```

---

### #13. Fix Bridge Rate Limit Reset Logic ⭐
**Alignment:** Correctness  
**Effort:** 10 minutes  
**Impact:** LOW - Better logic

**Current Issue:**
```solidity
// Drifts over time
if (block.timestamp >= lastResetTimestamp + 1 days) {
    dailyBridgeAmount = 0;
    lastResetTimestamp = block.timestamp;  // ❌ Can drift
}
```

**Better Approach:**
```solidity
// Aligns to day boundaries
uint256 currentDay = block.timestamp / 1 days;
uint256 lastDay = lastResetTimestamp / 1 days;

if (currentDay > lastDay) {
    dailyBridgeAmount = 0;
    lastResetTimestamp = currentDay * 1 days;  // ✅ Aligned
}
```

---

## 🔧 PRIORITY 4: Gas Optimizations (Lower Priority)

### #14. Use `++i` in Loops
**Effort:** 10 minutes (find/replace)  
**Savings:** ~5 gas per iteration  
**Contracts:** All (15+ locations)

### #15. Cache Array Lengths
**Effort:** 15 minutes  
**Savings:** ~100 gas per loop  
**Contracts:** PrivateSale, BeeSpawner, TreasuryVault

### #16. Custom Errors Instead of Strings
**Effort:** 2-3 hours (many locations)  
**Savings:** ~50 gas per revert  
**Contracts:** All (~100+ require statements)

---

## 📋 IMPLEMENTATION PRIORITY ORDER

### **This Week (High Impact + Governance-Critical)**
1. ✅ **#8 - Add pause check** (5 min) - Quick win
2. ✅ **#13 - Fix bridge reset logic** (10 min) - Quick win
3. ✅ **#10 - Supply verification** (10 min) - Quick win
4. ⭐ **#9 - Timelock controller** (2-3 hours) - CRITICAL for governance
5. ⭐ **#18 - Circuit breaker** (1-2 hours) - CRITICAL for security
6. ⭐ **#12 - Proposal expiration** (30 min) - Governance quality

### **Next Week (Security & Transparency)**
7. **#17 - Slippage protection** (30 min)
8. **#19 - Add missing events** (1 hour)

### **Before Mainnet (Gas Optimization)**
9. **#14 - Loop optimizations** (10 min)
10. **#15 - Cache array lengths** (15 min)
11. **#16 - Custom errors** (2-3 hours)

---

## 🎯 WHY THESE FIT YOUR GOVERNANCE

### Timelock Controller (#9)
✅ **Founder maintains control** BUT with transparency  
✅ **Community gets 48-hour notice** before changes  
✅ **Legally defensible** ("gave users warning")  
✅ **Industry standard** (Uniswap, Compound use this)  
✅ **Smooth transition** to DAO (already in place)

### Circuit Breaker (#18)
✅ **SecurityCouncil feature** (3-of-7 to adjust limits)  
✅ **Founder on council** (permanent seat)  
✅ **Automatic protection** (limits damage)  
✅ **Shows responsibility** (protecting users)

### Proposal Expiration (#12)
✅ **Better governance quality**  
✅ **Forces re-approval** if stale  
✅ **Cleaner DAO** (no ancient proposals)

### Events Everywhere (#19)
✅ **Full transparency** (all actions on-chain)  
✅ **Community can monitor** founder actions  
✅ **Builds trust** (nothing hidden)

---

## ✅ WHAT TO IMPLEMENT NOW

**Recommendation:** Implement #8, #10, #13 today (25 minutes total)  
**Then:** #9 (Timelock) and #18 (Circuit Breaker) this week  
**Result:** Significantly stronger governance + security

All of these align with your:
- ✅ Permanent Security Council seat
- ✅ Transparent founder control
- ✅ Smooth transition to DAO
- ✅ User protection responsibility

---

**Status:** Ready to implement  
**Effort:** ~1 day for Priority 1 + 2  
**Impact:** Major governance & security improvements
