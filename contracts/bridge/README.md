# OMK Token Cross-Chain Bridge

**Status**: ✅ Implemented  
**Chains**: Ethereum ↔ Solana  
**Type**: Lock & Mint Bridge

---

## 🌉 OVERVIEW

The OMK Bridge enables seamless token transfers between Ethereum and Solana, allowing users to:
- Lock OMK on Ethereum → Mint wrapped OMK on Solana
- Burn wrapped OMK on Solana → Unlock OMK on Ethereum

### Architecture

```
Ethereum                    Relayer Service                 Solana
─────────────────────────────────────────────────────────────────────

OMKBridge.sol  ←────────→  Bridge Relayer  ←────────→  omk-bridge (Anchor)
   │                             │                              │
   │ 1. Lock OMK                 │                              │
   │─────────────────────────────→ Monitor Lock Event          │
   │                             │─────────────────────────────→│
   │                             │         2. Mint Wrapped      │
   │                             │                              │
   │                             │        3. Monitor Burn       │
   │                             │←─────────────────────────────│
   │ 4. Release OMK              │                              │
   │←─────────────────────────────                              │
```

---

## 📦 COMPONENTS

### 1. Ethereum Bridge Contract (`OMKBridge.sol`)

**Location**: `contracts/ethereum/src/bridge/OMKBridge.sol`

**Features**:
- ✅ Lock OMK tokens for bridging
- ✅ Release OMK after Solana burn (with proof)
- ✅ Multi-signature validation (2+ validators)
- ✅ Rate limiting (10M OMK/day - adjustable)
- ✅ **Queen AI control with admin approval** ⭐
- ✅ Emergency pause
- ✅ Proof verification

**Key Functions**:
```solidity
// Lock tokens to bridge to Solana
function lockTokens(uint256 amount, bytes32 solanaAddress) external returns (uint256)

// Validators approve release
function validateRelease(address to, uint256 amount, bytes32 solanaProof) external

// Release tokens after Solana burn
function releaseTokens(address to, uint256 amount, bytes32 solanaProof) external returns (uint256)
```

### 2. Solana Bridge Program (`omk-bridge`)

**Location**: `contracts/solana/omk-bridge/`

**Features**:
- ✅ Mint wrapped OMK on Solana
- ✅ Burn wrapped OMK to bridge back
- ✅ Validator signature verification
- ✅ Transaction deduplication
- ✅ Emergency pause

**Key Instructions**:
```rust
// Initialize bridge
pub fn initialize(ctx: Context<Initialize>, ethereum_bridge: [u8; 20]) -> Result<()>

// Mint wrapped tokens (after ETH lock)
pub fn mint_wrapped(ctx: Context<MintWrapped>, amount: u64, ethereum_tx_hash: [u8; 32]) -> Result<()>

// Burn wrapped tokens (to bridge back)
pub fn burn_wrapped(ctx: Context<BurnWrapped>, amount: u64, ethereum_recipient: [u8; 20]) -> Result<()>
```

### 3. Relayer Service

**Location**: `contracts/bridge/relayer/`

**Purpose**: Off-chain service monitoring both chains and facilitating cross-chain transfers.

**Responsibilities**:
- Monitor Ethereum for lock events
- Call Solana program to mint wrapped tokens
- Monitor Solana for burn events
- Coordinate with validators
- Call Ethereum bridge to release tokens

---

## 🚀 DEPLOYMENT

### Prerequisites

```bash
# Ethereum
- Node.js 18+
- Hardhat
- Infura/Alchemy API key

# Solana
- Rust 1.70+
- Solana CLI 1.16+
- Anchor 0.29+

# Relayer
- Node.js 18+
- PM2 (production)
```

### 1. Deploy Ethereum Bridge

```bash
cd contracts/ethereum

# Compile
npx hardhat compile

# Deploy
npx hardhat run scripts/deploy-bridge.ts --network sepolia

# Verify
npx hardhat verify --network sepolia BRIDGE_ADDRESS
```

### 2. Deploy Solana Program

