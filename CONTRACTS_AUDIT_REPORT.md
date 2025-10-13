# OMK HIVE Smart Contracts - Critical Analysis & Recommendations

**Analysis Date:** 2025-10-10  
**Contracts Reviewed:** OMKToken, TreasuryVault, BeeSpawner, OMKBridge, PrivateSale, QueenController, TokenVesting

---

## 🔴 CRITICAL ISSUES (Must Fix Before Mainnet)

### 1. **OMKToken.sol - Reentrancy Vulnerability in `_beforeTokenTransfer`**
**Location:** Line 295-340  
**Severity:** HIGH

**Issue:**
```solidity
function _beforeTokenTransfer(...) internal virtual override(ERC20, ERC20Pausable) {
    // Queen rate limiting updates state DURING transfer
    todayQueenTransfers += amount;  // State change during transfer
    emit QueenTransfer(from, to, amount, todayQueenTransfers);
}
```

**Problem:** State changes in `_beforeTokenTransfer` can be exploited via reentrancy during token transfers with callbacks.

**Fix:**
- Move rate limiting to a separate `nonReentrant` wrapper function
- Or use OpenZeppelin's `_update` instead of `_beforeTokenTransfer` (Solidity 0.8.20+)

---

### 2. **PrivateSale.sol - Price Calculation Precision Loss**
**Location:** Line 278  
**Severity:** HIGH

**Issue:**
```solidity
uint256 tierPayment = (toAllocate * tierPrices[tier]) / (1000 * 10**12);
```

**Problem:**
- Division before multiplication causes precision loss
- Users might pay LESS than they should
- Example: 100 OMK at tier 0 ($0.100) = Expected $10, Actual might be $9.99

**Fix:**
```solidity
uint256 tierPayment = (toAllocate / 10**12) * tierPrices[tier] / 1000;
// Or use a more robust decimal library
```

---

### 3. **TokenVesting.sol - Admin Role Granted to Token Contract**
**Location:** Line 34  
**Severity:** MEDIUM-HIGH

**Issue:**
```solidity
_grantRole(DEFAULT_ADMIN_ROLE, _token); // Grant role to token contract
```

**Problem:**
- Token contract has full admin control over vesting
- If token contract is compromised, all vesting schedules can be manipulated
- Violates principle of least privilege

**Fix:**
- Remove this line
- Create a dedicated `VESTING_CREATOR_ROLE` instead
- Grant that role to the token contract

---

### 4. **OMKBridge.sol - Missing Nonce Validation**
**Location:** Line 206-246  
**Severity:** HIGH

**Issue:**
```solidity
function releaseTokens(..., bytes32 solanaProof) {
    require(!processedSolanaProofs[solanaProof], "Already processed");
    // No check for transaction ordering or nonce
}
```

**Problem:**
- Relayer can replay transactions in different order
- No mechanism to prevent front-running
- Bridge nonce increments but isn't validated

**Fix:**
```solidity
function releaseTokens(..., bytes32 solanaProof, uint256 expectedNonce) {
    require(bridgeNonce == expectedNonce, "Invalid nonce");
    // ... rest of function
}
```

---

### 5. **TreasuryVault.sol - Month Calculation Flaw**
**Location:** Line 170  
**Severity:** MEDIUM

**Issue:**
```solidity
uint256 currentMonth = block.timestamp / 30 days;
```

**Problem:**
- Months are not exactly 30 days
- Will drift over time
- Creates accounting inconsistencies

**Fix:**
```solidity
uint256 currentMonth = (block.timestamp - deploymentTimestamp) / 30 days;
// Or use a calendar-based approach
```

---

## ⚠️ MEDIUM PRIORITY ISSUES

### 6. **BeeSpawner.sol - Inefficient Array Iteration**
**Location:** Line 282-290, 295-317  
**Severity:** MEDIUM (Gas Optimization)

**Issue:**
```solidity
function getActiveBeeCount() external view returns (uint256) {
    uint256 count = 0;
    for (uint256 i = 0; i < beeCount; i++) {  // O(n) complexity
        if (bees[i].status == BeeStatus.ACTIVE) {
            count++;
        }
    }
    return count;
}
```

**Problem:**
- Linear scan on every call
- Can become very expensive as beeCount grows
- View functions should be cheap

**Fix:**
```solidity
uint256 public activeBeeCount;

function activateBee(...) {
    // ...
    activeBeeCount++;
}

function pauseBee(...) {
    // ...
    activeBeeCount--;
}
```

---

### 7. **QueenController.sol - Pseudo-Random Bee Address Generation**
**Location:** Line 147-160  
**Severity:** MEDIUM

