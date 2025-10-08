# OMK Hive AI 🐝

> **AI-Governed Token Economy** - Autonomous blockchain ecosystem powered by Queen AI and specialized bee agents

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)](https://www.typescriptlang.org/)
[![Solidity](https://img.shields.io/badge/Solidity-0.8.20-orange)](https://soliditylang.org/)
[![Python](https://img.shields.io/badge/Python-3.11-green)](https://www.python.org/)

## 🌟 Overview

OMK Hive is a revolutionary blockchain ecosystem that combines artificial intelligence with decentralized finance. At its core, a Queen AI orchestrates specialized bee agents to autonomously manage tokenomics, liquidity, treasury operations, and ecosystem growth.

### Key Features

- **🤖 AI Orchestration**: Queen AI with 10+ specialized bee agents
- **💰 Autonomous Treasury**: AI-managed allocation and investments
- **🔄 Cross-Chain**: Ethereum + Solana with seamless bridge
- **📊 Dynamic Economics**: AI-adjusted APY, liquidity, and tokenomics
- **🏠 Asset Tokenization**: Fractional real estate and RWA support
- **🧠 Multi-LLM**: Gemini, GPT-4, Claude 3.5, X Grok with failover
- **📈 Learning Function**: Background data collection for future self-hosted models
- **🌐 ASI Integration**: Fetch.ai uAgents for decentralized agent network

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
      │  (10+ AI)  │     │  Function  │
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

## 📚 Documentation

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

**Current Phase**: Prime Task 1 - Foundation Setup  
**Status**: In Development  
**Target Launch**: Q2 2025

---

**⚠️ Disclaimer**: This is experimental software. Use at your own risk. Not financial advice.
