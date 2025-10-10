# 🐝 Hive Communication Architecture

## How Bees Work Together

The OMK Hive is a **multi-agent AI system** where specialized bees collaborate to serve users.

## Bee Roles & Responsibilities

### 1. **UserExperienceBee** (Frontend Interface) 👑
**Primary Contact** - Handles all user conversations

**Responsibilities:**
- Receive user messages
- Understand intent
- Route to appropriate bee
- Present responses conversationally
- Trigger frontend actions (cards, forms, dashboards)

**Actions it can trigger:**
```typescript
- connect_wallet → Shows WalletConnectCard
- show_properties → Shows PropertyCard
- show_dashboard → Shows DashboardCard
- show_swap → Shows SwapCard
- show_roi_calculator → Shows ROI Calculator
- ask_teacher_bee → Activates Teacher Bee mode
```

**Example Flow:**
```
User: "connect wallet"
↓
UserExperienceBee recognizes "wallet" keyword
↓
Returns: {action: "connect_wallet"}
↓
Frontend shows WalletConnectCard
```

---

### 2. **MathsBee** (Calculations) 🔢
**Financial Calculations**

**Specialties:**
- AMM (Automated Market Maker) math
- Slippage calculations
- APY/ROI computations
- Price impact analysis
- Token value calculations

**When to use:**
- "Calculate my returns"
- "What's the APY?"
- "How much will I earn?"

**Collaboration:**
```
UserExperienceBee receives ROI question
↓
Sends to MathsBee for calculation
↓
MathsBee returns: {roi: 12%, monthly: $150, annual: $1,800}
↓
UserExperienceBee formats response for user
```

---

### 3. **SecurityBee** (Safety & Validation) 🛡️
**Security & Risk Assessment**

**Specialties:**
- Address validation
- Transaction risk scoring
- Contract safety checks
- User authentication
- Fraud detection

**When to use:**
- Before any blockchain transaction
- Wallet connections
- Investment approvals
- "Is this safe?"

**Collaboration:**
```
User wants to invest $5,000
↓
UserExperienceBee → SecurityBee: validate_address(wallet)
↓
SecurityBee → "Address valid, risk score: LOW"
↓
UserExperienceBee → BlockchainBee: execute_transaction()
```

---

### 4. **DataBee** (Information Retrieval) 📊
**Data Access & Analytics**

**Specialties:**
- Blockchain queries (Elastic Search + BigQuery)
- Property data
- Market prices
- User portfolio data
- Historical analytics

**When to use:**
- "Show my portfolio"
- "What's the current price?"
- "Property availability?"

**Collaboration:**
```
User: "show my dashboard"
↓
UserExperienceBee → DataBee: get_user_portfolio(wallet)
↓
DataBee queries blockchain + database
↓
Returns: {eth: 0.5, omk: 10000, properties: [...]}
↓
UserExperienceBee formats as DashboardCard
```

---

### 5. **BlockchainBee** (Transaction Execution) ⛓️
**On-Chain Operations**

**Specialties:**
- Execute swaps
- Transfer tokens
- Interact with smart contracts
- Bridge operations
- Gas optimization

**When to use:**
- After security approval
- User confirmed transaction
- Automated rebalancing

**Safety:** Never executes without:
1. SecurityBee approval
2. User confirmation
3. Queen AI override (for automated actions)

---

### 6. **TreasuryBee** (Budget Management) 💰
**Financial Planning & Budgets**

**Specialties:**
- Track spending
- Budget allocations
- Treasury proposals
- Fund management

---

### 7. **LogicBee** (Decision Making) 🧠
**AI-Powered Decisions**

**Specialties:**
- Analyze multiple data points
- Make recommendations
- Consensus building
- Complex reasoning

**When to use:**
- Multi-factor decisions
- "Should I invest now?"
- Market condition analysis

---

### 8. **PatternBee** (Trend Detection) 📈
**Market Intelligence**

**Specialties:**
- Price trend analysis
- Anomaly detection
- Volatility prediction
- Pattern recognition

---

### 9. **Teacher Bee** (Education Mode) 📚
**Web3 Education**

**Specialties:**
- Explain crypto concepts
- Wallet setup guidance
- Security best practices
- Investment education

**Activation:**
```
User: "What's a wallet?"
↓
UserExperienceBee detects educational query
↓
Activates Teacher Bee mode
↓
Teacher Bee provides step-by-step education
```

---

## Communication Patterns

### Pattern 1: Simple Query (No Bee Needed)
```
User: "hello"
↓
UserExperienceBee responds directly
↓
Shows action buttons
```

