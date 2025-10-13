# OMK Token - Governance Structure

**Last Updated:** October 10, 2025  
**Current Phase:** Founder-Led Development (2025-2027)

---

## Current Phase: Founder-Led (2025-2027)

OMK is currently in solo-founder phase. All admin roles are held by the founder's address. As the project grows, we will transition to multi-sig then DAO. Timeline and process will be announced to community.

### Admin Powers (Held by Founder)

The founder currently maintains the following administrative capabilities:

- **Emergency pause/unpause** - Ability to halt all token operations in case of security threats
- **Vesting schedule creation** - Management of token vesting for team, investors, and community
- **Role management** - Granting and revoking operational roles for Queen AI and other system components
- **Treasury oversight** - Approval authority for treasury fund allocations
- **Proposal veto** - Ability to veto governance proposals until December 31, 2027

### Rationale

Solo founder building MVP. Admin powers ensure rapid response to bugs/attacks during growth phase. This concentrated control is temporary and necessary for:

1. **Security Response:** Quick action against exploits or attacks
2. **Development Velocity:** Rapid iteration without governance delays
3. **Infrastructure Stability:** Consistent decision-making during critical growth
4. **User Protection:** Founder accountability during early adoption

### Transition Plan

**2027: Multi-sig Implementation**
- Admin role transferred to Gnosis Safe 3-of-5 multi-sig
- Signers include founder + trusted community members + advisors
- All critical operations require majority approval

**2027: DAO Governance Launch**
- Token-weighted voting system activated
- Community can propose and vote on protocol changes
- Founder retains veto power through end of 2027 for security

**2030: Full Decentralization**
- Administrative roles transferred to DAO
- Pure DAO governance for protocol decisions
- Protocol upgrades via community consensus
- Founder remains as permanent Security Council member (elected council: 6 members + founder)

---

## Smart Contract Architecture

### Role-Based Access Control

All OMK smart contracts use OpenZeppelin's `AccessControl` for transparent role management:

**Core Roles:**
- `DEFAULT_ADMIN_ROLE` - Full administrative control (Founder)
- `VESTING_CREATOR_ROLE` - Create token vesting schedules
- `TREASURER_ROLE` - Treasury management (Queen AI advised)
- `QUEEN_ROLE` - Autonomous AI operations
- `GUARDIAN_ROLE` - Governance veto power (Founder, expires 2027)

### Current Role Assignments

```
Founder Address: [To be set at deployment]
├── DEFAULT_ADMIN_ROLE (all contracts)
├── FOUNDER_ROLE (SecurityCouncil - permanent)
├── GUARDIAN_ROLE (GovernanceManager - veto until 2027)
├── VESTING_CREATOR_ROLE (TokenVesting)
├── TREASURER_ROLE (TreasuryVault)
└── Can grant/revoke all other roles

Queen AI Backend:
├── QUEEN_ROLE (QueenController)
├── TREASURER_ROLE (TreasuryVault - advisory)
└── MONITOR_ROLE (LiquiditySentinel)

Security Council (7 members):
├── Founder (permanent member)
└── 6 elected community members (6-month terms)
```

---

## Security Council

### Structure

The Security Council is a 7-member elected body with emergency powers to protect the protocol. The council composition is:

- **1 Permanent Member:** Founder (cannot be removed, no term limit)
- **6 Elected Members:** Community-elected representatives (6-month terms)

### Powers & Responsibilities

**Emergency Actions** (requires 3-of-7 signatures):
- Emergency pause of contracts in case of exploits
- Quick response to security threats
- Temporary parameter adjustments during attacks

**Parameter Changes** (requires 5-of-7 signatures):
- Modify rate limits
- Adjust protocol fees
- Update oracle settings
- Change operational parameters

### Founder's Permanent Seat

**Rationale:**
- Protocol creator and primary maintainer
- Deep technical knowledge of system architecture
- Long-term alignment with project success
- Cannot be removed by vote (ensures stability)

**Founder's Responsibilities:**
- Participate in emergency security decisions
- Provide technical expertise to council
- Vote on parameter changes
- Cannot single-handedly make decisions (requires consensus)

### Election Process

**Elected Members:**
- Nominated by token holders (requires 500K OMK to nominate)
- Voted in by community (token-weighted voting)
- 6-month terms (renewable)
- Can be removed early by DAO vote (requires 15% quorum + 66% approval)

**Term Limits:**
- Elected members serve 6-month terms
- Can be re-elected unlimited times
- Founder has no term limit (permanent)

### Action Requirements

