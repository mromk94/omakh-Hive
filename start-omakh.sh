#!/bin/bash

##############################################
# Omakh - Complete System Startup
# Starts Queen AI Backend + Frontend
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
BACKEND_DIR="$PROJECT_ROOT/backend/queen-ai"
FRONTEND_DIR="$PROJECT_ROOT/omk-frontend"

# PID files for cleanup
BACKEND_PID=""
FRONTEND_PID=""

echo ""
echo -e "${GOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GOLD}         👑  OMAKH HIVE - STARTUP  👑         ${NC}"
echo -e "${GOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Cleanup function - graceful shutdown
cleanup() {
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}  🛑  Shutting down gracefully...${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Kill frontend and all its children
    if [ ! -z "$FRONTEND_PID" ]; then
        echo -e "${BLUE}📱  Stopping Frontend (PID: $FRONTEND_PID)...${NC}"
        pkill -P "$FRONTEND_PID" 2>/dev/null || true
        kill -TERM "$FRONTEND_PID" 2>/dev/null || true
        wait "$FRONTEND_PID" 2>/dev/null || true
        # Kill any remaining processes on port 3001
        lsof -ti:3001 | xargs kill -9 2>/dev/null || true
        echo -e "${GREEN}✅  Frontend stopped${NC}"
    fi
    
    # Kill backend and all its children
    if [ ! -z "$BACKEND_PID" ]; then
        echo -e "${BLUE}🤖  Stopping Queen AI (PID: $BACKEND_PID)...${NC}"
        pkill -P "$BACKEND_PID" 2>/dev/null || true
        kill -TERM "$BACKEND_PID" 2>/dev/null || true
        wait "$BACKEND_PID" 2>/dev/null || true
        # Kill any remaining processes on port 8001
        lsof -ti:8001 | xargs kill -9 2>/dev/null || true
        echo -e "${GREEN}✅  Queen AI stopped${NC}"
    fi
    
    echo ""
    echo -e "${GOLD}👑  Omakh Hive shut down successfully  👑${NC}"
    echo ""
    exit 0
}

# Trap Ctrl+C and other termination signals
trap cleanup SIGINT SIGTERM EXIT

# Check if Queen backend .env exists
echo -e "${BLUE}🔍  Checking configuration...${NC}"
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo -e "${RED}❌  Backend .env file not found!${NC}"
    echo -e "${YELLOW}📝  Creating from .env.example...${NC}"
    if [ -f "$BACKEND_DIR/.env.example" ]; then
        cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
        echo -e "${YELLOW}⚠️   Please edit $BACKEND_DIR/.env with your API keys${NC}"
        echo -e "${YELLOW}⚠️   Especially: GOOGLE_API_KEY (for Gemini)${NC}"
        echo ""
        read -p "Press Enter after setting up .env file..."
    else
        echo -e "${RED}❌  .env.example not found either!${NC}"
        exit 1
    fi
fi

# Check if frontend .env.local exists
if [ ! -f "$FRONTEND_DIR/.env.local" ]; then
    echo -e "${YELLOW}📝  Creating frontend .env.local...${NC}"
    echo "NEXT_PUBLIC_QUEEN_API_URL=http://localhost:8001" > "$FRONTEND_DIR/.env.local"
    echo -e "${GREEN}✅  Created .env.local${NC}"
fi

echo -e "${GREEN}✅  Configuration verified${NC}"
echo ""

# Kill any existing processes on ports 8001 and 3001
echo -e "${BLUE}🧹  Cleaning up old processes...${NC}"
lsof -ti:8001 | xargs kill -9 2>/dev/null || true
lsof -ti:3001 | xargs kill -9 2>/dev/null || true
echo -e "${GREEN}✅  Cleanup complete${NC}"
echo ""

# Start Queen AI Backend
echo -e "${GOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GOLD}  🤖  Starting Queen AI Backend...${NC}"
echo -e "${GOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$BACKEND_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦  Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies if needed
if [ ! -f "venv/.installed" ] || [ "requirements.txt" -nt "venv/.installed" ]; then
    echo -e "${YELLOW}📦  Installing/updating dependencies...${NC}"
    pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt
    touch venv/.installed
    echo -e "${GREEN}✅  Dependencies installed${NC}"
fi

# Start Queen AI in background
echo -e "${BLUE}🚀  Launching Queen AI on port 8001...${NC}"
./venv/bin/python main.py > "$PROJECT_ROOT/logs/queen-backend.log" 2>&1 &
BACKEND_PID=$!

echo -e "${GREEN}✅  Queen AI started (PID: $BACKEND_PID)${NC}"

# Wait for backend to be ready
echo -e "${BLUE}⏳  Waiting for Queen AI to initialize...${NC}"
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅  Queen AI is operational!${NC}"
        break
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
    if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
        echo -e "${RED}❌  Queen AI failed to start${NC}"
        echo -e "${YELLOW}📋  Check logs: $PROJECT_ROOT/logs/queen-backend.log${NC}"
        exit 1
    fi
    
    echo -ne "${YELLOW}   Attempt $ATTEMPT/$MAX_ATTEMPTS...\r${NC}"
    sleep 1
done

echo ""

# Start Frontend
echo -e "${GOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GOLD}  📱  Starting Frontend...${NC}"
echo -e "${GOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$FRONTEND_DIR"

# Install dependencies if needed
if [ ! -d "node_modules" ] || [ "package.json" -nt "node_modules/.installed" ]; then
    echo -e "${YELLOW}📦  Installing npm packages...${NC}"
    npm install --silent
    touch node_modules/.installed
    echo -e "${GREEN}✅  NPM packages installed${NC}"
fi

# Start Next.js in background
echo -e "${BLUE}🚀  Launching Next.js on port 3001...${NC}"
npm run dev > "$PROJECT_ROOT/logs/frontend.log" 2>&1 &
FRONTEND_PID=$!

echo -e "${GREEN}✅  Frontend started (PID: $FRONTEND_PID)${NC}"

# Wait for frontend to be ready
echo -e "${BLUE}⏳  Waiting for Frontend to initialize...${NC}"
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -s http://localhost:3001 > /dev/null 2>&1; then
        echo -e "${GREEN}✅  Frontend is ready!${NC}"
        break
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
    if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
        echo -e "${RED}❌  Frontend failed to start${NC}"
        echo -e "${YELLOW}📋  Check logs: $PROJECT_ROOT/logs/frontend.log${NC}"
        exit 1
    fi
    
    echo -ne "${YELLOW}   Attempt $ATTEMPT/$MAX_ATTEMPTS...\r${NC}"
    sleep 1
done

echo ""
echo -e "${GOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GOLD}         ✅  OMAKH HIVE IS LIVE!  ✅         ${NC}"
echo -e "${GOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}🤖  Queen AI Backend:  ${BLUE}http://localhost:8001${NC}"
echo -e "${GREEN}📱  Frontend:          ${BLUE}http://localhost:3001${NC}"
echo ""
echo -e "${YELLOW}📊  Logs:${NC}"
echo -e "${BLUE}   Backend:  $PROJECT_ROOT/logs/queen-backend.log${NC}"
echo -e "${BLUE}   Frontend: $PROJECT_ROOT/logs/frontend.log${NC}"
echo ""
echo -e "${YELLOW}💡  Press Ctrl+C to stop all services${NC}"
echo ""
echo -e "${GOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Open browser (optional)
if command -v open &> /dev/null; then
    sleep 2
    open http://localhost:3001
fi

# Keep script running and wait for signals
wait
