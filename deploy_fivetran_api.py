#!/usr/bin/env python3
"""
Deploy OMK Hive connectors via Fivetran REST API
"""
import os
import json
import base64
import requests
from dotenv import load_dotenv

load_dotenv('backend/queen-ai/.env')

# Get credentials
FIVETRAN_API_KEY = os.getenv('FIVETRAN_API_KEY')
FIVETRAN_API_SECRET = os.getenv('FIVETRAN_API_SECRET')
FIVETRAN_GROUP_ID = os.getenv('FIVETRAN_GROUP_ID')
ETHEREUM_RPC_URL = os.getenv('ETHEREUM_RPC_URL')
SOLANA_RPC_URL = os.getenv('SOLANA_RPC_URL')

# Fivetran API base
BASE_URL = "https://api.fivetran.com/v1"

# Create auth header
auth_string = f"{FIVETRAN_API_KEY}:{FIVETRAN_API_SECRET}"
auth_bytes = auth_string.encode('ascii')
auth_b64 = base64.b64encode(auth_bytes).decode('ascii')

HEADERS = {
    'Authorization': f'Basic {auth_b64}',
    'Content-Type': 'application/json'
}

def test_connection():
    """Test API connection"""
    print("=" * 70)
    print("FIVETRAN API - CONNECTION TEST")
    print("=" * 70)
    print(f"\nAPI Key: {FIVETRAN_API_KEY[:10]}...")
    print(f"Group ID: {FIVETRAN_GROUP_ID}")
    
    # Get user info
    response = requests.get(f"{BASE_URL}/users", headers=HEADERS)
    
    if response.status_code == 200:
        print("\n✅ API connection successful!")
        data = response.json()
        print(f"User: {data.get('data', {}).get('email', 'N/A')}")
        return True
    else:
        print(f"\n❌ API connection failed: {response.status_code}")
        print(f"Error: {response.text}")
        return False

def list_connectors():
    """List existing connectors in group"""
    print("\n" + "=" * 70)
    print("EXISTING CONNECTORS")
    print("=" * 70)
    
    response = requests.get(
        f"{BASE_URL}/groups/{FIVETRAN_GROUP_ID}/connectors",
        headers=HEADERS
    )
    
    if response.status_code == 200:
        connectors = response.json().get('data', {}).get('items', [])
        print(f"\nFound {len(connectors)} connector(s)")
        for conn in connectors:
            print(f"  - {conn.get('schema')}: {conn.get('service')} ({conn.get('id')})")
        return connectors
    else:
        print(f"❌ Failed to list connectors: {response.text}")
        return []

def create_connector(name, schema, service_type, config):
    """Create a new connector"""
    print(f"\nCreating connector: {name}")
    
    payload = {
        "service": service_type,
        "group_id": FIVETRAN_GROUP_ID,
        "schema": schema,
        "config": config,
        "paused": False,
        "sync_frequency": 15  # 15 minutes
    }
    
    response = requests.post(
        f"{BASE_URL}/connectors",
        headers=HEADERS,
        json=payload
    )
    
    if response.status_code in [200, 201]:
        data = response.json().get('data', {})
        connector_id = data.get('id')
        print(f"✅ Created connector: {connector_id}")
        return connector_id
    else:
        print(f"❌ Failed to create connector")
        print(f"Status: {response.status_code}")
        print(f"Error: {response.text}")
        return None

def setup_connector_schema(connector_id, schema_config):
    """Set up connector schema"""
    response = requests.patch(
        f"{BASE_URL}/connectors/{connector_id}/schemas",
        headers=HEADERS,
        json=schema_config
    )
    
    if response.status_code == 200:
        print(f"✅ Schema configured for {connector_id}")
        return True
    else:
        print(f"⚠️  Schema setup returned: {response.status_code}")
        return False

def deploy_blockchain_connector():
    """Deploy blockchain transactions connector"""
    print("\n" + "=" * 70)
    print("CONNECTOR 1: Blockchain Transactions")
    print("=" * 70)
    
    config = {
        "connector_url": "https://github.com/mromk94/omakh-Hive/raw/main/backend/fivetran_connectors/blockchain_connector.py",
        "ethereum_rpc_url": ETHEREUM_RPC_URL,
        "solana_rpc_url": SOLANA_RPC_URL,
        "monitored_wallets": []
    }
    
    connector_id = create_connector(
        name="OMK Hive - Blockchain",
        schema="omk_blockchain_data",
        service_type="python_connector",
        config=config
    )
    
    return connector_id