**Issue:**
```solidity
address newBee = address(
    uint160(
        uint256(
            keccak256(
                abi.encodePacked(
                    block.timestamp,
                    block.prevrandao,  // Not truly random
                    msg.sender,
                    totalBees
                )
            )
        )
    )
);
```

**Problem:**
- `block.prevrandao` is predictable
- Validators can manipulate
- Not secure for address generation

**Fix:**
- Use CREATE2 with deterministic salt
- Or use Chainlink VRF for true randomness
- Or just use incremental addressing with a base contract

---

### 8. **PrivateSale.sol - Missing Pause Check in Critical Function**
**Location:** Line 343-365  
**Severity:** MEDIUM

**Issue:**
```solidity
function setupVestingForInvestor(...) 
    external
    onlyRole(SALE_MANAGER_ROLE)
{
    // No whenNotPaused modifier
```

**Problem:**
- Vesting can be set up even when contract is paused
- Inconsistent with other functions

**Fix:**
```solidity
function setupVestingForInvestor(...) 
    external
    onlyRole(SALE_MANAGER_ROLE)
    whenNotPaused  // Add this
{
```

---

## 📋 SUGGESTIONS & BEST PRACTICES

### 9. **Centralization Risk - Too Many Admin Powers**

**Affected Contracts:** All

**Issue:**
- `DEFAULT_ADMIN_ROLE` has too much power
- Single point of failure
- Can pause, unpause, modify critical parameters

**Recommendation:**
```solidity
// Implement a Timelock controller
TimelockController timelock = new TimelockController(
    2 days,  // Delay
    [admin1, admin2],  // Proposers
    [admin1, admin2, admin3],  // Executors
    address(0)  // Admin (no one)
);

// Grant roles to timelock instead of direct admin
_grantRole(DEFAULT_ADMIN_ROLE, address(timelock));
```

---

### 10. **OMKToken.sol - Missing Max Supply Check**

**Issue:**
```solidity
uint256 public constant TOTAL_SUPPLY = 1_000_000_000 * 10**18;

constructor(...) {
    _mint(address(this), TOTAL_SUPPLY);
    // No check that this equals expected supply
}
```

**Suggestion:**
```solidity
// Add verification
uint256 expectedDistribution = FOUNDERS_AMOUNT + 
    PRIVATE_INVESTORS_AMOUNT + 
    ECOSYSTEM_AMOUNT + 
    ADVISORS_AMOUNT + 
    BREAKSWITCH_AMOUNT + 
    TREASURY_AMOUNT + 
    PUBLIC_ACQUISITION_AMOUNT;
    
require(expectedDistribution == TOTAL_SUPPLY, "Supply mismatch");
```

---

### 11. **Missing NatSpec Documentation**

**Affected:** All contracts

**Issue:**
- Incomplete @param tags
- Missing @return tags
- No @dev tags for internal logic

**Example Fix:**
```solidity
/**
 * @notice Purchase OMK tokens with a stablecoin
 * @dev Automatically handles multi-tier purchases
 * @param amount Amount of OMK tokens to purchase (18 decimals)
 * @param paymentToken Address of the stablecoin to pay with (USDC/USDT)
 * @param maxPayment Maximum payment amount willing to pay (6 decimals for USDC)
 * @return success True if purchase was successful
 */
function purchaseTokens(
    uint256 amount,
    address paymentToken,
    uint256 maxPayment
) external nonReentrant whenNotPaused returns (bool success) {
```

---

### 12. **TreasuryVault.sol - Missing Proposal Expiration**

**Issue:**
```solidity
struct Proposal {
    // ...
    uint256 createdAt;
    // No expirationTime
}
```

**Suggestion:**
```solidity
struct Proposal {
    uint256 createdAt;
    uint256 expiresAt;  // Add expiration
    // ...
}

function executeProposal(uint256 proposalId) external {
    require(block.timestamp <= prop.expiresAt, "Proposal expired");
    // ...
}
```

---

### 13. **OMKBridge.sol - Rate Limit Reset Logic**

**Issue:**
```solidity
if (block.timestamp >= lastResetTimestamp + 1 days) {
    dailyBridgeAmount = 0;
    lastResetTimestamp = block.timestamp;  // Sets to current time
}
```

**Problem:**
- Drift accumulates
- Not aligned to UTC days
- Can be gamed by timing transactions

**Better Approach:**
```solidity
uint256 currentDay = block.timestamp / 1 days;
uint256 lastDay = lastResetTimestamp / 1 days;

if (currentDay > lastDay) {
    dailyBridgeAmount = 0;
    lastResetTimestamp = currentDay * 1 days;  // Align to day boundary
}
```

