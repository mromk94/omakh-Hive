# PRIME TASK 1: PROJECT FOUNDATION & REPOSITORY SETUP
**Repository**: https://github.com/mromk94/omakh-Hive.git  
**Status**: READY TO IMPLEMENT  
 

---

## PART 1: REPOSITORY STRUCTURE

### Complete Directory Tree

```
omakh-Hive/
├── README.md
├── .gitignore
├── .gitattributes
├── LICENSE
├── .editorconfig
├── .prettierrc
├── .eslintrc.json
├── docker-compose.yml
├── docker-compose.dev.yml
├── Makefile
│
├── .github/
│   ├── workflows/
│   │   ├── ci-contracts.yml
│   │   ├── ci-backend.yml
│   │   ├── ci-frontend.yml
│   │   ├── ci-queen-ai.yml
│   │   ├── deploy-staging.yml
│   │   └── deploy-production.yml
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   └── enhancement.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── CODEOWNERS
│
├── contracts/
│   ├── ethereum/
│   │   ├── src/
│   │   │   ├── core/
│   │   │   ├── liquidity/
│   │   │   ├── treasury/
│   │   │   ├── staking/
│   │   │   ├── assets/
│   │   │   ├── governance/
│   │   │   └── interfaces/
│   │   ├── test/
│   │   ├── scripts/
│   │   ├── hardhat.config.ts
│   │   ├── package.json
│   │   └── .env.example
│   ├── solana/
│   │   ├── programs/
│   │   ├── tests/
│   │   ├── Anchor.toml
│   │   └── package.json
│   └── bridge/
│
├── backend/
│   ├── api-gateway/
│   ├── queen-ai/
│   ├── bees/
│   ├── blockchain-service/
│   └── shared/
│
├── frontend/
│   ├── web/
│   ├── admin/
│   └── mobile/ (future)
│
├── infrastructure/
│   ├── terraform/
│   ├── k8s/
│   ├── helm/
│   └── scripts/
│
├── docs/
│   ├── architecture/
│   ├── api/
│   ├── deployment/
│   ├── security/
│   └── user-guides/
│
└── scripts/
    ├── setup/
    ├── deploy/
    ├── database/
    └── utils/
```

---

## PART 2: FILE-BY-FILE CREATION CHECKLIST

### ROOT LEVEL FILES

#### 1. README.md
```markdown
# OMK Hive AI - Autonomous Token Ecosystem

**Multi-chain AI-governed token with decentralized agent network**

## Overview
OMK Hive is an autonomous token ecosystem powered by a Queen AI and specialized bee agents, operating across Ethereum and Solana with real-world asset tokenization.

## Features
- 🤖 Queen AI orchestration with 10+ specialized bees
- 🔗 Multi-chain support (Ethereum + Solana)
- 🧠 Multi-LLM architecture (Gemini, GPT-4, Claude, Grok)
- 📊 Learning function for future self-hosted AI
- 🌐 ASI/Fetch.ai decentralized agent network
- 🏠 Fractionalized real-world asset tokenization
- 💎 Dynamic staking with AI-adjusted APY

## Tech Stack
- **Blockchain**: Solidity, Rust (Anchor), Hardhat
- **Backend**: Node.js, NestJS, Python, FastAPI
- **Frontend**: Next.js 14, React, TypeScript, Tailwind
- **AI/ML**: Gemini, Vertex AI, Fetch.ai uAgents
- **Infrastructure**: Google Cloud Platform (GKE, Cloud SQL)
- **Database**: PostgreSQL, Redis, BigQuery

## Repository Structure
- `/contracts` - Smart contracts (Ethereum, Solana, Bridge)
- `/backend` - Backend services (API, Queen AI, Bees)
- `/frontend` - Web and admin interfaces
- `/infrastructure` - IaC, K8s, deployment configs
- `/docs` - Documentation
- `/scripts` - Utility scripts

## Getting Started

### Prerequisites
- Node.js 20+
- Python 3.11+
- Docker & Docker Compose
- Google Cloud SDK
- Hardhat
- Anchor CLI

### Quick Start
```bash
# Clone repository
git clone https://github.com/mromk94/omakh-Hive.git
cd omakh-Hive

# Run setup script
make setup

# Start development environment
make dev
```

## Documentation
- [Architecture](./docs/architecture/)
- [API Documentation](./docs/api/)
- [Deployment Guide](./docs/deployment/)
- [Security](./docs/security/)

## License
Proprietary - All Rights Reserved

## Contact
- Website: (TBD)
- Twitter: (TBD)
- Discord: (TBD)
```

**TODO**:
- [ ] Create README.md with above content
- [ ] Update contact links when available
- [ ] Add badges (build status, coverage, etc.)

---

#### 2. .gitignore
```gitignore
# Dependencies
node_modules/
.pnp
.pnp.js

# Environment variables
.env
.env.local
.env.*.local
.env.production
.env.development
*.env

# Build outputs
dist/
build/
.next/
out/
target/
*.egg-info/

# Python
__pycache__/
*.py[cod]
*$py.class
.Python
venv/
.venv/
env/
ENV/
.pytest_cache/
.coverage
htmlcov/
*.cover

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Logs
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*

# Testing
coverage/
.nyc_output/
test-results/

# Hardhat
cache/
artifacts/
typechain-types/

# Solana/Anchor
.anchor/
test-ledger/

# Terraform
*.tfstate
*.tfstate.*
.terraform/
.terragrm-cache/

# Google Cloud
gcp-key.json
*-key.json
service-account*.json

# Secrets
secrets/
*.pem
*.key

# Temporary
tmp/
temp/
*.tmp
```

**TODO**:
- [ ] Create .gitignore file
- [ ] Verify all sensitive patterns are included

---

