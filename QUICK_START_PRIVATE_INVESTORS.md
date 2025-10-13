# Quick Start: Private Investor Management

**For:** Founder/Admin  
**Purpose:** Manage pre-TGE OTC investors  
**Contract:** PrivateInvestorRegistry.sol

---

## 🎯 Quick Access

**Frontend:** Type or click "Manage Private Investors" in chat  
**Contract Functions:** See below  
**Admin Required:** Your founder wallet

---

## 📋 3-Step Process

### Step 1: Register Investors (Pre-TGE)

**In Frontend:**
1. Open chat interface
2. Click "Manage Private Investors" (admin only)
3. Click "+ Register Investor"
4. Enter details:
   - Wallet address (where they'll receive tokens)
   - OMK allocation (e.g., 1,000,000)
   - Amount paid in USD (e.g., 100,000)
   - Investor ID (e.g., "INV-001")
5. Confirm & sign transaction

**In Solidity (Direct):**
```solidity
// Connect with your founder wallet
PrivateInvestorRegistry registry = PrivateInvestorRegistry(REGISTRY_ADDRESS);

registry.registerInvestor(
    0x742d35ab9...529fa,     // wallet
    1000000 * 10**18,         // 1M OMK
    100000 * 10**6,           // $100K USD (6 decimals)
    100000,                   // $0.10 per token (6 decimals)
    "INV-001"                 // ID
);
```

**Repeat for all investors** ⟳

---

### Step 2: Execute TGE (One-Time Action)

**⚠️ CRITICAL:** This is irreversible! Can only be done ONCE.

**Before executing:**
- ✅ All investors registered
- ✅ Contract has enough OMK tokens
- ✅ You're absolutely sure (can't add more investors after)

**In Frontend:**
1. Click "Execute TGE" button
2. Review summary carefully
3. Type "EXECUTE TGE" to confirm
4. Sign transaction

**In Solidity:**
```solidity
// First, make sure contract has tokens
omkToken.transfer(address(registry), 100_000_000 * 10**18);

// Then execute TGE
registry.executeTGE();
```

---

### Step 3: Distribute Tokens (Post-TGE)

**Option A: Distribute to Single Investor**
```solidity
registry.distributeToInvestor(0x742d35ab9...529fa);
```

**Option B: Batch Distribute (Recommended)**
```solidity
address[] memory wallets = new address[](3);
wallets[0] = 0x742d35ab9...529fa;
wallets[1] = 0x8f3a...29bc;
wallets[2] = 0x1c4e...88de;

registry.batchDistribute(wallets);
```

**Option C: Distribute All (Gas Intensive)**
```solidity
registry.distributeToAll();
// ⚠️ Use carefully - may hit gas limits if many investors
```

**In Frontend:**
- Click "Distribute Tokens"
- Choose individual or "Distribute to All"
- Confirm transaction

---

## ✅ Verification Steps

### After Registration
```solidity
// Check investor details
(uint256 allocation, , , , bool distributed, , , ) = 
    registry.getInvestor(investorWallet);

console.log("Allocation:", allocation);
console.log("Distributed:", distributed);
```

### After TGE
```solidity
// Check TGE status
bool executed = registry.tgeExecuted();
uint256 timestamp = registry.tgeTimestamp();

console.log("TGE Executed:", executed);
console.log("TGE Time:", timestamp);
```

### After Distribution
```solidity
// Check stats
(
    uint256 totalInvestors,
    uint256 totalAllocated,
    uint256 totalDistributed,
    uint256 pending,
    ,
) = registry.getStats();

console.log("Total:", totalAllocated);
console.log("Distributed:", totalDistributed);
console.log("Pending:", pending);
```

---

## 🚨 Common Issues & Solutions

### Issue 1: "TGE already executed"
**Problem:** Trying to register investor after TGE  
**Solution:** Cannot add investors after TGE. This is by design.

### Issue 2: "Insufficient tokens"
**Problem:** Contract doesn't have enough OMK for TGE  
**Solution:**
```solidity
// Transfer tokens to registry first
omkToken.transfer(address(registry), TOTAL_ALLOCATED);
```

