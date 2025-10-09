#!/usr/bin/env python3
"""
Convert JSON data to CSV format for Fivetran
Fivetran works much better with CSV files
"""
import json
import csv
import glob
from datetime import datetime

print("=" * 70)
print("CONVERTING DATA TO CSV FORMAT FOR FIVETRAN")
print("=" * 70)

# Find all JSON sync files
json_files = glob.glob("data_sync_*.json")

if not json_files:
    print("\n❌ No data_sync_*.json files found")
    print("Run: python3 sync_to_gcs.py first")
    exit(1)

print(f"\nFound {len(json_files)} JSON file(s)")

for json_file in json_files:
    print(f"\n📄 Processing: {json_file}")
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    timestamp = data.get('metadata', {}).get('collected_at', datetime.utcnow().isoformat())
    
    # Convert blockchain transactions
    if data.get('blockchain'):
        csv_file = json_file.replace('.json', '_blockchain.csv')
        print(f"  → Creating {csv_file}")
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            # Header
            writer.writerow([
                'timestamp',
                'table',
                'transaction_hash',
                'block_number',
                'from_address',
                'to_address',
                'value',
                'gas_price',
                'status'
            ])
            
            # Data rows
            for record in data['blockchain']:
                table = record.get('table', 'unknown')
                rec_data = record.get('data', {})
                writer.writerow([
                    timestamp,
                    table,
                    rec_data.get('transaction_hash', ''),
                    rec_data.get('block_number', ''),
                    rec_data.get('from_address', ''),
                    rec_data.get('to_address', ''),
                    rec_data.get('value', 0),
                    rec_data.get('gas_price', 0),
                    rec_data.get('status', 'pending')
                ])
        
        print(f"    ✓ Wrote {len(data['blockchain'])} blockchain records")
    
    # Convert DEX data
    if data.get('dex'):
        csv_file = json_file.replace('.json', '_dex.csv')
        print(f"  → Creating {csv_file}")
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            # Header
            writer.writerow([
                'timestamp',
                'table',
                'pool_address',
                'dex',
                'token_a',
                'token_b',
                'liquidity_usd',
                'volume_24h',
                'reserve_a',
                'reserve_b'
            ])
            
            # Data rows
            for record in data['dex']:
                table = record.get('table', 'unknown')
                rec_data = record.get('data', {})
                writer.writerow([
                    timestamp,
                    table,
                    rec_data.get('pool_address', ''),
                    rec_data.get('dex', 'unknown'),
                    rec_data.get('token_a', ''),
                    rec_data.get('token_b', ''),
                    rec_data.get('liquidity_usd', 0),
                    rec_data.get('volume_24h', 0),
                    rec_data.get('reserve_a', 0),
                    rec_data.get('reserve_b', 0)
                ])
        
        print(f"    ✓ Wrote {len(data['dex'])} DEX records")
    
    # Convert oracle data
    if data.get('oracle'):
        csv_file = json_file.replace('.json', '_oracle.csv')
        print(f"  → Creating {csv_file}")
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            # Header
            writer.writerow([
                'timestamp',
                'table',
                'oracle',
                'pair',
                'price',
                'confidence',
                'feed_address'
            ])
            
            # Data rows
            for record in data['oracle']:
                table = record.get('table', 'unknown')
                rec_data = record.get('data', {})
                writer.writerow([
                    timestamp,
                    table,
                    rec_data.get('oracle', 'unknown'),
                    rec_data.get('pair', ''),
                    rec_data.get('price', 0),
                    rec_data.get('confidence', 0),
                    rec_data.get('feed_address', '')
                ])
        
        print(f"    ✓ Wrote {len(data['oracle'])} oracle records")

print("\n" + "=" * 70)
print("CSV CONVERSION COMPLETE!")
print("=" * 70)

# List all CSV files
csv_files = glob.glob("data_sync_*_*.csv")
print(f"\nCreated {len(csv_files)} CSV file(s):")
for csv_file in csv_files:
    print(f"  • {csv_file}")

print("\n📤 Next steps:")
print("1. Upload to GCS:")
print("   python3 upload_to_gcs.py data_sync_*_*.csv")
print("\n2. Configure Fivetran:")
print("   - File Type: CSV")
print("   - Delimiter: comma")
print("   - Has Header: YES")
print("\n3. Resume connector in Fivetran dashboard")

print("\n✅ CSV format is much more reliable with Fivetran!")