---

## 🔧 GAS OPTIMIZATIONS

### 14. **Use `++i` Instead of `i++` in Loops**

**Locations:** Multiple contracts

**Current:**
```solidity
for (uint256 i = 0; i < length; i++) {
```

**Optimized:**
```solidity
for (uint256 i = 0; i < length; ++i) {
```

**Savings:** ~5 gas per iteration

---

### 15. **Cache Array Length in Loops**

**Example in PrivateSale.sol:**
```solidity
// Current
for (uint256 i = 0; i < investors.length; i++) {

// Optimized
uint256 length = investors.length;
for (uint256 i = 0; i < length; ++i) {
```

---

### 16. **Use Custom Errors Instead of Revert Strings**

**Current:**
```solidity
require(amount > 0, "PrivateSale: Amount must be positive");
```

**Optimized:**
```solidity
error AmountMustBePositive();

if (amount == 0) revert AmountMustBePositive();
```

**Savings:** ~50 gas per revert

---

## 🛡️ SECURITY RECOMMENDATIONS

### 17. **Add Slippage Protection to All Financial Functions**

**Issue:** Only `purchaseTokens` has `maxPayment` parameter

**Recommendation:** Add to:
- Bridge operations
- Liquidity operations
- Any token swap/exchange

---

### 18. **Implement Circuit Breaker Pattern**

**Suggestion:**
```solidity
uint256 public maxDailyVolume = 50_000_000 * 10**18;
uint256 public dailyVolume;

modifier circuitBreaker(uint256 amount) {
    require(dailyVolume + amount <= maxDailyVolume, "Circuit breaker triggered");
    dailyVolume += amount;
    _;
}
```

---

### 19. **Add Events for All State Changes**

**Missing Events:**
- `OMKToken.sol`: No event for rate limit changes
- `BeeSpawner.sol`: No event for metadata updates
- Many setter functions lack events

---

### 20. **Multi-Sig for Critical Functions**

**Current:** Single admin can execute critical functions

**Recommendation:**
- Use Gnosis Safe or similar multi-sig
- Require 3-of-5 signatures for:
  - Emergency shutdown
  - Role changes
  - Parameter updates

---

## 📊 TESTING RECOMMENDATIONS

### Required Test Coverage:

1. **OMKToken.sol:**
   - [ ] Queen rate limit edge cases
   - [ ] Vesting release timing
   - [ ] Private sale integration

2. **OMKBridge.sol:**
   - [ ] Multi-validator consensus
   - [ ] Replay attack prevention
   - [ ] Rate limit bypass attempts

3. **PrivateSale.sol:**
   - [ ] Multi-tier purchase scenarios
   - [ ] Whale limit enforcement
   - [ ] Price calculation accuracy

4. **TreasuryVault.sol:**
   - [ ] Monthly limit resets
   - [ ] Multi-sig approval flows
   - [ ] Emergency withdrawal

---

## ✅ WHAT'S WORKING WELL

1. **Good role-based access control** across all contracts
2. **Reentrancy guards** where needed
3. **Pause functionality** for emergency situations
4. **Rate limiting** on Queen AI operations
5. **Vesting schedules** properly implemented
6. **Multi-sig approvals** for critical operations

---

## 🚀 DEPLOYMENT CHECKLIST

Before mainnet deployment:

- [ ] Fix all CRITICAL issues (#1-5)
- [ ] Resolve MEDIUM priority issues (#6-8)
- [ ] Complete formal security audit (Trail of Bits, OpenZeppelin, Certik)
- [ ] 100% test coverage on all contracts
- [ ] Deploy to testnet for 30+ days
- [ ] Bug bounty program ($50K+ rewards)
- [ ] Multi-sig setup (Gnosis Safe 3-of-5)
- [ ] Timelock controller (48-hour delay)
- [ ] Emergency response plan documented
- [ ] Verify all contracts on Etherscan

---

## 📝 FINAL NOTES

**Overall Assessment:** The contracts are well-structured with good separation of concerns, but have several critical issues that MUST be fixed before mainnet deployment.

**Estimated Time to Production-Ready:** 4-6 weeks with dedicated team

**Recommended Next Steps:**
1. Fix CRITICAL issues immediately
2. Engage professional auditor
3. Expand test suite
4. Deploy to Goerli/Sepolia testnet
5. Run stress tests and attack simulations
6. Set up monitoring and alerting

---

**Generated:** 2025-10-10 by Cascade AI
