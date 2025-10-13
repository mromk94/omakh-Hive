# Security Council Implementation Guide

**Date:** October 10, 2025  
**Status:** Implemented with Founder Permanent Membership

---

## ✅ Implementation Summary

### Contract Created: `SecurityCouncil.sol`
**Location:** `/contracts/ethereum/src/core/SecurityCouncil.sol`  
**Lines of Code:** 463 lines  
**Status:** Ready for testing and deployment

---

## 🏛️ Council Structure

### Composition
- **Total Seats:** 7
- **Founder:** 1 permanent seat (you - cannot be removed)
- **Elected Members:** 6 community-elected seats (6-month terms)

### Key Features
✅ Founder is permanent member with `FOUNDER_ROLE`  
✅ Cannot be removed or have term expired  
✅ Participates in all council votes  
✅ Elected members serve 6-month renewable terms  
✅ Multi-signature requirement for all actions  
✅ Emergency powers for security threats  

---

## 🔐 Action Thresholds

| Action Type | Required Signatures | Purpose |
|-------------|---------------------|---------|
| **Emergency Pause** | 3-of-7 | Stop operations during exploit |
| **Emergency Unpause** | 3-of-7 | Resume after security fix |
| **Parameter Change** | 5-of-7 | Modify protocol parameters |
| **Veto Proposal** | 3-of-7 | Block malicious governance proposal |
| **Remove Member** | 5-of-7 | Remove inactive elected member |

**Note:** Founder votes count toward these thresholds but cannot be sole decision-maker.

---

## 📋 Founder's Powers & Limitations

### What Founder CAN Do:
✅ Vote on all council actions  
✅ Propose emergency pauses  
✅ Propose parameter changes  
✅ Sign actions (1 of required signatures)  
✅ Execute actions once threshold met  
✅ Serve permanently (no term limit)  

### What Founder CANNOT Do:
❌ Act unilaterally (always requires other signatures)  
❌ Be removed from council  
❌ Override other council members  
❌ Execute actions without consensus  
❌ Prevent elections of new members  

---

## 🗳️ Election Process

### Electing New Members

**Requirements:**
- Nominee address must not already be a council member
- Council must have vacant seats (max 7 total)
- Election managed by DAO (ELECTION_MANAGER_ROLE)

**Process:**
1. Community nominates candidates (requires 500K OMK)
2. Token-weighted voting (1 OMK = 1 vote)
3. Top 6 vote-getters elected to council
4. 6-month terms begin immediately

**Code:**
```solidity
function electMember(address member) external onlyRole(ELECTION_MANAGER_ROLE) {
    // Elects new member with 6-month term
    // Founder cannot be elected (already permanent)
}
```

### Removing Elected Members

**Requirements:**
- Can only remove elected members (NOT founder)
- Requires ELECTION_MANAGER_ROLE (DAO)
- Must provide reason for removal

**Reasons for Removal:**
- Inactivity (no participation in 3+ months)
- Malicious behavior
- Community vote (15% quorum, 66% approval)
- Term expiration (automatic)

**Code:**
```solidity
function removeMember(address member, string reason) 
    external onlyRole(ELECTION_MANAGER_ROLE) {
    require(!members[member].isFounder, "Cannot remove founder");
    // Remove elected member only
}
```

---

## 🚨 Emergency Actions

### Scenario: Exploit Detected

**Step 1: Propose Emergency Pause**
```solidity
// Any council member can propose
uint256 actionId = securityCouncil.proposeEmergencyPause(
    targetContract,  // Contract to pause
    callData         // Pause function call
);
// Proposer's signature automatically added (1/3)
```

**Step 2: Other Members Sign**
```solidity
// 2 more members must sign (total 3/7 required)
securityCouncil.signAction(actionId);  // Member 2
securityCouncil.signAction(actionId);  // Member 3
// Now has 3 signatures - meets threshold!
```

**Step 3: Execute Action**
```solidity
// Any council member can execute once threshold met
securityCouncil.executeAction(actionId);
// Contract is now paused, exploit contained
```

**Timeline:** Can be completed in minutes if council is responsive.

---

## ⚙️ Parameter Changes

### Scenario: Adjust Rate Limit