```bash
cd contracts/solana/omk-bridge

# Build
anchor build

# Get program ID
solana address -k target/deploy/omk_bridge-keypair.json

# Update lib.rs with program ID
# declare_id!("YOUR_PROGRAM_ID");

# Deploy to devnet
anchor deploy --provider.cluster devnet

# Initialize
anchor run initialize --provider.cluster devnet
```

### 3. Run Relayer Service

```bash
cd contracts/bridge/relayer

# Install dependencies
npm install

# Configure
cp .env.example .env
# Edit .env with your keys

# Development
npm run dev

# Production (with PM2)
pm2 start npm --name "omk-relayer" -- start
pm2 save
pm2 startup
```

---

## 👑 QUEEN AI & ADMIN CONTROL

### Proposal System

The bridge implements a **proposal-approval system** where Queen AI can propose changes and Admin approves them:

#### Queen AI Powers (Propose Only)
```solidity
// Queen proposes changes
function proposeChange(
    ProposalType proposalType,
    address targetAddress,
    uint256 newValue,
    string description
) external onlyRole(QUEEN_ROLE) returns (uint256 proposalId)
```

**What Queen Can Propose**:
- ✅ Update rate limit (adjust daily bridge capacity)
- ✅ Add/remove relayers
- ✅ Add/remove validators
- ✅ Update required validator count
- ✅ Pause/unpause bridge

**Flow**:
1. Queen detects need for change (e.g., high demand → increase rate limit)
2. Queen calls `proposeChange()` with details
3. Proposal logged on-chain with ID
4. Admin reviews proposal
5. Admin approves or rejects
6. If approved, Queen or Admin executes

#### Admin Powers (Full Control)

**Approve/Reject**:
```solidity
function approveProposal(uint256 proposalId) external onlyRole(DEFAULT_ADMIN_ROLE)
function rejectProposal(uint256 proposalId) external onlyRole(DEFAULT_ADMIN_ROLE)
```

**Direct Emergency Actions** (no proposal needed):
```solidity
function addRelayer(address relayer) external onlyRole(DEFAULT_ADMIN_ROLE)
function removeRelayer(address relayer) external onlyRole(DEFAULT_ADMIN_ROLE)
function pause() external onlyRole(DEFAULT_ADMIN_ROLE)
function unpause() external onlyRole(DEFAULT_ADMIN_ROLE)
function emergencyWithdraw(address to, uint256 amount) external onlyRole(DEFAULT_ADMIN_ROLE)
```

### Example: Queen Proposes Rate Limit Increase

```javascript
// 1. Queen detects high bridge demand
const currentLimit = await bridge.maxDailyBridge();
const newLimit = ethers.utils.parseEther("20000000"); // 20M OMK

// 2. Queen proposes increase
const tx = await bridge.connect(queen).proposeChange(
    0, // ProposalType.UPDATE_RATE_LIMIT
    ethers.constants.AddressZero,
    newLimit,
    "Increase daily limit to 20M due to high demand"
);
const receipt = await tx.wait();
const proposalId = receipt.events[0].args.proposalId;

// 3. Admin reviews and approves
await bridge.connect(admin).approveProposal(proposalId);

// 4. Queen or Admin executes
await bridge.connect(queen).executeProposal(proposalId);

// 5. Rate limit now 20M ✅
```

### View Pending Proposals

```javascript
// Get pending proposals count
const pendingCount = await bridge.getPendingProposalsCount();

// Get proposal details
const proposal = await bridge.getProposal(proposalId);
console.log("Proposer:", proposal.proposer);
console.log("Type:", proposal.proposalType);
console.log("Approved:", proposal.approved);
console.log("Executed:", proposal.executed);
```

---

## 🔐 SECURITY

### Multi-Signature Validation

All release transactions require approval from multiple validators:
- **Minimum Validators**: 2 (configurable)
- **Validator Rotation**: Supported
- **Independent Validation**: Each validator independently verifies Solana proofs

### Rate Limiting

To prevent abuse:
- **Max Daily Bridge**: 10M OMK
- **Auto Reset**: Every 24 hours
- **Admin Override**: Available in emergencies