### Pattern 2: Data Retrieval
```
User: "show my balance"
↓
UserExperienceBee → DataBee
↓
DataBee queries blockchain
↓
UserExperienceBee formats response
```

### Pattern 3: Complex Multi-Bee Flow
```
User: "I want to invest $1000"
↓
UserExperienceBee coordinates:
  1. SecurityBee: validate wallet
  2. DataBee: get available properties
  3. MathsBee: calculate blocks to buy
  4. LogicBee: recommend best property
↓
UserExperienceBee presents recommendation
↓
User confirms
↓
SecurityBee: final approval
↓
BlockchainBee: execute transaction
```

### Pattern 4: Educational Handover
```
User: "I don't understand blockchain"
↓
UserExperienceBee detects knowledge gap
↓
Activates Teacher Bee mode
↓
Teacher Bee takes over conversation
↓
Explains in simple terms
↓
Returns to UserExperienceBee when done
```

---

## Message Bus (Bee-to-Bee Communication)

Bees communicate via **Message Bus** without Queen intervention:

```python
# MathsBee needs market data
await message_bus.send(
    to="data_bee",
    from="maths_bee",
    priority="normal",
    data={"query": "get_omk_price"}
)

# DataBee responds
await message_bus.send(
    to="maths_bee",
    from="data_bee",
    priority="normal",
    data={"omk_price": 0.12}
)
```

---

## Hive Information Board

Shared knowledge system - all bees can post/query:

```python
# PatternBee detects price drop
await hive_board.post(
    category="market_alert",
    title="OMK price dropped 5%",
    content={"old_price": 0.12, "new_price": 0.114},
    priority="high",
    tags=["price", "alert", "omk"]
)

# LiquiditySentinelBee reads alert
alerts = await hive_board.query(
    category="market_alert",
    tags=["price"]
)
# Takes action: initiate buyback
```

---

## Queen AI Oversight

**Queen AI** coordinates but doesn't interfere in routine operations:

**Automated Operations** (No Queen needed):
- User queries → UserExperienceBee handles
- Data retrieval → DataBee handles
- Calculations → MathsBee handles

**Queen Approval Required:**
- Large transactions (>$10k)
- Treasury spending
- Protocol changes
- Emergency actions

**Queen Monitoring:**
- All bee activities logged
- Performance tracking
- Error handling
- System health

---

## Example: Complete User Journey

```
User: "I want to invest in real estate"
↓
┌─────────────────────────────────────┐
│ UserExperienceBee (Orchestrator)    │
└─────────────────────────────────────┘
         ↓
    "Show properties?"
         ↓
User: "yes"
         ↓
┌─────────────────────────────────────┐
│ DataBee: get_properties()           │ → Returns 15 properties
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│ UserExperienceBee                   │ → Shows PropertyCard
└─────────────────────────────────────┘
         ↓
User selects: "Dubai Marina, 10 blocks"
         ↓
┌─────────────────────────────────────┐
│ MathsBee: calculate_cost()          │ → $1,500
│ MathsBee: calculate_roi()           │ → 12% APY
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│ SecurityBee: validate_wallet()      │ → SAFE
│ SecurityBee: check_balance()        │ → Sufficient funds
└─────────────────────────────────────┘
         ↓
User: "confirm purchase"
         ↓
┌─────────────────────────────────────┐
│ BlockchainBee: execute_purchase()   │ → Transaction: 0x123...
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│ UserExperienceBee                   │ → "Success! 🎉"
└─────────────────────────────────────┘
         ↓
    Shows updated dashboard
```

---

## Frontend Action Mapping

UserExperienceBee returns actions that trigger frontend components:

| Action | Frontend Component | Purpose |
|--------|-------------------|---------|
| `connect_wallet` | WalletConnectCard | Connect MetaMask/Phantom |
| `show_properties` | PropertyCard | Browse real estate |
| `show_dashboard` | DashboardCard | Portfolio overview |
| `show_swap` | SwapCard | Token exchange |
| `show_roi_calculator` | ROI Calculator | Calculate returns |
| `ask_teacher_bee` | Teacher Bee Mode | Educational chat |
| `show_about` | InfoCard | Display information |

---

## Summary: How It All Works

1. **User sends message** → Frontend → Backend
2. **UserExperienceBee receives** → Understands intent
3. **Coordinates with bees** → Gets needed data/calculations
4. **Returns structured response** → With actions
5. **Frontend renders** → Shows cards, buttons, etc.
6. **User interacts** → Cycle continues

**Key Principle:** UserExperienceBee is the **face** of the hive. All other bees are **specialists** working behind the scenes.

**Result:** Seamless, intelligent, context-aware conversation that feels like talking to a human financial advisor! 🎯