| Action Type | Signatures Required | Example |
|-------------|---------------------|---------|
| Emergency Pause | 3-of-7 | Stop trading during exploit |
| Emergency Unpause | 3-of-7 | Resume operations after fix |
| Parameter Change | 5-of-7 | Adjust rate limits |
| Remove Member | 5-of-7 + DAO vote | Remove inactive member |

**Note:** Founder participates in all votes but cannot be removed.

---

## Governance Roadmap

### Phase 1: Foundation (2025-2026)
**Status:** Current Phase

- **Focus:** Product development, initial user acquisition
- **Governance:** Founder-led with community input
- **Token Holders:** Can provide feedback via Discord/forums
- **Changes:** Announced 48 hours in advance via official channels

### Phase 2: Multi-sig Transition (2027)
**Target:** Q1 2027

- **Multi-sig Setup:** 3-of-5 Gnosis Safe
- **Signers:** Founder + 2 core contributors + 2 community representatives
- **Requirements:** 3 signatures for any admin action
- **Timelock:** 48-hour delay on all changes

### Phase 3: DAO Activation (2027)
**Target:** Q3 2027

- **Voting System:** 1 OMK = 1 vote (with delegation)
- **Proposal Types:** Parameter changes, treasury allocations, protocol upgrades
- **Quorum:** 10% of circulating supply
- **Founder Veto:** Available until December 31, 2027 (for security only)

### Phase 4: Full Decentralization (2030)
**Target:** January 1, 2030

- **Complete DAO Control:** All protocol decisions via community vote
- **No Special Privileges:** Founder has same rights as any token holder
- **Security Council:** 7-member elected council for emergency actions
- **Upgrade Authority:** Time-locked multisig controlled by DAO

---

## Transparency Commitments

### Public Monitoring

All admin actions are recorded on-chain and can be monitored at:
- Etherscan contract events
- OMK governance dashboard (coming Q1 2026)
- Weekly transparency reports

### What Admin CAN Do:
✅ Pause contracts in emergency  
✅ Create vesting schedules for disclosed allocations  
✅ Grant operational roles to verified addresses  
✅ Veto dangerous governance proposals (until 2027)  
✅ Approve treasury proposals within budget limits  

### What Admin CANNOT Do:
❌ Mint additional tokens (fixed supply: 1B OMK)  
❌ Seize user funds  
❌ Change token economics retroactively  
❌ Bypass multi-sig approval for treasury (after 2027)  
❌ Veto governance proposals (after December 31, 2027)  

---

## Security Measures

### Current Protections

1. **Immutable Token Supply:** 1 billion OMK, cannot be changed
2. **Rate Limiting:** Queen AI daily transfer limits
3. **Multi-sig Validation:** Bridge operations require 2-of-3 validators
4. **Timelock (Post-2027):** 48-hour delay on parameter changes
5. **Emergency Pause:** Can halt operations if exploit detected

### Audit Status

- **Internal Review:** Completed October 2025
- **Professional Audit:** Scheduled for Q4 2025 (Trail of Bits + OpenZeppelin)
- **Bug Bounty:** $50,000 program launching Q1 2026
- **Ongoing:** Continuous security monitoring via MonitoringBee

---

## Community Participation

### Current Phase (Pre-DAO)

**How to Participate:**
- Join Discord for project updates and feedback
- Submit improvement proposals via GitHub
- Report bugs through official channels
- Participate in community calls (monthly)

**Founder Commitment:**
- Weekly progress updates
- Monthly community AMA sessions
- Transparent treasury reporting
- 48-hour notice before major changes

### Future Phases (Post-DAO)

**Governance Rights:**
- Submit proposals (requires 1M OMK or delegation)
- Vote on all proposals
- Delegate voting power
- Participate in security council elections

---

## Legal Disclaimer

The governance structure described herein is subject to change based on regulatory requirements, technical constraints, or community consensus. The founder reserves the right to modify the transition timeline if necessary for security or legal compliance reasons. All changes will be communicated to the community with maximum possible advance notice.

Token holders should understand that:
- OMK is a utility token, not a security
- Holding OMK does not grant equity or profit-sharing rights
- Governance rights are granted voluntarily by the protocol
- The founder makes no guarantees about future governance structure
- Users should conduct their own research before participating

---

## Contact & Resources

**Official Channels:**
- Website: [omk.ai]
- Documentation: [docs.omk.ai]
- GitHub: [github.com/omk-hive]
- Discord: [discord.gg/omk]
- Twitter: [@omk_ai]

**Security:**
- Bug Reports: security@omk.ai
- Emergency Contact: [Founder contact]

**Governance:**
- Proposals (Future): [governance.omk.ai]
- Forum (Future): [forum.omk.ai]

---

**Document Version:** 1.0  
**Effective Date:** October 10, 2025  
**Next Review:** January 1, 2026