### Emergency Controls

- **Pause Bridge**: Stops all bridge operations
- **Emergency Withdraw**: Admin can recover stuck tokens
- **Validator Update**: Add/remove validators on the fly

### Proof Verification

- **Ethereum → Solana**: Ethereum tx hash verified by multiple validators
- **Solana → Ethereum**: Solana signature hash used as proof, verified on-chain
- **Deduplication**: Each proof can only be used once

---

## 📊 MONITORING

### Health Checks

```bash
# Check Ethereum bridge status
cast call $ETH_BRIDGE_ADDRESS "getBridgeStats()" --rpc-url $ETH_RPC_URL

# Check Solana program state
solana program show $SOL_PROGRAM_ID --url devnet

# Check relayer status
curl http://localhost:3000/health
```

### Metrics

The bridge tracks:
- Total locked on Ethereum
- Total minted on Solana
- Total burned on Solana
- Total released on Ethereum
- Daily bridge volume
- Failed transactions
- Relayer uptime

---

## 🧪 TESTING

### Ethereum Bridge Tests

```bash
cd contracts/ethereum
npx hardhat test test/OMKBridge.test.ts
```

### Solana Program Tests

```bash
cd contracts/solana/omk-bridge
anchor test
```

### Integration Test (E2E)

```bash
cd contracts/bridge
npm run test:e2e
```

---

## 💸 FEES

### Ethereum → Solana
- **Ethereum Gas**: ~150k gas (lock transaction)
- **Solana Fee**: ~0.000005 SOL (mint transaction)
- **Bridge Fee**: None (covered by relayer)

### Solana → Ethereum
- **Solana Fee**: ~0.000005 SOL (burn transaction)
- **Ethereum Gas**: ~200k gas (release transaction)
- **Bridge Fee**: None (covered by relayer)

---

## 🔄 USER FLOW

### Bridging ETH → SOL

1. User approves OMK Bridge contract
2. User calls `lockTokens(amount, solanaAddress)`
3. OMK tokens locked in bridge contract
4. Relayer detects lock event
5. Relayer calls Solana program to mint wrapped OMK
6. User receives wrapped OMK on Solana

### Bridging SOL → ETH

1. User calls Solana program `burn_wrapped(amount, ethAddress)`
2. Wrapped OMK burned on Solana
3. Relayer detects burn event
4. Relayer + validators verify burn
5. Relayer calls Ethereum bridge to release OMK
6. User receives OMK on Ethereum

---

## 🛠️ MAINTENANCE

### Add Validator

```solidity
// Ethereum
bridge.addValidator(newValidatorAddress);

// Solana
// Update program config
```

### Update Rate Limit

```solidity
// Ethereum only (Solana has no rate limit)
bridge.setMaxDailyBridge(newLimit);
```

### Pause/Unpause

```solidity
// Ethereum
bridge.pause();
bridge.unpause();

// Solana
// Call pause_bridge / unpause_bridge
```

---

## 📝 TODO

- [ ] Implement validator signature collection
- [ ] Add monitoring dashboard
- [ ] Implement automatic alerting
- [ ] Add Prometheus metrics
- [ ] Create admin panel
- [ ] Implement fee collection
- [ ] Add automatic validator rotation
- [ ] Implement zkProof verification (future)

---

## 🔗 RESOURCES

- **Ethereum Bridge Contract**: [OMKBridge.sol](./ethereum/OMKBridge.sol)
- **Solana Program**: [lib.rs](./solana/omk-bridge/src/lib.rs)
- **Relayer Service**: [relayer/](./relayer/)
- **Anchor Documentation**: https://www.anchor-lang.com/
- **Wormhole (Reference)**: https://docs.wormhole.com/

---

## 📞 SUPPORT

For bridge-related issues:
1. Check relayer logs
2. Verify both chains are synced
3. Check validator signatures
4. Contact OMK Hive team on Discord

**Status Page**: https://status.omkhive.com  
**Discord**: https://discord.gg/omkhive
