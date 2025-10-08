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
mkdir -p contracts/bridge/{ethereum,solana,relayer}

# Backend subdirectories
mkdir -p backend/api-gateway/{src,test}
mkdir -p backend/api-gateway/src/{modules,common,config,guards,decorators}
mkdir -p backend/queen-ai/{src,tests}
mkdir -p backend/queen-ai/src/{core,llm,bees,learning,uagents,utils}
mkdir -p backend/queen-ai/src/llm/providers
mkdir -p backend/queen-ai/src/api

# Bee directories
mkdir -p backend/bees/{maths-bee,logic-bee,liquidity-sentinel,treasury-bee,pattern-recognition,purchase-bee,tokenization-bee,fractional-assets,stake-bot,visualization-bee}

# Frontend subdirectories
mkdir -p frontend/web/{src,public}
mkdir -p frontend/web/src/{app,components,lib,hooks,store,styles,types}
mkdir -p frontend/web/src/components/{ui,layout,features,shared}
mkdir -p frontend/web/public/{images,fonts}

# Infrastructure subdirectories
mkdir -p infrastructure/terraform/{modules,environments}
mkdir -p infrastructure/k8s/{base,overlays}
mkdir -p infrastructure/helm/{charts,values}

# Documentation subdirectories
mkdir -p docs/architecture
mkdir -p docs/api
mkdir -p docs/deployment

# Create .gitkeep files in empty directories
find . -type d -empty -exec touch {}/.gitkeep \;

echo "✅ Directory structure created successfully!"
echo ""
echo "Directory tree:"
tree -L 3 -d
