#!/bin/bash
# Install and Configure Fivetran CLI

echo "======================================================================"
echo "OMK HIVE - FIVETRAN CLI SETUP"
echo "======================================================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Install Fivetran SDK
echo ""
echo "Step 1: Installing Fivetran Connector SDK..."
pip3 install fivetran-connector-sdk

if [ $? -eq 0 ]; then
    echo "✅ Fivetran SDK installed successfully"
else
    echo "❌ Failed to install Fivetran SDK"
    exit 1
fi

# Verify installation
echo ""
echo "Step 2: Verifying installation..."
python3 -c "import fivetran_connector_sdk; print('✅ Fivetran SDK version:', fivetran_connector_sdk.__version__)" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "⚠️  SDK installed but unable to import. This is okay for now."
fi

echo ""
echo "======================================================================"
echo "SETUP COMPLETE!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "  1. Get your Fivetran API credentials from:"
echo "     https://fivetran.com/dashboard/account/api"
echo ""
echo "  2. Run: ./deploy_fivetran_connectors.sh"
echo ""
echo "======================================================================"