#### 3. .editorconfig
```ini
root = true

[*]
charset = utf-8
end_of_line = lf
indent_style = space
indent_size = 2
insert_final_newline = true
trim_trailing_whitespace = true
max_line_length = 100

[*.{js,jsx,ts,tsx}]
indent_size = 2

[*.{py}]
indent_size = 4

[*.{md,mdx}]
trim_trailing_whitespace = false

[*.{sol}]
indent_size = 4

[Makefile]
indent_style = tab
```

**TODO**:
- [ ] Create .editorconfig file

---

#### 4. .prettierrc
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "arrowParens": "always",
  "endOfLine": "lf",
  "overrides": [
    {
      "files": "*.sol",
      "options": {
        "printWidth": 120,
        "tabWidth": 4,
        "useTabs": false,
        "singleQuote": false,
        "bracketSpacing": false
      }
    }
  ]
}
```

**TODO**:
- [ ] Create .prettierrc file
- [ ] Install prettier in root package.json

---

#### 5. .eslintrc.json
```json
{
  "root": true,
  "env": {
    "browser": true,
    "es2021": true,
    "node": true
  },
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "prettier"
  ],
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "ecmaVersion": "latest",
    "sourceType": "module"
  },
  "plugins": ["@typescript-eslint"],
  "rules": {
    "no-console": "warn",
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "warn"
  }
}
```

**TODO**:
- [ ] Create .eslintrc.json file
- [ ] Install eslint dependencies in root

---

#### 6. LICENSE
```
Copyright (c) 2025 OMK Hive AI

All rights reserved.

This software and associated documentation files (the "Software") are proprietary
and confidential. Unauthorized copying, distribution, modification, or use of this
Software, via any medium, is strictly prohibited.
```

**TODO**:
- [ ] Create LICENSE file
- [ ] Confirm license type with team
- [ ] Update year and copyright holder

---

#### 7. Makefile
```makefile
.PHONY: help setup dev build test clean deploy

help:
	@echo "OMK Hive AI - Development Commands"
	@echo ""
	@echo "setup          - Initial project setup"
	@echo "dev            - Start development environment"
	@echo "build          - Build all services"
	@echo "test           - Run all tests"
	@echo "lint           - Lint all code"
	@echo "format         - Format all code"
	@echo "clean          - Clean build artifacts"
	@echo "deploy-staging - Deploy to staging"
	@echo "deploy-prod    - Deploy to production"

setup:
	@echo "Setting up OMK Hive development environment..."
	./scripts/setup/init.sh

dev:
	docker-compose -f docker-compose.dev.yml up

build:
	@echo "Building all services..."
	cd contracts/ethereum && npm run build
	cd backend/api-gateway && npm run build
	cd backend/queen-ai && pip install -r requirements.txt
	cd frontend/web && npm run build

test:
	@echo "Running tests..."
	cd contracts/ethereum && npm test
	cd backend/api-gateway && npm test
	cd backend/queen-ai && pytest
	cd frontend/web && npm test

lint:
	@echo "Linting code..."
	npm run lint --workspaces
	cd backend/queen-ai && pylint src/

format:
	@echo "Formatting code..."
	npm run format --workspaces
	cd backend/queen-ai && black src/

clean:
	@echo "Cleaning build artifacts..."
	find . -name "node_modules" -type d -prune -exec rm -rf '{}' +
	find . -name "dist" -type d -prune -exec rm -rf '{}' +
	find . -name "__pycache__" -type d -prune -exec rm -rf '{}' +
	find . -name ".next" -type d -prune -exec rm -rf '{}' +

deploy-staging:
	./scripts/deploy/staging.sh

deploy-prod:
	./scripts/deploy/production.sh
```

**TODO**:
- [ ] Create Makefile
- [ ] Create referenced scripts in /scripts

---

#### 8. docker-compose.yml (Production-like local)
```yaml
version: '3.9'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: omk_hive
      POSTGRES_USER: omk
      POSTGRES_PASSWORD: changeme
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U omk"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  api-gateway:
    build:
      context: ./backend/api-gateway
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://omk:changeme@postgres:5432/omk_hive
      - REDIS_URL=redis://redis:6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend/api-gateway/src:/app/src

  queen-ai:
    build:
      context: ./backend/queen-ai
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://omk:changeme@postgres:5432/omk_hive
      - REDIS_URL=redis://redis:6379
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend/queen-ai/src:/app/src

  frontend:
    build:
      context: ./frontend/web
      dockerfile: Dockerfile.dev
    ports:
      - "3001:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:3000
    volumes:
      - ./frontend/web/src:/app/src

volumes:
  postgres_data:
  redis_data:
```

**TODO**:
- [ ] Create docker-compose.yml
- [ ] Create .env.example for required variables
- [ ] Test local Docker setup

---

### GITHUB WORKFLOWS

#### .github/workflows/ci-contracts.yml
```yaml
name: CI - Smart Contracts

on:
  push:
    branches: [main, develop, staging]
    paths:
      - 'contracts/**'
  pull_request:
    branches: [main, develop, staging]
    paths:
      - 'contracts/**'

jobs:
  test-ethereum:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: contracts/ethereum/package-lock.json
      
      - name: Install dependencies
        working-directory: contracts/ethereum
        run: npm ci
      
      - name: Compile contracts
        working-directory: contracts/ethereum
        run: npm run compile
      
      - name: Run tests
        working-directory: contracts/ethereum
        run: npm test
      
      - name: Run coverage
        working-directory: contracts/ethereum
        run: npm run coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./contracts/ethereum/coverage/lcov.info
          flags: contracts-ethereum

  lint-ethereum:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install dependencies
        working-directory: contracts/ethereum
        run: npm ci
      
      - name: Run Solhint
        working-directory: contracts/ethereum
        run: npm run lint