### Issue 3: "Already distributed"
**Problem:** Trying to distribute to same investor twice  
**Solution:** Check distribution status first:
```solidity
(, , , , bool distributed, , , ) = registry.getInvestor(wallet);
if (!distributed) {
    registry.distributeToInvestor(wallet);
}
```

### Issue 4: "Not registered"
**Problem:** Wallet not in investor list  
**Solution:** Register investor first (if pre-TGE)

---

## 📊 Example Workflow

### Scenario: 3 Private Investors

**Investor 1:**
- Wallet: 0xAAA...AAA
- Allocation: 2,000,000 OMK
- Paid: $200,000
- Price: $0.10/OMK

**Investor 2:**
- Wallet: 0xBBB...BBB
- Allocation: 1,000,000 OMK
- Paid: $100,000
- Price: $0.10/OMK

**Investor 3:**
- Wallet: 0xCCC...CCC
- Allocation: 500,000 OMK
- Paid: $50,000
- Price: $0.10/OMK

**Total: 3,500,000 OMK**

```solidity
// 1. Register all investors
registry.registerInvestor(0xAAA, 2000000e18, 200000e6, 100000, "INV-001");
registry.registerInvestor(0xBBB, 1000000e18, 100000e6, 100000, "INV-002");
registry.registerInvestor(0xCCC, 500000e18, 50000e6, 100000, "INV-003");

// 2. Transfer tokens to registry
omkToken.transfer(address(registry), 3500000e18);

// 3. Verify balance
uint256 balance = omkToken.balanceOf(address(registry));
// balance should be ≥ 3,500,000 OMK

// 4. Execute TGE
registry.executeTGE();

// 5. Distribute to all
address[] memory all = new address[](3);
all[0] = 0xAAA;
all[1] = 0xBBB;
all[2] = 0xCCC;
registry.batchDistribute(all);

// 6. Verify distributions
// 0xAAA should have exactly 2,000,000 OMK
// 0xBBB should have exactly 1,000,000 OMK
// 0xCCC should have exactly 500,000 OMK
```

---

## 🔐 Security Checklist

**Before Registration:**
- [ ] Verify wallet address is correct (double-check!)
- [ ] Confirm allocation amount
- [ ] Confirm payment received
- [ ] Document investor details off-chain

**Before TGE:**
- [ ] All investors registered
- [ ] Registry contract has sufficient OMK
- [ ] Reviewed investor list
- [ ] Ready to proceed (irreversible!)

**Before Distribution:**
- [ ] TGE executed
- [ ] Verify each wallet address again
- [ ] Check gas estimates for batch operations
- [ ] Ready to distribute

**After Distribution:**
- [ ] Verify balances in investor wallets
- [ ] Confirm totalDistributed matches totalAllocated
- [ ] Document completion
- [ ] Notify investors

---

## 💡 Pro Tips

1. **Batch Operations:** Use `batchDistribute()` for multiple investors to save gas
2. **Double-Check Addresses:** One wrong character = tokens lost forever
3. **Test First:** Deploy to testnet and test full workflow
4. **Document Everything:** Keep off-chain records of all investors
5. **Verify Math:** Always check that allocation = (paid / price)

---

## 📞 Need Help?

**Documentation:**
- Full guide: `/PRIVATE_INVESTOR_OTC_FLOW.md`
- Contract code: `/contracts/ethereum/src/core/PrivateInvestorRegistry.sol`
- Frontend component: `/omk-frontend/components/cards/PrivateInvestorCard.tsx`

**Common Commands:**
```bash
# Compile contracts
forge build

# Run tests
forge test

# Deploy to testnet
forge script DeployPrivateInvestorRegistry --rpc-url sepolia

# Verify contract
forge verify-contract <ADDRESS> PrivateInvestorRegistry --chain sepolia
```

---

**Quick Reference Complete** ✅  
**Ready to manage private investors!** 🚀
