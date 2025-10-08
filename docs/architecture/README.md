# OMK Hive Architecture

## System Overview

OMK Hive is a decentralized AI-governed token economy built on multiple blockchain networks with a sophisticated AI orchestration layer.

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend Layer                         │
│         (Next.js + TailwindCSS + Web3 Wallets)             │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    API Gateway (NestJS)                     │
│         REST + GraphQL + WebSocket + Authentication         │
└─────────────┬──────────────────────────────┬────────────────┘
              │                              │
    ┌─────────▼──────────┐       ┌──────────▼─────────┐
    │   Queen AI Core    │       │  Blockchain Layer  │
    │  (FastAPI/Python)  │       │  (Ethereum/Solana) │
    └─────────┬──────────┘       └──────────┬─────────┘
              │                              │
    ┌─────────▼──────────┐                  │
    │   Bee Agents (10+) │                  │
    │  Specialized AI    │                  │
    └────────────────────┘                  │
              │                              │
    ┌─────────▼──────────────────────────────▼─────────┐
    │           Data Layer (PostgreSQL/Redis)          │
    └──────────────────────────────────────────────────┘
```

## Core Components

### 1. Frontend Layer
**Technology**: Next.js 14, TailwindCSS, shadcn/ui

**Responsibilities**:
- User interface for token interactions
- Wallet connection (Ethereum, Solana)
- Real-time data visualization
- Admin dashboard

**Key Features**:
- Server-side rendering for SEO
- Real-time updates via WebSocket
- Multi-chain wallet support
- Responsive design

### 2. API Gateway
**Technology**: NestJS, TypeORM, GraphQL, Apollo

**Responsibilities**:
- Request routing and authentication
- Rate limiting and security
- API versioning
- GraphQL endpoint
- WebSocket server

**Key Features**:
- JWT-based authentication
- Role-based access control
- Request validation
- API documentation (Swagger)
- Metrics and logging

### 3. Queen AI Orchestrator
**Technology**: FastAPI, Python 3.11, uAgents

**Responsibilities**:
- AI decision making
- Bee coordination
- LLM integration (multi-provider)
- Learning function management
- ASI network integration

**Key Features**:
- Multi-LLM support (Gemini, GPT-4, Claude, Grok)
- Autonomous decision engine
- State management
- Proposal generation
- Memory persistence

### 4. Bee Agents
**Technology**: Python, Specialized AI models

**Types**:
1. **Maths Bee** - Financial calculations
2. **Logic Bee** - Decision validation
3. **Liquidity Sentinel** - DEX monitoring
4. **Treasury Bee** - Fund management
5. **Pattern Recognition** - Market analysis
6. **Purchase Bee** - Asset acquisition
7. **Tokenization Bee** - Asset tokenization
8. **Fractional Assets** - RWA management
9. **Stake Bot** - Staking optimization
10. **Visualization Bee** - Data presentation

### 5. Blockchain Layer

#### Ethereum Contracts
**Technology**: Solidity 0.8.20, Hardhat, OpenZeppelin

**Core Contracts**:
- `OMKToken.sol` - ERC-20 token with extensions
- `QueenController.sol` - AI governance interface
- `BeeSpawner.sol` - Bee agent registry
- `LiquiditySentinel.sol` - AMM monitoring
- `TreasuryVault.sol` - Multisig treasury
- `StakingManager.sol` - Staking rewards
- `Fractionalizer.sol` - Asset tokenization
- `GovernanceDAO.sol` - Community governance

#### Solana Programs
**Technology**: Rust, Anchor Framework

**Programs**:
- Token program (SPL integration)
- Staking program
- Bridge program

#### Cross-Chain Bridge
**Technology**: Chainlink CCIP, Custom relayers

**Features**:
- Ethereum ↔ Solana token transfers
- State synchronization
- Secure message passing

### 6. Data Infrastructure

#### PostgreSQL
**Purpose**: Primary data store

**Schema**:
- Users and authentication
- Transactions history
- AI decisions log
- Bee performance metrics
- Configuration data

#### Redis
**Purpose**: Caching and real-time data

**Usage**:
- Session storage
- API rate limiting
- WebSocket state
- Real-time price feeds
- Job queues

#### BigQuery
**Purpose**: Learning function data

**Usage**:
- Transaction analysis
- User behavior patterns
- Model training data
- Analytics

### 7. Message Bus
**Technology**: Kafka or Redis Streams

**Responsibilities**:
- Event-driven communication
- Service decoupling
- Async job processing
- Real-time data streaming

## Data Flow

### 1. User Transaction Flow
```
User → Frontend → API Gateway → Blockchain
                      ↓
                  Queen AI (for approval)
                      ↓
                  Bee Agents (validation)
                      ↓
                  Learning Function (log)
```

### 2. AI Decision Flow
```
Trigger → Queen AI → Decision Engine
              ↓
         Consult Bees
              ↓
         Generate Proposal
              ↓
         Execute on Blockchain
              ↓
         Log to Learning DB
```

### 3. Cross-Chain Bridge Flow
```
Source Chain → Lock Tokens → Relayer
                   ↓
              Verify & Sign
                   ↓
            Mint on Target Chain
```

## Security Architecture

### Authentication & Authorization
- JWT tokens with refresh mechanism
- Role-based access control (RBAC)
- API key authentication for services
- Multisig for critical operations

### Smart Contract Security
- OpenZeppelin audited contracts
- Reentrancy guards
- Access control modifiers
- Pausable functionality
- Rate limiting

### Infrastructure Security
- Secrets in GCP Secret Manager
- Network policies in Kubernetes
- TLS/SSL everywhere
- Regular security scans

## Scalability

### Horizontal Scaling
- API Gateway: Multiple replicas
- Queen AI: Stateless, scales horizontally
- Bees: Independent, can scale per type

### Database Scaling
- PostgreSQL: Read replicas
- Redis: Cluster mode
- BigQuery: Auto-scaling

### Performance Optimization
- CDN for static assets
- Database query optimization
- Caching strategies
- Connection pooling

## Monitoring & Observability

### Metrics
- Prometheus for metrics collection
- Grafana for visualization
- Custom business metrics

### Logging
- Structured logging (JSON)
- Centralized in GCP Cloud Logging
- Log levels per environment

### Tracing
- OpenTelemetry integration
- Distributed tracing
- Performance profiling

### Alerting
- PagerDuty for critical alerts
- Slack for warnings
- Email for info

## Deployment Architecture

### Development
- Local Docker Compose
- Mock external services
- Local blockchain (Hardhat)

### Staging
- GKE cluster
- Cloud SQL (PostgreSQL)
- Memorystore (Redis)
- Sepolia testnet

### Production
- Multi-region GKE
- High-availability databases
- Auto-scaling enabled
- Ethereum/Solana mainnet

## Future Architecture Considerations

### Planned Enhancements
1. Service mesh (Istio) for advanced traffic management
2. Self-hosted LLM models
3. Advanced monitoring with AI anomaly detection
4. Multi-region active-active setup
5. Layer 2 scaling solutions

### Research Areas
1. ZK-rollups for privacy
2. Decentralized storage (IPFS/Filecoin)
3. Advanced AI models (custom training)
4. Cross-chain interoperability protocols

---

**See Also**:
- [Smart Contracts](contracts.md)
- [Queen AI System](queen-ai.md)
- [Bee Agents](bees.md)