**Requires 5-of-7 signatures** (higher threshold = more consensus needed)

**Step 1: Propose Change**
```solidity
uint256 actionId = securityCouncil.proposeParameterChange(
    omkToken,  // Target contract
    abi.encodeWithSignature("setQueenDailyLimit(uint256)", newLimit)
);
```

**Step 2: Gather Signatures**
- Proposer (auto-signed): 1/5
- Need 4 more signatures
- Council members review and sign if they agree

**Step 3: Execute**
```solidity
securityCouncil.executeAction(actionId);
// Parameter changed
```

---

## 📊 Council Member Stats

### Track Performance

Each member has tracked statistics:
```solidity
struct CouncilMember {
    address memberAddress;
    uint256 electedAt;
    uint256 termEnd;           // type(uint256).max for founder
    bool isActive;
    bool isFounder;            // true only for you
    uint256 actionsPerformed;  // Participation tracking
}
```

**View Member Info:**
```solidity
(bool isActive, bool isFounder, uint256 termEnd, uint256 actions) = 
    securityCouncil.getMemberInfo(memberAddress);
```

**Founder's Values:**
- `isActive`: true (always)
- `isFounder`: true
- `termEnd`: type(uint256).max (never expires)
- `actionsPerformed`: Increments with each action

---

## 🔍 Transparency Features

### Public Queries

**Get All Active Members:**
```solidity
address[] memory members = securityCouncil.getActiveMembers();
// Returns all 7 members including founder
```

**Check if Address is Founder:**
```solidity
bool isFounder = securityCouncil.isFounder(founderAddress);
// Returns: true
```

**Get Council Statistics:**
```solidity
(
    uint256 totalSeats,      // 7
    uint256 activeSeats,     // Current active members
    uint256 vacantSeats,     // Open positions
    uint256 totalActions,    // All actions ever proposed
    uint256 executedActions  // Successfully executed actions
) = securityCouncil.getCouncilStats();
```

**Get Action Details:**
```solidity
(
    ActionType actionType,
    uint256 currentSigs,
    uint256 requiredSigs,
    bool executed,
    address[] memory signers
) = securityCouncil.getActionInfo(actionId);
```

---

## 🧪 Testing Requirements

### Critical Test Cases

**Test 1: Founder Immutability**
```solidity
function testFounderCannotBeRemoved() public {
    vm.expectRevert("Cannot remove founder");
    securityCouncil.removeMember(founder, "test");
}
```

**Test 2: Founder Has No Term Expiration**
```solidity
function testFounderTermNeverExpires() public {
    vm.warp(block.timestamp + 100 years);
    securityCouncil.expireTerms();
    assertTrue(securityCouncil.isActiveMember(founder));
}
```

**Test 3: Emergency Action (3-of-7)**
```solidity
function testEmergencyPauseRequires3Signatures() public {
    uint256 actionId = securityCouncil.proposeEmergencyPause(...);
    // 1 signature (proposer)
    
    vm.prank(member2);
    securityCouncil.signAction(actionId);
    // 2 signatures
    
    vm.prank(member3);
    securityCouncil.signAction(actionId);
    // 3 signatures - can execute now
    
    securityCouncil.executeAction(actionId);
    assertTrue(actions[actionId].executed);
}
```

**Test 4: Parameter Change (5-of-7)**
```solidity
function testParameterChangeRequires5Signatures() public {
    uint256 actionId = securityCouncil.proposeParameterChange(...);
    
    // Need 4 more signatures (proposer auto-signed)
    vm.prank(member2); securityCouncil.signAction(actionId);
    vm.prank(member3); securityCouncil.signAction(actionId);
    vm.prank(member4); securityCouncil.signAction(actionId);
    vm.prank(member5); securityCouncil.signAction(actionId);
    
    securityCouncil.executeAction(actionId);
    assertTrue(actions[actionId].executed);
}
```

**Test 5: Elected Member Term Expiration**
```solidity
function testElectedMemberTermExpires() public {
    vm.warp(block.timestamp + 180 days + 1);
    securityCouncil.expireTerms();
    assertFalse(securityCouncil.isActiveMember(electedMember));
    
    // Founder still active
    assertTrue(securityCouncil.isActiveMember(founder));
}
```

