# OMK Hive AI 🐝

> **AI-Governed Token Economy** - Autonomous blockchain ecosystem powered by Queen AI and specialized bee agents

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)](https://www.typescriptlang.org/)
[![Solidity](https://img.shields.io/badge/Solidity-0.8.20-orange)](https://soliditylang.org/)
[![Python](https://img.shields.io/badge/Python-3.13-green)](https://www.python.org/)

## 🌟 Overview

OMK Hive is a revolutionary blockchain ecosystem that combines artificial intelligence with decentralized finance. At its core, a Queen AI orchestrates specialized bee agents to autonomously manage tokenomics, liquidity, treasury operations, and ecosystem growth.

### Key Features

- **👑 Queen Autonomy**: 24/7 autonomous operations with multi-layer safeguards
- **🤖 AI Orchestration**: Queen AI with 19 specialized bee agents
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
- **Python**: 3.13+
- **npm**: Latest
- **Google Cloud SDK**: For deployment
- **Hardhat**: For smart contracts (optional)
- **Rust**: For Solana programs (optional)

### Installation

```bash
# Clone repository
git clone https://github.com/mromk94/omakh-Hive.git
cd omakh-Hive
```

### Start (recommended)

```bash
# From repo root
chmod +x start-omakh.sh stop-omakh.sh reboot-omakh.sh
./reboot-omakh.sh   # or: ./start-omakh.sh
```

Behavior:
- Backend: http://localhost:8001
- New Frontend (site): http://localhost:3000  (Admin via /kingdom)
- Admin (legacy): http://localhost:3001/kingdom
- Logs: logs/queen-backend.log, logs/new-frontend.log, logs/frontend.log

### Manual (alternative)

```bash
# Backend (terminal A)
cd backend/queen-ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# New Frontend (terminal B)
cd new-frontend
npm install
npm run dev

# Admin (terminal C)
cd omk-frontend
npm install
npm run dev -- -p 3001
```

Visit:
- **Site**: http://localhost:3000 (Admin via /kingdom)
- **Admin (direct)**: http://localhost:3001/kingdom
- **Queen AI API**: http://localhost:8001/health
- **Production API**: https://omk-queen-ai-475745165557.us-central1.run.app

## 📦 Project Structure

```
omakh-Hive/
├── backend/
│   └── queen-ai/          # FastAPI Backend + Queen AI
│       ├── app/
│       │   ├── api/v1/    # REST API endpoints
│       │   ├── bees/      # 19 specialized bee agents
│       │   ├── core/      # Orchestrator, message bus, hive board
│       │   ├── llm/       # Multi-LLM abstraction (Gemini, GPT-4, Claude, Grok)
│       │   └── blockchain/# Ethereum + Solana integration
│       ├── data/          # File-based storage (JSON)
│       ├── main.py        # FastAPI application
│       └── requirements.txt
├── omk-frontend/          # Next.js Frontend
│   ├── app/               # App router pages
│   ├── components/        # React components
│   └── hooks/             # WebSocket + custom hooks
├── contracts/
│   ├── ethereum/          # Solidity contracts
│   ├── solana/            # Rust programs (planned)
│   └── bridge/            # Cross-chain bridge (planned)
└── infrastructure/        # Deployment configs
    ├── k8s/               # Kubernetes manifests
    └── terraform/         # GCP infrastructure (planned)
```

## 🛠️ Technology Stack

### Blockchain
- **Ethereum**: Solidity 0.8.20, Hardhat, OpenZeppelin
- **Solana**: Rust, Anchor Framework
- **Fetch.ai**: CosmWasm, uAgents

### Backend
- **Queen AI**: Python 3.13, FastAPI, structlog
- **Multi-LLM**: Google Gemini (primary), OpenAI GPT-4, Anthropic Claude 3.5, X Grok
- **Storage**: File-based JSON (MySQL/PostgreSQL planned)
- **Message Bus**: In-memory (Redis planned)
- **WebSockets**: Real-time Hive Intelligence updates

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
- **Compute**: Cloud Run (currently deployed)
- **CI/CD**: Cloud Build, Artifact Registry, GitHub
- **Monitoring**: Cloud Logging
- **Future**: GKE, Cloud SQL, Memorystore, Secret Manager

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
# Backend tests
cd backend/queen-ai
pytest tests/ -v

# Frontend tests  
cd omk-frontend
npm test

# Contract tests
cd contracts/ethereum
npx hardhat test
```

## 🚢 Deployment

### Google Cloud Run (Production)
```bash
cd backend/queen-ai

# Build and deploy
gcloud builds submit --tag=gcr.io/omk-hive/omk-queen-ai
gcloud run deploy omk-queen-ai \
  --image gcr.io/omk-hive/omk-queen-ai \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated
```

**Live Backend**: https://omk-queen-ai-475745165557.us-central1.run.app

### Frontend (Netlify)
```bash
cd omk-frontend
npm run build
# Deploy via Netlify CLI or GitHub integration
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Development Guidelines:**
- Follow existing code style
- Add tests for new features
- Update documentation
- Test locally before pushing

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

**Current Phase**: Active Development - Core Features  
**Progress**:
- ✅ Queen AI Orchestrator with 19 specialized bee agents
- ✅ Multi-LLM integration (Gemini, GPT-4, Claude, Grok)
- ✅ FastAPI backend deployed to Google Cloud Run
- ✅ Next.js frontend with Kingdom admin dashboard
- ✅ Hive Intelligence real-time WebSocket
- ✅ Ethereum smart contracts (OMKToken, QueenController, PrivateSale)
- ✅ Background initialization for instant startup
- 🚧 Database migration (file → MySQL/PostgreSQL)
- 🚧 Solana programs
- 🚧 Cross-chain bridge

**Status**: Active Development  
**Deployed**: Backend live on Google Cloud Run  
**Target Launch**: Q1 2026

---

**⚠️ Disclaimer**: This is experimental software. Use at your own risk. Not financial advice.
