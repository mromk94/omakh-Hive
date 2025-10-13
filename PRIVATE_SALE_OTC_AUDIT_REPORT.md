# 🔒 PRIVATE SALE & OTC AUDIT REPORT

**Date:** October 12, 2025  
**Status:** 🟡 **REQUIRES FIXES BEFORE DEPLOYMENT**

---

## 📋 EXECUTIVE SUMMARY

**Reviewed:**
- ✅ PrivateSale.sol, PrivateInvestorRegistry.sol, OMKDispenser.sol
- ✅ VestingManager.sol, TokenVesting.sol
- ✅ 4 documentation files

**Issues Found:**
- 🔴 **CRITICAL:** 3 issues
- 🟠 **HIGH:** 4 issues  
- 🟡 **MEDIUM:** 8 issues
- 🟢 **LOW:** 3 issues

---

## 🔴 CRITICAL ISSUES

### **C-1: PrivateSale - Vesting Setup Can Lock Tokens Forever**

**File:** `PrivateSale.sol:345-368`  
**Severity:** 🔴 CRITICAL

**Problem:**
```solidity
// WRONG ORDER - sets address before operations complete
investments[investor].vestingContract = address(vesting); // Line 355
omkToken.safeTransfer(address(vesting), amount); // Line 358 - could fail
vesting.createVestingSchedule(...); // Line 361 - could fail
```

**Impact:** If transfer/schedule fails, address is set but vesting broken. Cannot retry.

**Fix:**
```solidity
// Move line 355 to AFTER line 367 (end of function)
// Check balance first:
require(omkToken.balanceOf(address(this)) >= amount, "Insufficient balance");
```

---

### **C-2: OMKDispenser - No Price Change Limits**

**File:** `OMKDispenser.sol:305-318`  
**Severity:** 🔴 CRITICAL

**Problem:**
```solidity
function updateTokenPrice(address token, uint256 newPrice) external onlyRole(ORACLE_ROLE) {
    tokenPricesUSD[token] = newPrice; // No validation, no time-lock
}
```

**Impact:** Malicious oracle can manipulate prices instantly for arbitrage.

**Fix:**
```solidity
uint256 public constant MAX_PRICE_CHANGE_PCT = 20; // 20% max
mapping(address => uint256) public lastPriceUpdate;
uint256 public constant PRICE_UPDATE_DELAY = 30 minutes;

function updateTokenPrice(address token, uint256 newPrice) external onlyRole(ORACLE_ROLE) {
    require(block.timestamp >= lastPriceUpdate[token] + PRICE_UPDATE_DELAY, "Too soon");
    uint256 oldPrice = tokenPricesUSD[token];
    uint256 maxChange = (oldPrice * MAX_PRICE_CHANGE_PCT) / 100;
    require(newPrice >= oldPrice - maxChange && newPrice <= oldPrice + maxChange, "Change too large");
    tokenPricesUSD[token] = newPrice;
    lastPriceUpdate[token] = block.timestamp;
}
```

---

### **C-3: Documentation/Implementation Mismatch**

**Files:** Multiple  
**Severity:** 🔴 CRITICAL

**Issues:**
1. **OTC Payment Flow Missing:** `OTC_PAYMENT_FLOW_IMPLEMENTATION.md` describes payment step NOT implemented in frontend
2. **Current:** User submits → "Wait for email"
3. **Should be:** User submits → Pay crypto → Auto-verify → Confirm
4. **Advisors Amount:** Docs unclear on 20M vs 40M (contract has 40M)

**Fix:** Implement payment verification step, update all documentation.

---

## 🟠 HIGH SEVERITY ISSUES

### **H-1: PrivateInvestorRegistry - Unbounded Investor Array**

**File:** `PrivateInvestorRegistry.sol:108`  
**Severity:** 🟠 HIGH

**Problem:**
```solidity
investorList.push(wallet); // No limit on array size
```

**Impact:** With 10,000+ investors, `distributeToAll()` and `getAllInvestors()` will fail due to gas limits.

**Fix:**
```solidity
uint256 public constant MAX_INVESTORS = 1000;
require(investorList.length < MAX_INVESTORS, "Max investors reached");
```

---

### **H-2: TokenVesting - No Emergency Pause**

**File:** `TokenVesting.sol`  
**Severity:** 🟠 HIGH

**Problem:** No `Pausable` functionality. If vulnerability found, cannot stop vesting releases.

**Fix:**
```solidity
import "@openzeppelin/contracts/security/Pausable.sol";
contract TokenVesting is AccessControl, Pausable {
    function release(address beneficiary) external whenNotPaused { /*...*/ }
    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) { _pause(); }
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) { _unpause(); }
}
```

---

### **H-3: PrivateSale - No USD Raise Cap**

**File:** `PrivateSale.sol:208`  
**Severity:** 🟠 HIGH

**Problem:** Only checks token limit, not USD amount. Could raise more than $12.25M target.

**Fix:**
```solidity
uint256 public constant MAX_RAISE_USD = 12_250_000 * 10**6;
uint256 totalRaisedUSD = getTotalRaisedUSD();
require(totalRaisedUSD + paymentRequired <= MAX_RAISE_USD, "Max raise exceeded");
```

---

### **H-4: VestingManager - Advisors Manager Upgrade Issue**

**File:** `VestingManager.sol:242-248`  
**Severity:** 🟠 HIGH

**Problem:** `updateAdvisorsManager()` changes address but doesn't migrate 40M tokens from old manager.

**Fix:** Document clearly that changing address requires manual token migration, or implement migration function.

---

