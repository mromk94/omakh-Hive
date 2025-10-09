#!/usr/bin/env python3
"""Check existing Fivetran setup"""
import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv('backend/queen-ai/.env')

FIVETRAN_API_KEY = os.getenv('FIVETRAN_API_KEY')
FIVETRAN_API_SECRET = os.getenv('FIVETRAN_API_SECRET')
FIVETRAN_GROUP_ID = os.getenv('FIVETRAN_GROUP_ID')

auth_string = f"{FIVETRAN_API_KEY}:{FIVETRAN_API_SECRET}"
auth_b64 = base64.b64encode(auth_string.encode('ascii')).decode('ascii')

HEADERS = {
    'Authorization': f'Basic {auth_b64}',
    'Content-Type': 'application/json'
}

print("=" * 70)
print("CHECKING YOUR FIVETRAN SETUP")
print("=" * 70)

# Get connectors
response = requests.get(
    f"https://api.fivetran.com/v1/groups/{FIVETRAN_GROUP_ID}/connectors",
    headers=HEADERS
)

if response.status_code == 200:
    connectors = response.json().get('data', {}).get('items', [])
    
    print(f"\nFound {len(connectors)} connector(s):\n")
    
    for conn in connectors:
        conn_id = conn['id']
        print(f"Connector: {conn['schema']}")
        print(f"  ID: {conn_id}")
        print(f"  Service: {conn['service']}")
        print(f"  Status: {conn['status']['setup_state']}")
        print(f"  Paused: {conn.get('paused', False)}")
        
        # Get detailed config
        detail_resp = requests.get(
            f"https://api.fivetran.com/v1/connectors/{conn_id}",
            headers=HEADERS
        )
        
        if detail_resp.status_code == 200:
            detail = detail_resp.json().get('data', {})
            config = detail.get('config', {})
            
            print(f"  Config:")
            for key, value in config.items():
                if key not in ['api_key', 'secret', 'password']:
                    print(f"    - {key}: {value}")
        
        print("-" * 70)
    
    # Check if GCS connector can be used
    gcs_connectors = [c for c in connectors if c['service'] == 'gcs']
    
    if gcs_connectors:
        print("\n✅ You have a GCS connector!")
        print("\n💡 RECOMMENDATION:")
        print("Instead of custom Fivetran connectors, we can:")
        print("1. Collect blockchain data locally (using our Python scripts)")
        print("2. Write data to your GCS bucket")
        print("3. Fivetran automatically ingests from GCS to BigQuery")
        print("\nThis is simpler and gives you more control!")
        print("\nWant me to create the GCS sync script? (yes/no)")
    else:
        print("\n⚠️  No GCS connector found")
        print("You need to complete the GCS setup in Fivetran UI")
        
else:
    print(f"Error: {response.status_code}")
    print(response.text)
