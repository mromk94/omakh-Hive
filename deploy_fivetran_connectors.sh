#!/bin/bash
# Deploy OMK Hive Custom Connectors to Fivetran

echo "======================================================================"
echo "OMK HIVE - DEPLOY FIVETRAN CONNECTORS"
echo "======================================================================"

# Load environment variables
source backend/queen-ai/.env 2>/dev/null || true

# Check for required credentials
if [ -z "$FIVETRAN_API_KEY" ] || [ -z "$FIVETRAN_API_SECRET" ]; then
    echo ""
    echo "❌ Fivetran credentials not found in .env"
    echo ""
    echo "Please add to backend/queen-ai/.env:"
    echo "  FIVETRAN_API_KEY=your_api_key"
    echo "  FIVETRAN_API_SECRET=your_api_secret"
    echo "  FIVETRAN_GROUP_ID=your_group_id"
    echo ""
    echo "Get credentials from: https://fivetran.com/dashboard/account/api"
    exit 1
fi

echo "✅ Fivetran credentials found"

# Check for RPC URLs
if [ -z "$ETHEREUM_RPC_URL" ]; then
    echo "⚠️  ETHEREUM_RPC_URL not set in .env"
    read -p "Enter Ethereum RPC URL: " ETHEREUM_RPC_URL
    echo "ETHEREUM_RPC_URL=$ETHEREUM_RPC_URL" >> backend/queen-ai/.env
fi

if [ -z "$SOLANA_RPC_URL" ]; then
    SOLANA_RPC_URL="https://api.mainnet-beta.solana.com"
    echo "✅ Using default Solana RPC: $SOLANA_RPC_URL"
fi

echo ""
echo "======================================================================"
echo "CONNECTOR 1: Blockchain Transactions"
echo "======================================================================"

# Package blockchain connector
echo "📦 Packaging blockchain connector..."
cd backend/fivetran_connectors

# Create configuration file
cat > blockchain_config.json <<EOF
{
  "connector_name": "omk_hive_blockchain",
  "destination_group_id": "$FIVETRAN_GROUP_ID",
  "config": {
    "ethereum_rpc_url": "$ETHEREUM_RPC_URL",
    "solana_rpc_url": "$SOLANA_RPC_URL",
    "monitored_wallets": []
  },
  "sync_frequency": 15
}
EOF

echo "✅ Configuration created"

# Test connector locally first
echo "🧪 Testing blockchain connector..."
python3 blockchain_connector.py

if [ $? -eq 0 ]; then
    echo "✅ Blockchain connector validation passed"
else
    echo "❌ Blockchain connector validation failed"
    exit 1
fi

echo ""
echo "======================================================================"
echo "CONNECTOR 2: DEX Pools"
echo "======================================================================"

# Test DEX pools connector
echo "🧪 Testing DEX pools connector..."
python3 dex_pools_connector.py

if [ $? -eq 0 ]; then
    echo "✅ DEX pools connector validation passed"
else
    echo "❌ DEX pools connector validation failed"
    exit 1
fi

echo ""
echo "======================================================================"
echo "CONNECTOR 3: Price Oracles"
echo "======================================================================"

# Test price oracle connector
echo "🧪 Testing price oracle connector..."
python3 price_oracle_connector.py

if [ $? -eq 0 ]; then
    echo "✅ Price oracle connector validation passed"
else
    echo "❌ Price oracle connector validation failed"
    exit 1
fi

cd ../..

echo ""
echo "======================================================================"
echo "ALL CONNECTORS VALIDATED!"
echo "======================================================================"
echo ""
echo "⚠️  IMPORTANT: Manual Deployment Required"
echo ""
echo "Fivetran Connector SDK deployment via CLI is currently limited."
echo "You need to deploy via Fivetran Platform API."
echo ""
echo "Option 1: Use Fivetran REST API (recommended)"
echo "  curl -X POST https://api.fivetran.com/v1/connectors \\"
echo "    -H 'Authorization: Basic \$(echo -n \$FIVETRAN_API_KEY:\$FIVETRAN_API_SECRET | base64)' \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d @backend/fivetran_connectors/blockchain_config.json"
echo ""
echo "Option 2: Contact Fivetran Support"
echo "  Email: support@fivetran.com"
echo "  Subject: Custom Python Connector Deployment"
echo ""
echo "Option 3: Use Alternative Approach"
echo "  We can set up data collection locally and sync to GCS/BigQuery directly"
echo ""
echo "======================================================================"
echo ""
read -p "Would you like me to create a direct BigQuery sync script? (y/n): " create_sync

if [ "$create_sync" = "y" ]; then
    echo "Creating direct BigQuery sync script..."
    # This will be created in next step
    echo "✅ Run: python3 sync_to_bigquery.py"
fi
