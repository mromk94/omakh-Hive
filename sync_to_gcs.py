#!/usr/bin/env python3
"""
Sync blockchain data to GCS for Fivetran ingestion
Works with your existing GCS connector: omk-hive-blockchain-data
"""
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, 'backend/fivetran_connectors')

from blockchain_connector import BlockchainConnector
from dex_pools_connector import DEXPoolsConnector
from price_oracle_connector import PriceOracleConnector

load_dotenv('backend/queen-ai/.env')

# GCS setup
GCS_BUCKET = "omk-hive-blockchain-data"
ETHEREUM_RPC_URL = os.getenv('ETHEREUM_RPC_URL')
SOLANA_RPC_URL = os.getenv('SOLANA_RPC_URL')

print("=" * 70)
print("OMK HIVE → GCS SYNC")
print("=" * 70)
print(f"\nBucket: {GCS_BUCKET}")
print(f"Timestamp: {datetime.utcnow().isoformat()}")

# Initialize connectors
print("\n📊 Initializing connectors...")

blockchain_config = {
    "ethereum_rpc_url": ETHEREUM_RPC_URL,
    "solana_rpc_url": SOLANA_RPC_URL,
    "monitored_wallets": []
}

dex_config = {
    "ethereum_rpc_url": ETHEREUM_RPC_URL,
    "monitored_pools": []
}

oracle_config = {
    "ethereum_rpc_url": ETHEREUM_RPC_URL
}

try:
    blockchain = BlockchainConnector(blockchain_config)
    dex = DEXPoolsConnector(dex_config)
    oracle = PriceOracleConnector(oracle_config)
    print("✅ Connectors initialized")
except Exception as e:
    print(f"❌ Failed to initialize connectors: {e}")
    sys.exit(1)

# Collect data
print("\n🔄 Collecting blockchain data...")

all_data = {
    "blockchain": [],
    "dex": [],
    "oracle": [],
    "metadata": {
        "collected_at": datetime.utcnow().isoformat(),
        "ethereum_rpc": ETHEREUM_RPC_URL,
        "solana_rpc": SOLANA_RPC_URL
    }
}

try:
    # Collect blockchain transactions
    print("  • Blockchain transactions...")
    state = {}
    count = 0
    for table, record in blockchain.update(state):
        all_data["blockchain"].append({
            "table": table,
            "data": record
        })
        count += 1
        if count >= 10:  # Limit for first sync
            break
    print(f"    ✓ Collected {count} blockchain records")
    
    # Collect DEX data
    print("  • DEX pools...")
    state = {}
    count = 0
    for table, record in dex.update(state):
        all_data["dex"].append({
            "table": table,
            "data": record
        })
        count += 1
        if count >= 10:
            break
    print(f"    ✓ Collected {count} DEX records")
    
    # Collect oracle data
    print("  • Price oracles...")
    state = {}
    count = 0
    for table, record in oracle.update(state):
        all_data["oracle"].append({
            "table": table,
            "data": record
        })
        count += 1
        if count >= 10:
            break
    print(f"    ✓ Collected {count} oracle records")
    
except Exception as e:
    print(f"❌ Data collection failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Write to local file (for now)
output_file = f"data_sync_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
print(f"\n💾 Writing to: {output_file}")

# Convert datetime objects to strings
def convert_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

with open(output_file, 'w') as f:
    json.dump(all_data, f, indent=2, default=convert_datetime)

print(f"✅ Data written: {output_file}")

# Summary
total_records = (
    len(all_data["blockchain"]) + 
    len(all_data["dex"]) + 
    len(all_data["oracle"])
)

print("\n" + "=" * 70)
print("SYNC COMPLETE")
print("=" * 70)
print(f"\nTotal records collected: {total_records}")
print(f"  • Blockchain: {len(all_data['blockchain'])}")
print(f"  • DEX: {len(all_data['dex'])}")
print(f"  • Oracle: {len(all_data['oracle'])}")

print("\n📤 Next step: Upload to GCS")
print(f"   gsutil cp {output_file} gs://{GCS_BUCKET}/")
print(f"\n   Or use: python3 upload_to_gcs.py {output_file}")

print("\n✅ Once uploaded, Fivetran will automatically sync to BigQuery!")