## 🟡 MEDIUM SEVERITY ISSUES

### **M-1: PrivateSale - No Minimum Purchase**
**Fix:** `uint256 public constant MIN_PURCHASE = 1000 * 10**18;`

### **M-2: OMKDispenser - Daily Limit Exploitable**
**Issue:** Limits reset at midnight. User can spend $500k at 11:59 PM, then $500k at 12:01 AM.
**Fix:** Implement rolling 24-hour window or document as known behavior.

### **M-3: TokenVesting - Cliff % Hardcoded**
**Issue:** Line 165: `uint256 cliffAmount = schedule.totalAmount / 4;` always 25%.
**Fix:** Make cliff percentage configurable parameter.

### **M-4: PrivateSale - Tier Math Precision**
**Issue:** Division before multiplication in `calculatePayment()` line 280.
**Fix:** Rearrange: `(toAllocate * tierPrices[tier]) / (1000 * 10**12)`

### **M-5: PrivateInvestorRegistry - Expensive Removal**
**Issue:** O(n) complexity in `removeInvestor()` loop.
**Fix:** Document as emergency-only operation.

### **M-6: PrivateSale - Missing Vesting Completion Event**
**Fix:** Add `event VestingSetupComplete(address indexed investor, address vestingContract);`

### **M-7: All Contracts - Missing Natspec**
**Issue:** Many functions lack `@param` and `@return` documentation.
**Fix:** Add comprehensive Natspec comments.

### **M-8: PrivateInvestorRegistry - No Investor Limit Warning**
**Issue:** No check/warning for approaching gas limits with many investors.
**Fix:** Emit warning event when approaching 500+ investors.

---

## 🟢 LOW PRIORITY ISSUES

### **L-1: PrivateSale - Investor Data Public**
**Issue:** Anyone can query `getInvestorInfo()` to see purchase amounts.
**Fix:** Document that investment amounts are intentionally public, or add privacy mode.

### **L-2: OMKDispenser - Decimal Confusion**
**Issue:** Comments say 8 decimals but USD prices should be 6 decimals for USDC compatibility.
**Fix:** Clarify decimal standards in comments.

### **L-3: All Contracts - Missing Integration Tests**
**Issue:** No evidence of end-to-end integration tests.
**Fix:** Create comprehensive test suite covering all flows.

---

## ✅ WHAT WORKS WELL

1. **✅ Access Control:** All contracts use OpenZeppelin `AccessControl` correctly
2. **✅ ReentrancyGuard:** Applied appropriately in critical functions
3. **✅ SafeERC20:** Used for all token transfers
4. **✅ Event Emissions:** Most state changes emit events
5. **✅ Emergency Withdraw:** Properly blocked after TGE in PrivateInvestorRegistry
6. **✅ Batch Operations:** Present for whitelisting and distribution
7. **✅ View Functions:** Comprehensive read functions for all contracts

---

## 📊 FLOW ANALYSIS

### **Private Sale Flow:** ✅ SOUND
```
User KYC → Whitelist → Purchase (pay stablecoin) → Tokens held in contract 
→ Admin sets up vesting → Tokens move to vesting contract → Cliff period 
→ User claims vested tokens
```

**Issues:** Step "Admin sets up vesting" has Critical-1 bug.

### **OTC/Private Investor Flow:** 🟡 INCOMPLETE
```
Admin registers investor → TGE execution → Distribution to wallets
```

**Issues:** Missing payment verification step in OTC docs/frontend.

### **Dispenser Flow:** ✅ SOUND
```
User sends ETH/USDT/USDC → Contract calculates OMK amount → Transfers OMK → Tracks limits
```

**Issues:** High-2 (no price change limits).

---

## 🎯 PRIORITY FIXES

### **Must Fix Before Deployment:**
1. 🔴 C-1: Reorder vesting setup operations
2. 🔴 C-2: Add price change limits to OMKDispenser
3. 🔴 C-3: Implement OTC payment verification
4. 🟠 H-2: Add Pausable to TokenVesting
5. 🟠 H-3: Add USD raise cap to PrivateSale

### **Should Fix Before Launch:**
6. 🟠 H-1: Add investor limit check
7. 🟠 H-4: Document advisors manager upgrade process
8. 🟡 M-1: Add minimum purchase amount
9. 🟡 M-3: Make cliff percentage configurable

### **Nice to Have:**
10. 🟡 M-2, M-4, M-5, M-6, M-7, M-8
11. 🟢 All LOW priority items

---

## 🔧 RECOMMENDED ACTIONS

**Immediate (Today):**
1. Fix C-1 (vesting setup order)
2. Fix C-2 (price limits)
3. Add H-2 (pausable vesting)

**This Week:**
4. Implement C-3 (OTC payment verification)
5. Fix H-3 (USD cap)
6. Add H-1 (investor limit)

**Before Mainnet:**
7. Comprehensive testing
8. External security audit
9. Update all documentation
10. Integration tests

---

## 📞 SUMMARY

**Overall Assessment:** 🟡 **REQUIRES FIXES**

**Contracts are well-structured** with proper access control, reentrancy protection, and OpenZeppelin standards. However, **3 critical issues must be fixed** before deployment:

1. Vesting setup can lock tokens
2. Price manipulation risk  
3. OTC payment flow incomplete

**Recommendation:** Fix critical and high-severity issues, then conduct external audit before mainnet deployment.

**Estimated Fix Time:** 
- Critical: 4-6 hours
- High: 6-8 hours
- Total: 10-14 hours of development

---

**Audit Complete** ✅  
**Next:** Implement fixes and re-audit
