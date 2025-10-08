#!/bin/bash
set -e

echo "🗄️  Database Migration Script"
echo "============================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
ENVIRONMENT=${1:-development}

case $ENVIRONMENT in
    development)
        DB_URL=${DATABASE_URL:-"postgresql://omk_user:omk_password@localhost:5432/omk_hive"}
        ;;
    staging)
        DB_URL=${STAGING_DATABASE_URL}
        ;;
    production)
        DB_URL=${PRODUCTION_DATABASE_URL}
        echo -e "${RED}⚠️  WARNING: Running migrations on PRODUCTION!${NC}"
        read -p "Are you sure? (yes/no): " -r
        if [[ ! $REPLY =~ ^yes$ ]]; then
            echo "Migration cancelled."
            exit 1
        fi
        ;;
    *)
        echo -e "${RED}Invalid environment: $ENVIRONMENT${NC}"
        echo "Usage: $0 [development|staging|production]"
        exit 1
        ;;
esac

echo -e "${YELLOW}Environment: ${ENVIRONMENT}${NC}"
echo ""

# Run API Gateway migrations
echo -e "${YELLOW}Running API Gateway migrations...${NC}"
cd backend/api-gateway
npm run migration:run
echo -e "${GREEN}✓ API Gateway migrations complete${NC}"

# Run Queen AI migrations (if using Alembic)
echo -e "${YELLOW}Running Queen AI migrations...${NC}"
cd ../queen-ai
if [ -f "alembic.ini" ]; then
    source venv/bin/activate
    alembic upgrade head
    deactivate
    echo -e "${GREEN}✓ Queen AI migrations complete${NC}"
else
    echo -e "${YELLOW}⚠ No Alembic configuration found, skipping${NC}"
fi

cd ../..

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ All migrations complete!${NC}"
echo -e "${GREEN}========================================${NC}"