```

**TODO**:
- [ ] Create .github/workflows/ci-contracts.yml
- [ ] Add similar workflows for backend, frontend, queen-ai
- [ ] Configure repository secrets
- [ ] Test workflow triggers

---

## PART 3: PACKAGE.JSON FILES

### Root package.json
```json
{
  "name": "omk-hive",
  "version": "1.0.0",
  "private": true,
  "description": "OMK Hive AI - Autonomous Token Ecosystem",
  "repository": "https://github.com/mromk94/omakh-Hive.git",
  "author": "OMK Hive Team",
  "license": "PROPRIETARY",
  "workspaces": [
    "contracts/ethereum",
    "backend/api-gateway",
    "backend/blockchain-service",
    "frontend/web",
    "frontend/admin"
  ],
  "scripts": {
    "dev": "docker-compose -f docker-compose.dev.yml up",
    "build": "npm run build --workspaces",
    "test": "npm run test --workspaces",
    "lint": "npm run lint --workspaces",
    "format": "prettier --write \"**/*.{js,jsx,ts,tsx,json,md}\"",
    "prepare": "husky install",
    "clean": "npm run clean --workspaces && rm -rf node_modules"
  },
  "devDependencies": {
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "eslint": "^8.50.0",
    "eslint-config-prettier": "^9.0.0",
    "husky": "^8.0.3",
    "lint-staged": "^15.0.0",
    "prettier": "^3.0.0",
    "typescript": "^5.2.0"
  },
  "engines": {
    "node": ">=20.0.0",
    "npm": ">=10.0.0"
  }
}
```

**TODO**:
- [ ] Create root package.json
- [ ] Run `npm install` to initialize workspaces
- [ ] Configure husky for git hooks

---

### contracts/ethereum/package.json
```json
{
  "name": "@omk-hive/contracts-ethereum",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "compile": "hardhat compile",
    "test": "hardhat test",
    "coverage": "hardhat coverage",
    "deploy:testnet": "hardhat run scripts/deploy.ts --network sepolia",
    "deploy:mainnet": "hardhat run scripts/deploy.ts --network mainnet",
    "lint": "solhint 'src/**/*.sol'",
    "typechain": "hardhat typechain",
    "clean": "hardhat clean"
  },
  "dependencies": {
    "@openzeppelin/contracts": "^5.0.0",
    "@openzeppelin/contracts-upgradeable": "^5.0.0",
    "@chainlink/contracts": "^0.8.0"
  },
  "devDependencies": {
    "@nomicfoundation/hardhat-toolbox": "^4.0.0",
    "@nomicfoundation/hardhat-verify": "^2.0.0",
    "@typechain/ethers-v6": "^0.5.0",
    "@typechain/hardhat": "^9.0.0",
    "@types/chai": "^4.3.0",
    "@types/mocha": "^10.0.0",
    "@types/node": "^20.0.0",
    "chai": "^4.3.0",
    "dotenv": "^16.3.0",
    "ethers": "^6.9.0",
    "hardhat": "^2.19.0",
    "hardhat-gas-reporter": "^1.0.0",
    "solhint": "^4.0.0",
    "solidity-coverage": "^0.8.5",
    "ts-node": "^10.9.0",
    "typechain": "^8.3.0",
    "typescript": "^5.2.0"
  }
}
```

**TODO**:
- [ ] Create contracts/ethereum/package.json
- [ ] Install dependencies: `cd contracts/ethereum && npm install`

---

### contracts/ethereum/hardhat.config.ts
```typescript
import { HardhatUserConfig } from 'hardhat/config';
import '@nomicfoundation/hardhat-toolbox';
import '@nomicfoundation/hardhat-verify';
import 'hardhat-gas-reporter';
import 'solidity-coverage';
import * as dotenv from 'dotenv';

dotenv.config();

const config: HardhatUserConfig = {
  solidity: {
    version: '0.8.20',
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
      viaIR: true,
    },
  },
  networks: {
    hardhat: {
      chainId: 31337,
    },
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL || '',
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
      chainId: 11155111,
    },
    mainnet: {
      url: process.env.MAINNET_RPC_URL || '',
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
      chainId: 1,
    },
  },
  etherscan: {
    apiKey: {
      sepolia: process.env.ETHERSCAN_API_KEY || '',
      mainnet: process.env.ETHERSCAN_API_KEY || '',
    },
  },
  gasReporter: {
    enabled: process.env.REPORT_GAS === 'true',
    currency: 'USD',
    coinmarketcap: process.env.COINMARKETCAP_API_KEY,
  },
  paths: {
    sources: './src',
    tests: './test',
    cache: './cache',
    artifacts: './artifacts',
  },
  typechain: {
    outDir: 'typechain-types',
    target: 'ethers-v6',
  },
};

export default config;
```

**TODO**:
- [ ] Create contracts/ethereum/hardhat.config.ts
- [ ] Create contracts/ethereum/.env.example

---

### contracts/ethereum/.env.example
```bash
# Network RPCs
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_KEY
MAINNET_RPC_URL=https://mainnet.infura.io/v3/YOUR_INFURA_KEY

# Private Keys (NEVER commit actual keys)
PRIVATE_KEY=your_private_key_here

# Etherscan
ETHERSCAN_API_KEY=your_etherscan_api_key

# Gas Reporter
REPORT_GAS=true
COINMARKETCAP_API_KEY=your_coinmarketcap_key

