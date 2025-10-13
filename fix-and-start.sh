#!/bin/bash

# OMK Hive - Quick Fix and Start Script
# Installs missing dependencies and starts the system

set -e

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "     🔧  OMAKH HIVE - FIX & START  🔧"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Install backend dependencies
echo "📦  Installing Python dependencies..."
cd backend/queen-ai
if pip3 install -r requirements.txt; then
    echo "✅  Python dependencies installed"
else
    echo "❌  Failed to install Python dependencies"
    echo "💡  Try: pip3 install --user -r requirements.txt"
    exit 1
fi

# Verify critical packages
echo ""
echo "🔍  Verifying installation..."
python3 -c "import anthropic, requests, psutil" 2>/dev/null && echo "✅  All required packages available" || {
    echo "❌  Some packages failed to install"
    exit 1
}

# Return to project root
cd "$SCRIPT_DIR"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "     🚀  Starting OMAKH HIVE  🚀"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start the system
./start-omakh.sh