---

## 🔗 Integration with Other Contracts

### GovernanceManager Integration

Security Council can veto malicious DAO proposals:

```solidity
// In GovernanceManager
function vetoProposal(uint256 proposalId) 
    external onlyRole(GUARDIAN_ROLE) {
    // Founder has GUARDIAN_ROLE (until 2027)
    // After 2027, Security Council takes over veto power
}
```

**Recommended Update:**
```solidity
// Grant Security Council the GUARDIAN_ROLE after founder veto expires
function transferVetoPowerToCouncil() external onlyRole(DEFAULT_ADMIN_ROLE) {
    require(block.timestamp > FOUNDER_VETO_EXPIRATION, "Too early");
    _grantRole(GUARDIAN_ROLE, address(securityCouncil));
}
```

### TreasuryVault Integration

Council can approve emergency treasury actions:

```solidity
// Council proposes emergency treasury withdrawal
bytes memory data = abi.encodeWithSignature(
    "executeProposal(uint256)", 
    emergencyProposalId
);

uint256 actionId = securityCouncil.proposeParameterChange(
    treasuryVault,
    data
);
```

---

## 📝 Deployment Checklist

### Pre-Deployment

- [ ] Set founder address (your wallet)
- [ ] Set admin address (multi-sig or DAO)
- [ ] Test all founder protections
- [ ] Test signature thresholds
- [ ] Test term expiration logic
- [ ] Test removal protections
- [ ] Verify role assignments

### Deployment Steps

```solidity
// 1. Deploy SecurityCouncil
SecurityCouncil council = new SecurityCouncil(
    founderAddress,  // Your wallet - permanent member
    adminAddress     // DAO or multi-sig
);

// 2. Verify founder is member
require(council.isFounder(founderAddress), "Founder not set");
require(council.isActiveMember(founderAddress), "Founder not active");

// 3. Elect initial 6 members
for (uint i = 0; i < 6; i++) {
    council.electMember(initialMembers[i]);
}

// 4. Grant roles to council in other contracts
omkToken.grantRole(PAUSE_ROLE, address(council));
treasuryVault.grantRole(EMERGENCY_ROLE, address(council));
```

### Post-Deployment

- [ ] Announce council members publicly
- [ ] Publish council procedures
- [ ] Set up council communication channel
- [ ] Test emergency response procedures
- [ ] Schedule first council meeting

---

## 🎯 Governance Transition Timeline

### 2025-2027: Founder-Led + Council Formation
- **Founder:** Holds all admin roles + permanent council seat
- **Council:** Being formed, learning processes
- **DAO:** Not yet active (launching 2027)

### 2027: DAO Activation
- **Founder:** Admin → Multi-sig, retains council seat permanently
- **Council:** Fully operational, 6 elected members
- **DAO:** Token holders vote on proposals

### 2030+: Mature Governance
- **Founder:** Permanent Security Council member (1-of-7)
- **Council:** Handles emergencies, can veto malicious proposals
- **DAO:** Full control over protocol decisions

**Founder's Role Evolution:**
- **2025-2027:** Admin + Council Member
- **2027-2030:** Council Member (veto expires 2027)
- **2030+:** Council Member (permanent, 1 vote of 7)

---

## ✅ Summary

**What Was Implemented:**
✅ SecurityCouncil contract (463 lines)  
✅ Founder permanent membership (immutable)  
✅ 3-of-7 threshold for emergencies  
✅ 5-of-7 threshold for parameter changes  
✅ 6-month terms for elected members  
✅ Automatic term expiration  
✅ Performance tracking  
✅ Full transparency (all actions on-chain)  

**What This Achieves:**
✅ Founder maintains permanent influence via council  
✅ Cannot be removed or voted out  
✅ Always has 1 vote in security decisions  
✅ Balanced with community (6 other members)  
✅ Transparent and legitimate  
✅ Industry-standard governance model  

**Ready for:**
✅ Testing  
✅ Security audit  
✅ Testnet deployment  
✅ Community announcement  

---

**Implementation Complete** ✅  
**Founder Permanent Seat** ✅  
**Multi-Signature Security** ✅  
**Community Governance** ✅  
**Fully Transparent** ✅