# Contract Addresses (will be populated after deployment)
OMK_TOKEN_ADDRESS=
QUEEN_CONTROLLER_ADDRESS=
TREASURY_VAULT_ADDRESS=
```

**TODO**:
- [ ] Create contracts/ethereum/.env.example
- [ ] Add to .gitignore verification

---

### backend/api-gateway/package.json
```json
{
  "name": "@omk-hive/api-gateway",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "build": "nest build",
    "start": "nest start",
    "start:dev": "nest start --watch",
    "start:debug": "nest start --debug --watch",
    "start:prod": "node dist/main",
    "lint": "eslint \"{src,test}/**/*.ts\"",
    "lint:fix": "eslint \"{src,test}/**/*.ts\" --fix",
    "format": "prettier --write \"src/**/*.ts\" \"test/**/*.ts\"",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:cov": "jest --coverage",
    "test:e2e": "jest --config ./test/jest-e2e.json"
  },
  "dependencies": {
    "@nestjs/common": "^10.0.0",
    "@nestjs/core": "^10.0.0",
    "@nestjs/platform-express": "^10.0.0",
    "@nestjs/config": "^3.1.0",
    "@nestjs/jwt": "^10.2.0",
    "@nestjs/passport": "^10.0.2",
    "@nestjs/swagger": "^7.1.0",
    "@nestjs/typeorm": "^10.0.0",
    "@nestjs/graphql": "^12.0.0",
    "@nestjs/apollo": "^12.0.0",
    "@apollo/server": "^4.9.0",
    "typeorm": "^0.3.17",
    "pg": "^8.11.0",
    "redis": "^4.6.0",
    "bcrypt": "^5.1.1",
    "passport": "^0.7.0",
    "passport-jwt": "^4.0.1",
    "passport-local": "^1.0.0",
    "class-validator": "^0.14.0",
    "class-transformer": "^0.5.1",
    "ethers": "^6.9.0",
    "rxjs": "^7.8.0",
    "reflect-metadata": "^0.1.13"
  },
  "devDependencies": {
    "@nestjs/cli": "^10.0.0",
    "@nestjs/schematics": "^10.0.0",
    "@nestjs/testing": "^10.0.0",
    "@types/express": "^4.17.17",
    "@types/jest": "^29.5.2",
    "@types/node": "^20.3.1",
    "@types/passport-jwt": "^3.0.9",
    "@types/passport-local": "^1.0.35",
    "@types/bcrypt": "^5.0.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "eslint": "^8.42.0",
    "jest": "^29.5.0",
    "prettier": "^3.0.0",
    "source-map-support": "^0.5.21",
    "ts-jest": "^29.1.0",
    "ts-loader": "^9.4.3",
    "ts-node": "^10.9.1",
    "tsconfig-paths": "^4.2.0",
    "typescript": "^5.1.3"
  }
}
```

**TODO**:
- [ ] Create backend/api-gateway/package.json
- [ ] Install dependencies

---

### backend/queen-ai/requirements.txt
```txt
# FastAPI Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# AI/ML
google-cloud-aiplatform==1.38.1
google-generativeai==0.3.1
openai==1.3.7
anthropic==0.7.7

# Fetch.ai uAgents
uagents==0.7.0
cosmpy==0.9.0

# Database
sqlalchemy==2.0.23
asyncpg==0.29.0
redis==5.0.1
psycopg2-binary==2.9.9

# Utils
python-dotenv==1.0.0
httpx==0.25.2
aiohttp==3.9.1
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Logging & Monitoring
structlog==23.2.0
sentry-sdk==1.38.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0
httpx-mock==0.13.0

# Development
black==23.12.1
pylint==3.0.3
mypy==1.7.1
isort==5.13.2
```

**TODO**:
- [ ] Create backend/queen-ai/requirements.txt
- [ ] Create backend/queen-ai/pyproject.toml for project metadata

---

### backend/queen-ai/pyproject.toml
```toml
[tool.poetry]
name = "queen-ai"
version = "1.0.0"
description = "OMK Hive Queen AI Orchestrator"
authors = ["OMK Hive Team"]
license = "Proprietary"

[tool.poetry.dependencies]
python = "^3.11"

