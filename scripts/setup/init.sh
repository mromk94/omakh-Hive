#!/bin/bash
set -e

echo "🚀 OMK Hive - Initial Setup Script"
echo "===================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running in project root
if [ ! -f "package.json" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1/8: Checking prerequisites...${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is not installed. Please install Node.js 20+${NC}"
    exit 1
fi
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 20 ]; then
    echo -e "${RED}Node.js version must be 20 or higher. Current: $(node -v)${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js $(node -v)${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.11+${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $(python3 --version)${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠ Docker is not installed. You'll need it for local development.${NC}"
else
    echo -e "${GREEN}✓ Docker $(docker --version)${NC}"
fi

# Check pnpm (optional)
if command -v pnpm &> /dev/null; then
    echo -e "${GREEN}✓ pnpm $(pnpm -v)${NC}"
fi

echo ""
echo -e "${YELLOW}Step 2/8: Creating environment files...${NC}"

# Copy .env.example files
if [ ! -f "contracts/ethereum/.env" ]; then
    cp contracts/ethereum/.env.example contracts/ethereum/.env
    echo -e "${GREEN}✓ Created contracts/ethereum/.env${NC}"
fi

if [ ! -f "backend/api-gateway/.env" ]; then
    cat > backend/api-gateway/.env << EOF
NODE_ENV=development
PORT=3000
DATABASE_URL=postgresql://omk_user:omk_password@localhost:5432/omk_hive
REDIS_URL=redis://localhost:6379
QUEEN_AI_URL=http://localhost:8000
JWT_SECRET=your-secret-key-change-in-production
EOF
    echo -e "${GREEN}✓ Created backend/api-gateway/.env${NC}"
fi

if [ ! -f "backend/queen-ai/.env" ]; then
    cat > backend/queen-ai/.env << EOF
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=postgresql://omk_user:omk_password@localhost:5432/omk_hive
REDIS_URL=redis://localhost:6379
DEFAULT_LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GROK_API_KEY=your_grok_key
EOF
    echo -e "${GREEN}✓ Created backend/queen-ai/.env${NC}"
fi

if [ ! -f "frontend/web/.env.local" ]; then
    cat > frontend/web/.env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:3000
NEXT_PUBLIC_CHAIN_ID=1
NEXT_PUBLIC_ENABLE_TESTNETS=true
EOF
    echo -e "${GREEN}✓ Created frontend/web/.env.local${NC}"
fi

echo ""
echo -e "${YELLOW}Step 3/8: Installing root dependencies...${NC}"
npm install
echo -e "${GREEN}✓ Root dependencies installed${NC}"

echo ""
echo -e "${YELLOW}Step 4/8: Installing contract dependencies...${NC}"
cd contracts/ethereum && npm install && cd ../..
echo -e "${GREEN}✓ Contract dependencies installed${NC}"

echo ""
echo -e "${YELLOW}Step 5/8: Installing backend dependencies...${NC}"
cd backend/api-gateway && npm install && cd ../..
echo -e "${GREEN}✓ API Gateway dependencies installed${NC}"

echo ""
echo -e "${YELLOW}Step 6/8: Installing Queen AI dependencies...${NC}"
cd backend/queen-ai
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
cd ../..
echo -e "${GREEN}✓ Queen AI dependencies installed${NC}"

echo ""
echo -e "${YELLOW}Step 7/8: Installing frontend dependencies...${NC}"
cd frontend/web && npm install && cd ../..
echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

echo ""
echo -e "${YELLOW}Step 8/8: Setting up Git hooks...${NC}"
npx husky install
echo -e "${GREEN}✓ Git hooks configured${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Setup complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo ""
echo "1. Update .env files with your API keys:"
echo "   - contracts/ethereum/.env"
echo "   - backend/api-gateway/.env"
echo "   - backend/queen-ai/.env"
echo "   - frontend/web/.env.local"
echo ""
echo "2. Start the development environment:"
echo "   ${GREEN}make dev${NC}"
echo ""
echo "3. Or start services individually:"
echo "   ${GREEN}make dev-services${NC}  (Start databases only)"
echo "   ${GREEN}cd backend/api-gateway && npm run start:dev${NC}"
echo "   ${GREEN}cd backend/queen-ai && source venv/bin/activate && uvicorn main:app --reload${NC}"
echo "   ${GREEN}cd frontend/web && npm run dev${NC}"
echo ""
echo "4. Access the services:"
echo "   - Frontend: http://localhost:3001"
echo "   - API Gateway: http://localhost:3000"
echo "   - Queen AI: http://localhost:8000"
echo ""
echo -e "${YELLOW}For more information, see README.md${NC}"
