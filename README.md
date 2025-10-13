# OMK Hive AI 🐝

> **AI-Governed Token Economy** - Autonomous blockchain ecosystem powered by Queen AI and specialized bee agents

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)](https://www.typescriptlang.org/)
[![Solidity](https://img.shields.io/badge/Solidity-0.8.20-orange)](https://soliditylang.org/)
[![Python](https://img.shields.io/badge/Python-3.11-green)](https://www.python.org/)

## 🌟 Overview

OMK Hive is a revolutionary blockchain ecosystem that combines artificial intelligence with decentralized finance. At its core, a Queen AI orchestrates specialized bee agents to autonomously manage tokenomics, liquidity, treasury operations, and ecosystem growth.

### Key Features

- **👑 Queen Autonomy**: 24/7 autonomous operations with multi-layer safeguards
- **🤖 AI Orchestration**: Queen AI with 16+ specialized bee agents
- **💰 Autonomous Treasury**: AI-managed allocation and investments (400M OMK)
- **🔄 Cross-Chain**: Ethereum + Solana with seamless bridge
- **📊 Dynamic Economics**: AI-adjusted APY, liquidity, and tokenomics
- **🏠 Asset Tokenization**: Fractional real estate and RWA support
- **🧠 Multi-LLM**: Gemini, GPT-4, Claude 3.5, X Grok with failover
- **🔍 Data Intelligence**: Enterprise DataBee with Elastic Search + BigQuery integration
- **💬 Conversational AI**: RAG-powered queries on all platform data
- **📈 Learning Function**: Background data collection for future self-hosted models
- **🌐 ASI Integration**: Fetch.ai uAgents for decentralized agent network
- **🛡️ Safety First**: Rate limiting (50M/day), emergency controls, full transparency

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Frontend Layer                     │
│         (Next.js + TailwindCSS + shadcn/ui)        │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│                API Gateway (NestJS)                 │
│          REST + GraphQL + WebSocket                 │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│            Queen AI Orchestrator                    │
│         (FastAPI + uAgents + Multi-LLM)            │
└────────────┬──────────────────┬─────────────────────┘
             │                  │
      ┌──────▼─────┐     ┌─────▼──────┐
      │ Bee Agents │     │  Learning  │
      │  (16 AI)   │     │  Function  │
      │ +DataBee   │     │ +Analytics │
      └──────┬─────┘     └────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐     ┌──────────┐
│ Ethereum│     │  Solana  │
│Contracts│     │ Programs │
└─────────┘     └──────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Node.js**: v20+
- **Python**: 3.11+
- **Docker**: Latest
- **pnpm**: Latest (or npm/yarn)
- **Hardhat**: For smart contracts
- **Rust**: For Solana programs

### Installation

```bash
# Clone repository
git clone https://github.com/mromk94/omakh-Hive.git
cd omakh-Hive

# Run setup script
make setup

# Start development environment
make dev
```

Visit:
- Frontend: http://localhost:3001
- API Gateway: http://localhost:3000
- Queen AI: http://localhost:8000

## 📦 Monorepo Structure

```
omakh-Hive/
├── contracts/              # Smart contracts
│   ├── ethereum/          # Solidity contracts
│   ├── solana/            # Rust programs
│   └── bridge/            # Cross-chain bridge
├── backend/               # Backend services
│   ├── api-gateway/       # NestJS API
│   ├── queen-ai/          # Python FastAPI Queen
│   ├── bees/              # Bee agents
│   └── shared/            # Shared utilities
├── frontend/              # Frontend applications
│   └── web/               # Next.js web app
├── infrastructure/        # IaC and deployments
│   ├── terraform/         # GCP infrastructure
│   ├── k8s/               # Kubernetes manifests
│   └── helm/              # Helm charts
├── docs/                  # Documentation
└── scripts/               # Utility scripts
```

## 🛠️ Technology Stack

### Blockchain
- **Ethereum**: Solidity 0.8.20, Hardhat, OpenZeppelin
- **Solana**: Rust, Anchor Framework
- **Fetch.ai**: CosmWasm, uAgents

### Backend
- **API Gateway**: NestJS, TypeScript, TypeORM, GraphQL
- **Queen AI**: Python, FastAPI, uAgents, structlog
- **Databases**: PostgreSQL, Redis
- **Message Bus**: Kafka / Redis Streams

### AI/ML
- **Primary LLM**: Google Gemini 1.5 (Vertex AI)
- **Alternatives**: OpenAI GPT-4, Anthropic Claude 3.5, X Grok
- **Learning**: BigQuery, Cloud Storage, Vertex AI Model Registry

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Styling**: TailwindCSS
- **Components**: shadcn/ui
- **State**: Zustand
- **Web3**: Wagmi, Viem, @solana/web3.js

### Infrastructure (GCP)
- **Compute**: Google Kubernetes Engine (GKE)
- **Database**: Cloud SQL (PostgreSQL)
- **Cache**: Memorystore (Redis)
- **Storage**: Cloud Storage
- **CI/CD**: Cloud Build, Artifact Registry
- **Monitoring**: Cloud Monitoring, Cloud Logging
- **Secrets**: Secret Manager

## 👑 Queen Autonomy Architecture

**OMK Hive's Queen AI operates autonomously 24/7** with full control over 400M OMK tokens for market operations.

### **Why Autonomous?**
- ⚡ **Real-time response** to market conditions (no human delay)
- 🤖 **True AI governance** (not admin-approved actions)
- 🌍 **24/7 availability** (Queen never sleeps)

### **Safeguards**
- 🛡️ **50M OMK daily limit** (5% of supply maximum per day)
- 🔔 **Large transfer alerts** (>100M OMK triggers monitoring)
- 🚨 **Emergency pause** (Admin can halt all operations)
- 📊 **Full transparency** (All operations logged on-chain)

### **Queen's Responsibilities**
1. **DEX Liquidity Management** - Add/remove liquidity in real-time
2. **Market Making** - CEX operations and order book management
3. **Staking Rewards** - Calculate and distribute rewards daily
4. **Airdrops & Incentives** - Community growth campaigns
5. **Cross-chain Operations** - Bridge management and multi-chain liquidity

**Learn more**: [Queen Autonomy Architecture](docs/QUEEN_AUTONOMY_ARCHITECTURE.md)

## 💰 Tokenomics

**Total Supply**: 1,000,000,000 OMK

| Allocation | Amount | % | Control |
|------------|--------|---|---------|
| Public Acquisition | 400M | 40% | Queen AI (immediate) |
| Founders | 250M | 25% | Vested (12m cliff + 36m) |
| Treasury | 120M | 12% | TreasuryVault |
| Ecosystem | 100M | 10% | Queen AI (36m vesting) |
| Private Investors | 100M | 10% | Private Sale (30m vesting) |
| Advisors | 20M | 2% | Vested (18m linear) |
| Breakswitch | 10M | 1% | Admin (emergency) |

### **Private Sale**
- **Structure**: 10 tiers × 10M tokens
- **Price Range**: $0.100 - $0.145 per token
- **Total Raise**: $12.25M USD
- **Whale Limit**: 20M OMK per investor
- **Vesting**: 12-month cliff + 18-month linear

**Learn more**: [Tokenomics](docs/TOKENOMICS_UPDATED.md) | [Private Sale](docs/PRIVATE_SALE_STRUCTURE.md)

## 📚 Documentation

- [Queen Autonomy Architecture](docs/QUEEN_AUTONOMY_ARCHITECTURE.md) ⭐ **NEW**
- [Private Sale Structure](docs/PRIVATE_SALE_STRUCTURE.md) ⭐ **NEW**
- [Tokenomics](docs/TOKENOMICS_UPDATED.md) ⭐ **UPDATED**
- [Architecture Overview](docs/architecture/README.md)
- [Smart Contracts](docs/architecture/contracts.md)
- [Queen AI System](docs/architecture/queen-ai.md)
- [Bee Agents](docs/architecture/bees.md)
- [API Documentation](docs/api/README.md)
- [Deployment Guide](docs/deployment/README.md)
- [Contributing](docs/CONTRIBUTING.md)

## 🔐 Security

- All smart contracts audited
- Multisig for treasury operations
- Rate limiting on all APIs
- Secrets managed via GCP Secret Manager
- Regular security scans (Slither, Mythril)

## 🧪 Testing

```bash
# Run all tests
make test

# Test specific component
make test-contracts      # Smart contracts
make test-backend        # Backend services
make test-queen          # Queen AI
make test-frontend       # Frontend
```

## 🚢 Deployment

### Development
```bash
make deploy-dev
```

### Staging
```bash
make deploy-staging
```

### Production
```bash
make deploy-production
```

See [Deployment Guide](docs/deployment/README.md) for details.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Website**: [Coming Soon]
- **Documentation**: [Coming Soon]
- **Twitter**: [Coming Soon]
- **Discord**: [Coming Soon]

## 👥 Team

Built by the OMK Hive team with ❤️

## 📊 Project Status

**Current Phase**: Prime Task 2 - Smart Contract Development  
**Progress**:
- ✅ PRIME TASK 1: Foundation & Setup (74% complete)
- 🚧 PRIME TASK 2: Smart Contracts (30% complete)
  - ✅ OMKToken.sol with Queen autonomy safeguards
  - ✅ QueenController.sol with operation tracking
  - ✅ PrivateSale.sol with tiered pricing
  - ✅ TokenVesting.sol utility
  - ⏳ TreasuryVault.sol (pending)
  - ⏳ LiquiditySentinel.sol (pending)
- ⏳ PRIME TASK 3: AI Core (not started)

**Status**: Active Development  
**Target Launch**: December 2025

---

**⚠️ Disclaimer**: This is experimental software. Use at your own risk. Not financial advice.
