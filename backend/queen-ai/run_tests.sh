#!/bin/bash

echo "🧪 Running OMK Hive Database Tests"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if database exists
echo "📊 Checking database..."
if mysql -u root -p'Successtrain2025@@' -e "USE \`omk-hive1\`" 2>/dev/null; then
    echo -e "${GREEN}✅ Database 'omk-hive1' exists${NC}"
else
    echo -e "${RED}❌ Database 'omk-hive1' not found${NC}"
    echo -e "${YELLOW}⚠️  Run ./setup_database.sh first${NC}"
    exit 1
fi

# Check if MySQL is running
echo "🔍 Checking MySQL service..."
if pgrep -x "mysqld" > /dev/null; then
    echo -e "${GREEN}✅ MySQL is running${NC}"
else
    echo -e "${RED}❌ MySQL is not running${NC}"
    echo "Start MySQL with: brew services start mysql"
    exit 1
fi

echo ""
echo "🧪 Running tests..."
echo ""

# Run pytest with verbose output
pytest tests/ -v -s --tb=short

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
