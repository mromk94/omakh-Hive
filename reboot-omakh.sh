#!/bin/bash

##############################################
# Omakh - System Reboot
# Stops and restarts everything cleanly
##############################################

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
GOLD='\033[38;5;220m'

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo -e "${GOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GOLD}        🔄  OMAKH HIVE - REBOOT  🔄          ${NC}"
echo -e "${GOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Step 1: Stop everything
echo -e "${YELLOW}🛑  Stopping all services...${NC}"
echo ""

# Kill all Queen AI processes
QUEEN_PIDS=$(pgrep -f "python.*main.py" || true)
if [ ! -z "$QUEEN_PIDS" ]; then
    echo -e "${BLUE}🤖  Stopping Queen AI processes...${NC}"
    echo "$QUEEN_PIDS" | xargs kill -TERM 2>/dev/null || true
    sleep 2
    # Force kill if still running
    QUEEN_PIDS=$(pgrep -f "python.*main.py" || true)
    if [ ! -z "$QUEEN_PIDS" ]; then
        echo "$QUEEN_PIDS" | xargs kill -9 2>/dev/null || true
    fi
    echo -e "${GREEN}✅  Queen AI stopped${NC}"
else
    echo -e "${YELLOW}⚠️   No Queen AI processes found${NC}"
fi

# Kill all Next.js processes
NEXT_PIDS=$(pgrep -f "next dev" || true)
if [ ! -z "$NEXT_PIDS" ]; then
    echo -e "${BLUE}📱  Stopping Frontend processes...${NC}"
    echo "$NEXT_PIDS" | xargs kill -TERM 2>/dev/null || true
    sleep 2
    # Force kill if still running
    NEXT_PIDS=$(pgrep -f "next dev" || true)
    if [ ! -z "$NEXT_PIDS" ]; then
        echo "$NEXT_PIDS" | xargs kill -9 2>/dev/null || true
    fi
    echo -e "${GREEN}✅  Frontend stopped${NC}"
else
    echo -e "${YELLOW}⚠️   No Frontend processes found${NC}"
fi

# Kill any orphaned node processes on port 3001
PORT_3001_PID=$(lsof -ti:3001 || true)
if [ ! -z "$PORT_3001_PID" ]; then
    echo -e "${BLUE}🔌  Freeing port 3001...${NC}"
    kill -9 $PORT_3001_PID 2>/dev/null || true
    echo -e "${GREEN}✅  Port 3001 freed${NC}"
fi

# Kill any orphaned python processes on port 8001
PORT_8001_PID=$(lsof -ti:8001 || true)
if [ ! -z "$PORT_8001_PID" ]; then
    echo -e "${BLUE}🔌  Freeing port 8001...${NC}"
    kill -9 $PORT_8001_PID 2>/dev/null || true
    echo -e "${GREEN}✅  Port 8001 freed${NC}"
fi

echo ""
echo -e "${GREEN}✅  All services stopped${NC}"
echo ""

# Wait a moment for ports to fully release
sleep 2

# Step 2: Clear caches (optional)
echo -e "${BLUE}🧹  Clearing caches...${NC}"

# Clear Next.js cache
if [ -d "$PROJECT_ROOT/omk-frontend/.next" ]; then
    rm -rf "$PROJECT_ROOT/omk-frontend/.next"
    echo -e "${GREEN}✅  Frontend cache cleared${NC}"
fi

# Clear Python cache
find "$PROJECT_ROOT/backend/queen-ai" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT/backend/queen-ai" -type f -name "*.pyc" -delete 2>/dev/null || true
echo -e "${GREEN}✅  Backend cache cleared${NC}"

echo ""

# Step 3: Restart everything
echo -e "${GOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GOLD}        🚀  RESTARTING SERVICES...  🚀        ${NC}"
echo -e "${GOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Call the startup script
exec "$PROJECT_ROOT/start-omakh.sh"
