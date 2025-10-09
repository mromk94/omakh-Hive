#!/bin/bash
# Install dependencies in small chunks to avoid hanging
# Run from backend/queen-ai directory

echo "🐝 OMK HIVE - Dependency Installation Script"
echo "============================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate venv
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip first
echo "📦 Upgrading pip..."
pip install --upgrade pip
echo "✅ Pip upgraded"
echo ""

# Install in chunks
echo "📦 Installing core dependencies (chunk 1/6)..."
pip install fastapi uvicorn python-dotenv pydantic-settings
echo "✅ Chunk 1 complete"
echo ""

echo "📦 Installing web3 and blockchain (chunk 2/6)..."
pip install web3 eth-account
echo "✅ Chunk 2 complete"
echo ""

echo "📦 Installing logging (chunk 3/6)..."
pip install structlog
echo "✅ Chunk 3 complete"
echo ""

echo "📦 Installing LLM providers (chunk 4/6)..."
pip install google-generativeai openai anthropic
echo "✅ Chunk 4 complete"
echo ""

echo "📦 Installing utilities (chunk 5/6)..."
pip install aiofiles python-multipart httpx
echo "✅ Chunk 5 complete"
echo ""

echo "📦 Installing testing tools (chunk 6/6)..."
pip install pytest pytest-asyncio
echo "✅ Chunk 6 complete"
echo ""

echo "🎉 All dependencies installed successfully!"
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run the Queen AI:"
echo "  uvicorn app.main:app --reload"
echo ""
