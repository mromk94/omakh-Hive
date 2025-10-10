#!/bin/bash

##############################################
# Omakh - System Shutdown
# Gracefully stops all services
##############################################

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
GOLD='\033[38;5;220m'

echo ""
echo -e "${GOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GOLD}      🛑  OMAKH HIVE - SHUTDOWN  🛑         ${NC}"
echo -e "${GOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Kill all Queen AI processes
QUEEN_PIDS=$(pgrep -f "python.*main.py" || true)
if [ ! -z "$QUEEN_PIDS" ]; then
    echo -e "${BLUE}🤖  Stopping Queen AI processes...${NC}"
    echo "$QUEEN_PIDS" | xargs kill -TERM 2>/dev/null || true
    
    # Wait up to 10 seconds for graceful shutdown
    for i in {1..10}; do
        QUEEN_PIDS=$(pgrep -f "python.*main.py" || true)
        if [ -z "$QUEEN_PIDS" ]; then
            break
        fi
        echo -ne "${YELLOW}   Waiting for graceful shutdown... ($i/10)\r${NC}"
        sleep 1
    done
    echo ""
    
    # Force kill if still running
    QUEEN_PIDS=$(pgrep -f "python.*main.py" || true)
    if [ ! -z "$QUEEN_PIDS" ]; then
        echo -e "${YELLOW}⚠️   Force stopping Queen AI...${NC}"
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
    
    # Wait up to 5 seconds for graceful shutdown
    for i in {1..5}; do
        NEXT_PIDS=$(pgrep -f "next dev" || true)
        if [ -z "$NEXT_PIDS" ]; then
            break
        fi
        echo -ne "${YELLOW}   Waiting for graceful shutdown... ($i/5)\r${NC}"
        sleep 1
    done
    echo ""
    
    # Force kill if still running
    NEXT_PIDS=$(pgrep -f "next dev" || true)
    if [ ! -z "$NEXT_PIDS" ]; then
        echo -e "${YELLOW}⚠️   Force stopping Frontend...${NC}"
        echo "$NEXT_PIDS" | xargs kill -9 2>/dev/null || true
    fi
    echo -e "${GREEN}✅  Frontend stopped${NC}"
else
    echo -e "${YELLOW}⚠️   No Frontend processes found${NC}"
fi

# Kill any orphaned processes on ports
PORT_3001_PID=$(lsof -ti:3001 || true)
if [ ! -z "$PORT_3001_PID" ]; then
    echo -e "${BLUE}🔌  Freeing port 3001...${NC}"
    kill -9 $PORT_3001_PID 2>/dev/null || true
    echo -e "${GREEN}✅  Port 3001 freed${NC}"
fi

PORT_8001_PID=$(lsof -ti:8001 || true)
if [ ! -z "$PORT_8001_PID" ]; then
    echo -e "${BLUE}🔌  Freeing port 8001...${NC}"
    kill -9 $PORT_8001_PID 2>/dev/null || true
    echo -e "${GREEN}✅  Port 8001 freed${NC}"
fi

echo ""
echo -e "${GOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GOLD}  ✅  OMAKH HIVE SHUTDOWN COMPLETE  ✅      ${NC}"
echo -e "${GOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
