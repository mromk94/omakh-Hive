#!/bin/bash

echo "🧹 Cleaning OMK Hive project..."
echo "================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Cleaning node_modules...${NC}"
find . -name "node_modules" -type d -prune -exec rm -rf '{}' +
echo -e "${GREEN}✓ node_modules cleaned${NC}"

echo -e "${YELLOW}Cleaning Python virtual environments...${NC}"
find . -name "venv" -type d -prune -exec rm -rf '{}' +
find . -name ".venv" -type d -prune -exec rm -rf '{}' +
find . -name "__pycache__" -type d -prune -exec rm -rf '{}' +
find . -name "*.pyc" -delete
echo -e "${GREEN}✓ Python environments cleaned${NC}"

echo -e "${YELLOW}Cleaning build artifacts...${NC}"
rm -rf contracts/ethereum/artifacts
rm -rf contracts/ethereum/cache
rm -rf contracts/ethereum/typechain-types
rm -rf backend/api-gateway/dist
rm -rf frontend/web/.next
rm -rf frontend/web/out
echo -e "${GREEN}✓ Build artifacts cleaned${NC}"

echo -e "${YELLOW}Cleaning test coverage...${NC}"
find . -name "coverage" -type d -prune -exec rm -rf '{}' +
find . -name ".nyc_output" -type d -prune -exec rm -rf '{}' +
find . -name "htmlcov" -type d -prune -exec rm -rf '{}' +
find . -name ".coverage" -delete
find . -name "*.lcov" -delete
echo -e "${GREEN}✓ Coverage reports cleaned${NC}"

echo -e "${YELLOW}Cleaning logs...${NC}"
rm -rf logs/*.log
echo -e "${GREEN}✓ Logs cleaned${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Cleanup complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Run './scripts/setup/init.sh' to reinstall dependencies"
