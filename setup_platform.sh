#!/bin/bash
# OMK Hive Platform - Quick Setup

echo "======================================================================"
echo "OMK HIVE - PLATFORM SETUP"
echo "======================================================================"

echo ""
echo "This script will help you set up credentials for:"
echo "  1. Elastic Search (AI-Powered Search & RAG)"
echo "  2. Fivetran + BigQuery (Data Pipelines)"
echo ""

ENV_FILE="backend/queen-ai/.env"

# Check if .env exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Creating .env from .env.example..."
    cp backend/queen-ai/.env.example "$ENV_FILE"
fi

echo "----------------------------------------------------------------------"
echo "STEP 1: ELASTIC SEARCH SETUP"
echo "----------------------------------------------------------------------"
echo ""
echo "1. Visit: https://cloud.elastic.co/registration"
echo "2. Sign up for 14-day free trial"
echo "3. Create a deployment (choose region closest to you)"
echo "4. Copy the Cloud ID and API Key"
echo ""
read -p "Do you have Elastic credentials? (y/n): " has_elastic

if [ "$has_elastic" = "y" ]; then
    read -p "Enter ELASTIC_CLOUD_ID: " elastic_cloud_id
    read -p "Enter ELASTIC_API_KEY: " elastic_api_key
    
    # Update .env
    sed -i.bak "s|ELASTIC_CLOUD_ID=.*|ELASTIC_CLOUD_ID=$elastic_cloud_id|" "$ENV_FILE"
    sed -i.bak "s|ELASTIC_API_KEY=.*|ELASTIC_API_KEY=$elastic_api_key|" "$ENV_FILE"
    
    echo "✅ Elastic credentials saved!"
else
    echo "⚠️  Skipping Elastic setup. You can add credentials later in $ENV_FILE"
fi

echo ""
echo "----------------------------------------------------------------------"
echo "STEP 2: FIVETRAN + BIGQUERY SETUP"
echo "----------------------------------------------------------------------"
echo ""
echo "1. Visit: https://fivetran.com/signup"
echo "2. Sign up (free 500K MAR)"
echo "3. Go to Settings → API Config"
echo "4. Generate API key and secret"
echo ""
read -p "Do you have Fivetran credentials? (y/n): " has_fivetran

if [ "$has_fivetran" = "y" ]; then
    read -p "Enter FIVETRAN_API_KEY: " fivetran_key
    read -p "Enter FIVETRAN_API_SECRET: " fivetran_secret
    read -p "Enter FIVETRAN_GROUP_ID (from dashboard): " fivetran_group
    
    # Update .env
    sed -i.bak "s|FIVETRAN_API_KEY=.*|FIVETRAN_API_KEY=$fivetran_key|" "$ENV_FILE"
    sed -i.bak "s|FIVETRAN_API_SECRET=.*|FIVETRAN_API_SECRET=$fivetran_secret|" "$ENV_FILE"
    sed -i.bak "s|FIVETRAN_GROUP_ID=.*|FIVETRAN_GROUP_ID=$fivetran_group|" "$ENV_FILE"
    
    echo "✅ Fivetran credentials saved!"
else
    echo "⚠️  Skipping Fivetran setup. You can add credentials later in $ENV_FILE"
fi

echo ""
echo "----------------------------------------------------------------------"
echo "STEP 3: BLOCKCHAIN RPC URLS (Optional - for Fivetran connectors)"
echo "----------------------------------------------------------------------"
echo ""
echo "For free RPCs:"
echo "  Ethereum: https://infura.io/ or https://alchemy.com/"
echo "  Solana: https://api.mainnet-beta.solana.com (public)"
echo ""
read -p "Do you want to add RPC URLs? (y/n): " has_rpc

if [ "$has_rpc" = "y" ]; then
    read -p "Enter ETHEREUM_RPC_URL: " eth_rpc
    read -p "Enter SOLANA_RPC_URL [https://api.mainnet-beta.solana.com]: " sol_rpc
    sol_rpc=${sol_rpc:-https://api.mainnet-beta.solana.com}
    
    # Update .env
    sed -i.bak "s|ETHEREUM_RPC_URL=.*|ETHEREUM_RPC_URL=$eth_rpc|" "$ENV_FILE"
    sed -i.bak "s|SOLANA_RPC_URL=.*|SOLANA_RPC_URL=$sol_rpc|" "$ENV_FILE"
    
    echo "✅ RPC URLs saved!"
else
    echo "⚠️  Skipping RPC setup"
fi

# Clean up backup files
rm -f "${ENV_FILE}.bak"

echo ""
echo "======================================================================"
echo "SETUP COMPLETE!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "  1. Check deployment: python3 check_deployment.py"
echo "  2. Initialize Elastic: cd backend/queen-ai && python3 initialize_elastic.py"
echo "  3. Deploy Fivetran connectors (manual via web UI)"
echo ""
echo "Full guide: DEPLOYMENT_GUIDE.md"
echo "======================================================================"