[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 100

[tool.pylint]
max-line-length = 100
disable = ["C0111", "C0103"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "-v --cov=src --cov-report=html --cov-report=term"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

**TODO**:
- [ ] Create backend/queen-ai/pyproject.toml

---

### frontend/web/package.json
```json
{
  "name": "@omk-hive/web",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "format": "prettier --write \"src/**/*.{js,jsx,ts,tsx,json,css,md}\"",
    "test": "jest",
    "test:watch": "jest --watch",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "next": "14.0.4",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@tanstack/react-query": "^5.14.2",
    "zustand": "^4.4.7",
    "wagmi": "^2.2.0",
    "viem": "^2.0.0",
    "@rainbow-me/rainbowkit": "^2.0.0",
    "@solana/wallet-adapter-react": "^0.15.35",
    "@solana/web3.js": "^1.87.6",
    "axios": "^1.6.2",
    "lucide-react": "^0.294.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.1.0",
    "class-variance-authority": "^0.7.0",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-select": "^2.0.0",
    "recharts": "^2.10.3",
    "date-fns": "^3.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.10.4",
    "@types/react": "^18.2.45",
    "@types/react-dom": "^18.2.17",
    "typescript": "^5.3.3",
    "eslint": "^8.55.0",
    "eslint-config-next": "14.0.4",
    "tailwindcss": "^3.3.6",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "@testing-library/react": "^14.1.2",
    "@testing-library/jest-dom": "^6.1.5",
    "jest": "^29.7.0",
    "jest-environment-jsdom": "^29.7.0"
  }
}
```

**TODO**:
- [ ] Create frontend/web/package.json
- [ ] Create frontend/web/next.config.js
- [ ] Create frontend/web/tailwind.config.ts

---

## PART 4: INFRASTRUCTURE FILES

### infrastructure/terraform/main.tf
```hcl
terraform {
  required_version = ">= 1.6"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  
  backend "gcs" {
    bucket = "omk-hive-terraform-state"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# VPC Network
resource "google_compute_network" "vpc" {
  name                    = "omk-hive-vpc"
  auto_create_subnetworks = false
}

# Subnet
resource "google_compute_subnetwork" "subnet" {
  name          = "omk-hive-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc.id
  
  secondary_ip_range {
    range_name    = "gke-pods"
    ip_cidr_range = "10.1.0.0/16"
  }
  
  secondary_ip_range {
    range_name    = "gke-services"
    ip_cidr_range = "10.2.0.0/20"
  }
}

# GKE Autopilot Cluster
resource "google_container_cluster" "primary" {
  name     = "omk-hive-gke"
  location = var.region
  
  enable_autopilot = true
  
  network    = google_compute_network.vpc.id
  subnetwork = google_compute_subnetwork.subnet.id
  
  ip_allocation_policy {
    cluster_secondary_range_name  = "gke-pods"
    services_secondary_range_name = "gke-services"
  }
  
  release_channel {
    channel = "REGULAR"
  }
  
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }
}

# Cloud SQL PostgreSQL
resource "google_sql_database_instance" "main" {
  name             = "omk-hive-db"
  database_version = "POSTGRES_16"
  region           = var.region
  
  settings {
    tier = "db-f1-micro"  # Start small, upgrade later
    
    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc.id
    }
    
    backup_configuration {
      enabled            = true
      start_time         = "02:00"
      point_in_time_recovery_enabled = true
    }
  }
  
  deletion_protection = true
}

# Memorystore Redis
resource "google_redis_instance" "cache" {
  name           = "omk-hive-redis"
  tier           = "BASIC"
  memory_size_gb = 1
  region         = var.region
  
  authorized_network = google_compute_network.vpc.id
  redis_version      = "REDIS_7_0"
}

# Cloud Storage Bucket for Learning Function Data
resource "google_storage_bucket" "learning_data" {
  name          = "${var.project_id}-learning-data"
  location      = var.region
  storage_class = "STANDARD"
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }
}

# Secret Manager
resource "google_secret_manager_secret" "gemini_api_key" {
  secret_id = "gemini-api-key"
  
  replication {
    automatic = true
  }
}
```

**TODO**:
- [ ] Create infrastructure/terraform/main.tf
- [ ] Create infrastructure/terraform/variables.tf
- [ ] Create infrastructure/terraform/outputs.tf

---

### infrastructure/k8s/api-gateway-deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: omk-hive
  labels:
    app: api-gateway
    tier: backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      serviceAccountName: api-gateway-sa
      containers:
      - name: api-gateway
        image: gcr.io/PROJECT_ID/api-gateway:latest
        ports:
        - containerPort: 3000
          name: http
        env:
        - name: NODE_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-credentials
              key: url
        resources:
          requests:
            cpu: "250m"
            memory: "512Mi"
          limits:
            cpu: "500m"
            memory: "1Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: api-gateway
  namespace: omk-hive
spec:
  selector:
    app: api-gateway
  ports:
  - port: 80
    targetPort: 3000
    name: http
  type: ClusterIP
```

**TODO**:
- [ ] Create infrastructure/k8s/ directory with all deployment YAMLs
- [ ] Create namespace.yaml, ingress.yaml, etc.

---

## PART 5: SCRIPTS & AUTOMATION

### scripts/setup/init.sh
```bash
#!/bin/bash
set -e

echo "🚀 Initializing OMK Hive Development Environment"
echo "================================================"

# Check prerequisites
echo "📋 Checking prerequisites..."

command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed."; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed."; exit 1; }
command -v gcloud >/dev/null 2>&1 || { echo "❌ Google Cloud SDK is required but not installed."; exit 1; }

echo "✅ All prerequisites met"

# Install root dependencies
echo ""
echo "📦 Installing root dependencies..."
npm install

# Setup contracts/ethereum
echo ""
echo "📜 Setting up Ethereum contracts..."
cd contracts/ethereum
cp .env.example .env
npm install
cd ../..

# Setup backend/api-gateway
echo ""
echo "🔧 Setting up API Gateway..."
cd backend/api-gateway
cp .env.example .env
npm install
cd ../..

# Setup backend/queen-ai
echo ""
echo "👑 Setting up Queen AI..."
cd backend/queen-ai
cp .env.example .env
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ../..

# Setup frontend/web
echo ""
echo "🎨 Setting up Frontend..."
cd frontend/web
cp .env.local.example .env.local
npm install
cd ../..

# Setup Git hooks
echo ""
echo "🪝 Setting up Git hooks..."
npx husky install
npx husky add .husky/pre-commit "npx lint-staged"
npx husky add .husky/commit-msg 'npx --no -- commitlint --edit ${1}'

# Initialize GCP (if needed)
echo ""
echo "☁️  Initializing Google Cloud..."
read -p "Do you want to initialize GCP project? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    read -p "Enter your GCP Project ID: " PROJECT_ID
    gcloud config set project $PROJECT_ID
    gcloud auth application-default login
    echo "✅ GCP configured"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env files with your credentials"
echo "2. Run 'make dev' to start development environment"
echo "3. Visit http://localhost:3001 for frontend"
echo "4. Visit http://localhost:3000/api for backend API"
```

**TODO**:
- [ ] Create scripts/setup/init.sh
- [ ] Make executable: `chmod +x scripts/setup/init.sh`
- [ ] Test setup script

---

## PART 6: DOCUMENTATION STRUCTURE

### docs/architecture/README.md
```markdown
# OMK Hive Architecture Documentation

## System Overview

OMK Hive is a multi-layered autonomous token ecosystem powered by AI agents.

### High-Level Architecture

```
┌─────────────────────────────────────────────┐
│          User Interface Layer               │
│  (Next.js Web App, Admin Dashboard)         │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│          API Gateway Layer                  │
│  (NestJS REST + GraphQL APIs)              │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         Queen AI Orchestration              │
│  (Python FastAPI + uAgents)                │
└──────────────────┬──────────────────────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
         ▼                   ▼
┌─────────────────┐  ┌──────────────────┐
│  Specialized    │  │  Smart Contracts │
│  Bees (10+)     │  │  (ETH + SOL)     │
└─────────────────┘  └──────────────────┘
```

## Component Details

- [Queen AI Architecture](./queen-ai.md)
- [Bee System](./bees.md)
- [Smart Contracts](./contracts.md)
- [Frontend Architecture](./frontend.md)
- [Database Schema](./database.md)
- [Infrastructure](./infrastructure.md)

## Technology Stack

See [../TECH_STACK.md](../TECH_STACK.md)
```

**TODO**:
- [ ] Create docs/architecture/README.md
- [ ] Create detailed architecture docs for each component

---

### docs/CONTRIBUTING.md
```markdown
# Contributing to OMK Hive

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/omakh-Hive.git`
3. Create a feature branch: `git checkout -b feature/amazing-feature`
4. Make your changes
5. Run tests: `make test`
6. Commit: `git commit -m 'Add amazing feature'`
7. Push: `git push origin feature/amazing-feature`
8. Open a Pull Request

## Development Workflow

### Branch Naming
- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Urgent production fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring

### Commit Messages
Follow conventional commits:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test additions/changes
- `chore:` - Build/config changes

Example: `feat: add Gemini provider to LLM abstraction layer`

### Code Style

**TypeScript/JavaScript**:
- Use Prettier for formatting
- Follow ESLint rules
- Use 2-space indentation
- Use single quotes

**Python**:
- Use Black for formatting
- Follow PEP 8
- Use 4-space indentation
- Type hints required

**Solidity**:
- Follow Solidity style guide
- Use 4-space indentation
- Document all functions with NatSpec

### Testing Requirements

- **Unit Tests**: Required for all new features
- **Integration Tests**: Required for API endpoints
- **E2E Tests**: Required for critical user flows
- **Coverage**: Maintain >80% coverage

### Pull Request Process

1. Update documentation
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review from 2+ team members
6. Address review comments
7. Squash commits before merge

## Code Review Checklist

- [ ] Code follows project style guidelines
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] No sensitive data exposed
- [ ] Performance impact considered
- [ ] Security implications reviewed

## Questions?

Open an issue or contact the team.
```

**TODO**:
- [ ] Create docs/CONTRIBUTING.md
- [ ] Customize for team workflow

---

## PART 7: COMPREHENSIVE TODO CHECKLIST

### Phase 1: Repository Setup (Week 1)

#### Day 1: Initialize Repository
- [ ] Clone repository from https://github.com/mromk94/omakh-Hive.git
- [ ] Create branch structure (main, develop, staging)
- [ ] Set up branch protection rules on GitHub
- [ ] Add team members with appropriate permissions
- [ ] Enable Dependabot and code scanning

#### Day 2: Root Configuration
- [ ] Create README.md
- [ ] Create .gitignore
- [ ] Create .gitattributes
- [ ] Create .editorconfig
- [ ] Create .prettierrc
- [ ] Create .eslintrc.json
- [ ] Create LICENSE
- [ ] Create root package.json
- [ ] Create Makefile
- [ ] Create docker-compose.yml
- [ ] Create docker-compose.dev.yml

#### Day 3: Directory Structure
- [ ] Create /contracts/ethereum directory structure
- [ ] Create /contracts/solana directory structure
- [ ] Create /backend/api-gateway directory structure
- [ ] Create /backend/queen-ai directory structure
- [ ] Create /backend/bees directory structure
- [ ] Create /frontend/web directory structure
- [ ] Create /infrastructure directory structure
- [ ] Create /docs directory structure
- [ ] Create /scripts directory structure

#### Day 4: Package Configuration
- [ ] Create contracts/ethereum/package.json
- [ ] Create contracts/ethereum/hardhat.config.ts
- [ ] Create contracts/ethereum/.env.example
- [ ] Create backend/api-gateway/package.json
- [ ] Create backend/api-gateway/nest-cli.json
- [ ] Create backend/api-gateway/.env.example
- [ ] Create backend/queen-ai/requirements.txt
- [ ] Create backend/queen-ai/pyproject.toml
- [ ] Create backend/queen-ai/.env.example
- [ ] Create frontend/web/package.json
- [ ] Create frontend/web/next.config.js
- [ ] Create frontend/web/tailwind.config.ts
- [ ] Create frontend/web/.env.local.example

#### Day 5: GitHub Workflows
- [ ] Create .github/workflows/ci-contracts.yml
- [ ] Create .github/workflows/ci-backend.yml
- [ ] Create .github/workflows/ci-frontend.yml
- [ ] Create .github/workflows/ci-queen-ai.yml
- [ ] Create .github/workflows/deploy-staging.yml
- [ ] Create .github/workflows/deploy-production.yml
- [ ] Create .github/ISSUE_TEMPLATE/bug_report.md
- [ ] Create .github/ISSUE_TEMPLATE/feature_request.md
- [ ] Create .github/PULL_REQUEST_TEMPLATE.md
- [ ] Create .github/CODEOWNERS
- [ ] Add GitHub repository secrets

### Phase 2: Infrastructure Setup (Week 1, Days 6-7)

#### Infrastructure as Code
- [ ] Create infrastructure/terraform/main.tf
- [ ] Create infrastructure/terraform/variables.tf
- [ ] Create infrastructure/terraform/outputs.tf
- [ ] Create infrastructure/terraform/backend.tf
- [ ] Create infrastructure/k8s/namespace.yaml
- [ ] Create infrastructure/k8s/api-gateway-deployment.yaml
- [ ] Create infrastructure/k8s/queen-ai-deployment.yaml
- [ ] Create infrastructure/k8s/ingress.yaml
- [ ] Create infrastructure/k8s/secrets.yaml (template)
- [ ] Create infrastructure/helm/ charts

#### Scripts
- [ ] Create scripts/setup/init.sh
- [ ] Create scripts/setup/install-deps.sh
- [ ] Create scripts/deploy/staging.sh
- [ ] Create scripts/deploy/production.sh
- [ ] Create scripts/database/migrate.sh
- [ ] Create scripts/database/seed.sh
- [ ] Create scripts/utils/clean.sh
- [ ] Make all scripts executable (chmod +x)

### Phase 3: Documentation (Week 2)

#### Core Documentation
- [ ] Create docs/README.md
- [ ] Create docs/CONTRIBUTING.md
- [ ] Create docs/TECH_STACK.md
- [ ] Create docs/CHANGELOG.md
- [ ] Create docs/architecture/README.md
- [ ] Create docs/architecture/queen-ai.md
- [ ] Create docs/architecture/bees.md
- [ ] Create docs/architecture/contracts.md
- [ ] Create docs/architecture/database.md
- [ ] Create docs/api/README.md
- [ ] Create docs/deployment/README.md
- [ ] Create docs/deployment/gcp-setup.md
- [ ] Create docs/security/README.md

### Phase 4: Initial Dependencies Installation (Week 2)

#### Root Setup
- [ ] Run `npm install` in root
- [ ] Configure Husky git hooks
- [ ] Test root scripts (lint, format)

#### Contracts Setup
- [ ] Run `npm install` in contracts/ethereum
- [ ] Verify Hardhat installation
- [ ] Test compilation (even with empty contracts)
- [ ] Set up Solhint

#### Backend Setup
- [ ] Run `npm install` in backend/api-gateway
- [ ] Verify NestJS CLI
- [ ] Create initial NestJS modules structure
- [ ] Set up TypeORM configuration

#### Queen AI Setup
- [ ] Create Python virtual environment in backend/queen-ai
- [ ] Run `pip install -r requirements.txt`
- [ ] Verify FastAPI installation
- [ ] Test basic FastAPI server

#### Frontend Setup
- [ ] Run `npm install` in frontend/web
- [ ] Verify Next.js installation
- [ ] Set up Tailwind CSS
- [ ] Install shadcn/ui CLI and init

### Phase 5: Docker & Local Development (Week 2-3)

#### Docker Setup
- [ ] Create backend/api-gateway/Dockerfile
- [ ] Create backend/api-gateway/Dockerfile.dev
- [ ] Create backend/queen-ai/Dockerfile
- [ ] Create backend/queen-ai/Dockerfile.dev
- [ ] Create frontend/web/Dockerfile
- [ ] Create frontend/web/Dockerfile.dev
- [ ] Test docker-compose build
- [ ] Test docker-compose up
- [ ] Verify all services start correctly
- [ ] Test inter-service communication

### Phase 6: GCP Setup (Week 3)

#### Google Cloud Platform
- [ ] Create GCP account (if not exists)
- [ ] Apply for Google for Startups Cloud Program
- [ ] Create GCP project
- [ ] Enable required APIs:
  - [ ] Compute Engine API
  - [ ] Kubernetes Engine API
  - [ ] Cloud SQL Admin API
  - [ ] Cloud Storage API
  - [ ] Secret Manager API
  - [ ] Artifact Registry API
  - [ ] Cloud Build API
  - [ ] Vertex AI API
- [ ] Create service accounts
- [ ] Set up billing alerts
- [ ] Configure IAM permissions

#### Infrastructure Deployment
- [ ] Initialize Terraform
- [ ] Create Terraform state bucket
- [ ] Run `terraform plan`
- [ ] Run `terraform apply` (dev environment)
- [ ] Verify GKE cluster creation
- [ ] Verify Cloud SQL instance creation
- [ ] Verify Memorystore Redis creation
- [ ] Configure kubectl to connect to GKE

### Phase 7: CI/CD Testing (Week 3)

#### GitHub Actions
- [ ] Trigger contracts CI workflow
- [ ] Trigger backend CI workflow
- [ ] Trigger frontend CI workflow
- [ ] Trigger queen-ai CI workflow
- [ ] Fix any failing workflows
- [ ] Verify code coverage reporting
- [ ] Test deployment to staging (manual trigger)

### Phase 8: Verification & Testing (End of Week 3)

#### Local Development
- [ ] Clone repo fresh to test setup
- [ ] Run `make setup` and verify
- [ ] Run `make dev` and verify all services start
- [ ] Access frontend at localhost:3001
- [ ] Access API at localhost:3000
- [ ] Test hot reload on code changes
- [ ] Verify database connections
- [ ] Verify Redis connections

#### Documentation Verification
- [ ] Review all README files
- [ ] Verify all links work
- [ ] Check for typos
- [ ] Ensure setup instructions are accurate
- [ ] Get team member to follow setup guide

#### Repository Health
- [ ] Verify .gitignore catches all secrets
- [ ] Check no sensitive data committed
- [ ] Verify branch protection working
- [ ] Test PR workflow
- [ ] Verify CI runs on PR
- [ ] Check code review process

---

## PART 8: FILE CREATION SCRIPT

### Auto-generate Directory Structure

Create `scripts/setup/create-structure.sh`:

```bash
#!/bin/bash
set -e

echo "📁 Creating OMK Hive directory structure..."

# Root directories
mkdir -p .github/{workflows,ISSUE_TEMPLATE}
mkdir -p contracts/{ethereum,solana,bridge}
mkdir -p backend/{api-gateway,queen-ai,bees,blockchain-service,shared}
mkdir -p frontend/{web,admin}
mkdir -p infrastructure/{terraform,k8s,helm,scripts}
mkdir -p docs/{architecture,api,deployment,security,user-guides}
mkdir -p scripts/{setup,deploy,database,utils}

# Contracts subdirectories
mkdir -p contracts/ethereum/{src,test,scripts}
mkdir -p contracts/ethereum/src/{core,liquidity,treasury,staking,assets,governance,interfaces}
mkdir -p contracts/solana/{programs,tests}

# Backend subdirectories
mkdir -p backend/api-gateway/{src,test}
mkdir -p backend/api-gateway/src/{modules,common,config,guards,decorators}
mkdir -p backend/queen-ai/{src,tests}
mkdir -p backend/queen-ai/src/{core,llm,bees,learning,uagents,utils}
mkdir -p backend/queen-ai/src/llm/providers

# Bee directories
mkdir -p backend/bees/{maths-bee,logic-bee,liquidity-sentinel,treasury-bee,pattern-recognition,purchase-bee,tokenization-bee,fractional-assets,stake-bot,visualization-bee}

# Frontend subdirectories
mkdir -p frontend/web/{src,public}
mkdir -p frontend/web/src/{app,components,lib,hooks,store,styles,types}
mkdir -p frontend/web/src/components/{ui,layout,features,shared}

echo "✅ Directory structure created!"
echo ""
echo "Next: Run scripts/setup/create-files.sh to create initial files"
```

**TODO**:
- [ ] Create scripts/setup/create-structure.sh
- [ ] Make executable
- [ ] Run and verify

---

## PART 9: CRITICAL FILES SUMMARY

### Must-Have Files Before Development Starts

#### Root Level (13 files)
1. README.md
2. .gitignore
3. .gitattributes
4. .editorconfig
5. .prettierrc
6. .eslintrc.json
7. LICENSE
8. package.json
9. Makefile
10. docker-compose.yml
11. docker-compose.dev.yml
12. .env.example
13. CHANGELOG.md

#### GitHub (11 files)
1. .github/workflows/ci-contracts.yml
2. .github/workflows/ci-backend.yml
3. .github/workflows/ci-frontend.yml
4. .github/workflows/ci-queen-ai.yml
5. .github/workflows/deploy-staging.yml
6. .github/workflows/deploy-production.yml
7. .github/ISSUE_TEMPLATE/bug_report.md
8. .github/ISSUE_TEMPLATE/feature_request.md
9. .github/PULL_REQUEST_TEMPLATE.md
10. .github/CODEOWNERS
11. .github/dependabot.yml

#### Contracts/Ethereum (5 files)
1. package.json
2. hardhat.config.ts
3. tsconfig.json
4. .env.example
5. .solhint.json

#### Backend/API-Gateway (6 files)
1. package.json
2. nest-cli.json
3. tsconfig.json
4. .env.example
5. Dockerfile
6. Dockerfile.dev

#### Backend/Queen-AI (6 files)
1. requirements.txt
2. pyproject.toml
3. .env.example
4. Dockerfile
5. Dockerfile.dev
6. pytest.ini

#### Frontend/Web (7 files)
1. package.json
2. next.config.js
3. tailwind.config.ts
4. tsconfig.json
5. .env.local.example
6. Dockerfile
7. Dockerfile.dev

#### Infrastructure (8 files)
1. terraform/main.tf
2. terraform/variables.tf
3. terraform/outputs.tf
4. terraform/backend.tf
5. k8s/namespace.yaml
6. k8s/api-gateway-deployment.yaml
7. k8s/queen-ai-deployment.yaml
8. k8s/ingress.yaml

#### Scripts (6 files)
1. scripts/setup/init.sh
2. scripts/setup/create-structure.sh
3. scripts/deploy/staging.sh
4. scripts/deploy/production.sh
5. scripts/database/migrate.sh
6. scripts/utils/clean.sh

**Total Critical Files: 68**

---

## PART 10: FINAL VERIFICATION CHECKLIST

### ✅ Repository Verification

- [ ] All branches created (main, develop, staging)
- [ ] Branch protection rules configured
- [ ] Team members added with correct permissions
- [ ] Repository secrets configured
- [ ] Dependabot enabled
- [ ] Code scanning enabled

### ✅ Structure Verification

- [ ] All 68 critical files created
- [ ] Directory structure matches specification
- [ ] No empty directories (all have README or .gitkeep)
- [ ] File permissions correct (scripts executable)

### ✅ Configuration Verification

- [ ] All package.json files valid JSON
- [ ] All .env.example files created
- [ ] No actual secrets in repository
- [ ] Docker files properly configured
- [ ] CI/CD workflows syntax valid

### ✅ Dependencies Verification

- [ ] Root npm install successful
- [ ] Contracts npm install successful
- [ ] Backend npm install successful
- [ ] Queen AI pip install successful
- [ ] Frontend npm install successful
- [ ] No dependency conflicts

### ✅ Development Environment Verification

- [ ] `make setup` runs successfully
- [ ] `make dev` starts all services
- [ ] All Docker containers running
- [ ] Database accessible
- [ ] Redis accessible
- [ ] No port conflicts

### ✅ CI/CD Verification

- [ ] All workflows trigger correctly
- [ ] Tests run in CI
- [ ] Linting runs in CI
- [ ] Code coverage generated
- [ ] Deployments work (staging)

### ✅ Documentation Verification

- [ ] README clear and accurate
- [ ] Contributing guide complete
- [ ] Architecture docs created
- [ ] API docs structure ready
- [ ] Deployment docs created

---

## COMPLETION CRITERIA

Prime Task 1 is **COMPLETE** when:

1. ✅ All 68 critical files created and configured
2. ✅ Repository structure matches specification
3. ✅ All dependencies installed successfully
4. ✅ Docker development environment working
5. ✅ CI/CD pipelines functional
6. ✅ Documentation framework in place
7. ✅ Team can clone and run `make setup` successfully
8. ✅ All verification checklists passed

---

## NEXT STEPS AFTER COMPLETION

Once Prime Task 1 is complete:

1. **Proceed to Prime Task 2**: Smart Contract Core Infrastructure
2. **Begin development**: Team can start coding
3. **Daily standups**: Track progress on Prime Task 2
4. **Update CHANGELOG.md**: Document major milestones

---

## ESTIMATED EFFORT

- **Solo Developer**: 2-3 weeks
- **Small Team (2-3)**: 1-2 weeks
- **Full Team (5+)**: 4-5 days

**Priority**: HIGH - Nothing can proceed without this foundation

---

**END OF PRIME TASK 1 DETAILED SPECIFICATION**
