# OMK Hive Innovation Lab

The Innovation Lab is the home for all autonomous agent development using Fetch.ai's uAgents framework and other advanced AI technologies.

## 🚀 Overview

The Innovation Lab contains:

- **Bee Agents**: Specialized autonomous agents that perform various functions in the OMK Hive ecosystem
- **ASI Integration**: Connection to the Fetch.ai Autonomous Service Interface (ASI) network
- **Agent Orchestration**: Coordination between different agent types
- **Experimental Features**: Cutting-edge AI capabilities being tested for production

## 🐝 Bee Agents

All bee agents are now organized within the Innovation Lab:

1. **Maths Bee** - Financial calculations, mathematical modeling
2. **Logic Bee** - Decision validation, logic checking
3. **Liquidity Sentinel** - DEX/AMM monitoring and analysis
4. **Treasury Bee** - Fund management and allocation
5. **Pattern Recognition** - Market analysis and trend identification
6. **Purchase Bee** - Asset acquisition strategy
7. **Tokenization Bee** - Asset tokenization processing
8. **Fractional Assets** - Real-world asset management
9. **Stake Bot** - Staking optimization and management
10. **Visualization Bee** - Data visualization and reporting

## 🔌 ASI Integration

This lab connects to Fetch.ai's ASI network, enabling:

- Agent-to-agent communication across networks
- Participation in the wider Fetch.ai ecosystem
- Access to decentralized agent services
- Off-chain data exchange
- Cross-platform agent coordination

## 🛠️ Development

### Prerequisites

- Python 3.13+ 
- uAgents 0.22.10+
- cosmpy 0.9.2+

### Local Development

```bash
# Activate virtual environment
cd /Users/mac/CascadeProjects/omakh-Hive/backend/queen-ai
source venv/bin/activate

# Run a single bee agent
cd ../innovation-lab/bees/maths-bee
python agent.py

# Run the ASI connector
cd ../innovation-lab/asi
python connector.py
```

## 📊 Architecture

```
innovation-lab/
├── asi/                   # ASI integration and connector
│   ├── connector.py       # Main ASI network connector
│   ├── protocols/         # Protocol definitions
│   └── services/          # ASI service definitions
├── bees/                  # All bee agents
│   ├── maths-bee/         # Financial calculations
│   ├── logic-bee/         # Decision validation
│   ├── liquidity-sentinel/ # DEX monitoring
│   └── ...                # Other bees
├── shared/                # Shared code and utilities
│   ├── protocols/         # Communication protocols
│   ├── models/            # Data models
│   └── utils/             # Utilities
└── orchestration/         # Agent coordination
    ├── registry.py        # Agent registry
    └── scheduler.py       # Task scheduling
```

## 📈 Future Roadmap

- **Q4 2025**: Advanced multi-agent reasoning
- **Q1 2026**: Agent economic simulation
- **Q2 2026**: Inter-blockchain agent communication
- **Q3 2026**: Advanced LLM integration with agent coordination