def deploy_dex_connector():
    """Deploy DEX pools connector"""
    print("\n" + "=" * 70)
    print("CONNECTOR 2: DEX Pools")
    print("=" * 70)
    
    config = {
        "connector_url": "https://github.com/mromk94/omakh-Hive/raw/main/backend/fivetran_connectors/dex_pools_connector.py",
        "ethereum_rpc_url": ETHEREUM_RPC_URL,
        "monitored_pools": []
    }
    
    connector_id = create_connector(
        name="OMK Hive - DEX Pools",
        schema="omk_dex_data",
        service_type="python_connector",
        config=config
    )
    
    return connector_id

def deploy_oracle_connector():
    """Deploy price oracle connector"""
    print("\n" + "=" * 70)
    print("CONNECTOR 3: Price Oracles")
    print("=" * 70)
    
    config = {
        "connector_url": "https://github.com/mromk94/omakh-Hive/raw/main/backend/fivetran_connectors/price_oracle_connector.py",
        "ethereum_rpc_url": ETHEREUM_RPC_URL
    }
    
    connector_id = create_connector(
        name="OMK Hive - Price Oracles",
        schema="omk_price_data",
        service_type="python_connector",
        config=config
    )
    
    return connector_id

def main():
    """Main deployment flow"""
    print("\n" + "=" * 70)
    print("OMK HIVE - FIVETRAN API DEPLOYMENT")
    print("=" * 70)
    
    # Test connection
    if not test_connection():
        print("\n❌ Cannot proceed without API connection")
        return
    
    # List existing connectors
    existing = list_connectors()
    
    # Ask for confirmation
    print("\n" + "=" * 70)
    print("READY TO DEPLOY")
    print("=" * 70)
    print("\nThis will create 3 custom connectors:")
    print("  1. Blockchain Transactions (ETH + SOL)")
    print("  2. DEX Pools (Uniswap + Raydium)")
    print("  3. Price Oracles (Chainlink + Pyth)")
    print(f"\nGroup ID: {FIVETRAN_GROUP_ID}")
    print(f"Sync Frequency: Every 15 minutes")
    
    response = input("\nProceed with deployment? (yes/no): ")
    
    if response.lower() != 'yes':
        print("\n❌ Deployment cancelled")
        return
    
    # Deploy connectors
    print("\n" + "=" * 70)
    print("DEPLOYING CONNECTORS")
    print("=" * 70)
    
    connectors = []
    
    # Try to deploy each connector
    print("\nAttempting to create connectors via API...")
    
    # 1. Blockchain connector
    blockchain_id = create_connector(
        name="OMK Hive - Blockchain",
        schema="omk_blockchain_data",
        service_type="function",  # Try function type
        config={
            "function": "connector",
            "config": {
                "ethereum_rpc_url": ETHEREUM_RPC_URL,
                "solana_rpc_url": SOLANA_RPC_URL
            }
        }
    )
    if blockchain_id:
        connectors.append(("Blockchain", blockchain_id))
    
    # 2. DEX connector
    dex_id = create_connector(
        name="OMK Hive - DEX Pools",
        schema="omk_dex_data",
        service_type="function",
        config={
            "function": "connector",
            "config": {
                "ethereum_rpc_url": ETHEREUM_RPC_URL
            }
        }
    )
    if dex_id:
        connectors.append(("DEX", dex_id))
    
    # 3. Oracle connector
    oracle_id = create_connector(
        name="OMK Hive - Price Oracles",
        schema="omk_price_data",
        service_type="function",
        config={
            "function": "connector",
            "config": {
                "ethereum_rpc_url": ETHEREUM_RPC_URL
            }
        }
    )
    if oracle_id:
        connectors.append(("Oracle", oracle_id))
    
    print("\n" + "=" * 70)
    print("DEPLOYMENT SUMMARY")
    print("=" * 70)
    
    if connectors:
        print(f"\n✅ Successfully created {len(connectors)} connector(s):")
        for name, conn_id in connectors:
            print(f"  - {name}: {conn_id}")
        
        print("\n📝 Next steps:")
        print("1. Go to Fivetran dashboard to configure each connector")
        print("2. Upload Python files via web UI (API limitation)")
        print("3. Set sync schedule and test")
    else:
        print("\n⚠️  API deployment failed - using web UI method:")
        print("\n1. Go to: https://fivetran.com/dashboard/connectors")
        print("2. Click 'Add Connector' → 'Connector SDK'")
        print("3. Upload each connector file from backend/fivetran_connectors/")
        print(f"4. Use these configs:")
        print(f"   - ethereum_rpc_url: {ETHEREUM_RPC_URL}")
        print(f"   - solana_rpc_url: {SOLANA_RPC_URL}")
        print(f"   - Destination: moss_against group")

if __name__ == "__main__":
    main()
