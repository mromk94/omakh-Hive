# Fix Fivetran GCS Connector Configuration

## Problem
Error: `Cannot invoke "com.fivetran.integrations.file.FileOptions.name()" because the return value of "com.fivetran.integrations.file.FileUpdater.fileType()" is null`

This means Fivetran doesn't know what file type to expect.

## Solution

### Option 1: Configure via Fivetran Dashboard (Easiest)

1. Go to: https://fivetran.com/dashboard/connectors/ballad_monde

2. Click **"Setup"** tab

3. Update these settings:
   ```
   File Type: JSON
   Compression: NONE
   JSON Parsing: Standard JSON (or Auto-detect)
   Path Prefix: blockchain_data/
   ```

4. Under **"Table Configuration"**:
   - Add table mapping for your files
   - Table name: `hive_mind`
   - Source: `blockchain_data/*.json`

5. Click **"Save & Test"**

6. Click **"Resume Connector"**

---

### Option 2: Restructure Data for CSV (Recommended)

Fivetran works better with CSV files. Let's convert our data:

**Run this script:**
```bash
cd /Users/mac/CascadeProjects/omakh-Hive
python3 convert_to_csv.py
python3 upload_to_gcs.py data_sync_*.csv
```

Then in Fivetran:
- File Type: `CSV`
- Delimiter: `,`
- Has Header: `YES`
- Compression: `NONE`

---

### Option 3: Use Newline-Delimited JSON

Convert JSON to NDJSON format:

**Run this:**
```bash
python3 convert_to_ndjson.py
python3 upload_to_gcs.py data_sync_*.ndjson
```

Then in Fivetran:
- File Type: `JSON`
- JSON Type: `NEWLINE_DELIMITED`

---

## Quick Fix (Try This First)

1. **Pause the connector** (it's already paused)

2. **Delete existing files from GCS**:
   ```bash
   gsutil rm gs://omk-hive-blockchain-data/blockchain_data/*.json
   ```

3. **Update Fivetran settings**:
   - File Type: `CSV`
   - Change file pattern to `*.csv`

4. **Upload CSV format**:
   ```bash
   python3 convert_to_csv.py
   gsutil cp data_sync_*.csv gs://omk-hive-blockchain-data/blockchain_data/
   ```

5. **Resume connector**

---

## Best Practice Going Forward

Use **CSV format** with these columns:

### blockchain_transactions.csv
```
timestamp,chain,transaction_hash,from_address,to_address,value,gas_price,status
2025-10-09T16:00:00Z,ethereum,0xabc...,0x123...,0x456...,1.5,30,success
```

### dex_pools.csv
```
timestamp,dex,pool_address,token_a,token_b,liquidity_usd,volume_24h
2025-10-09T16:00:00Z,uniswap,0xpool...,ETH,USDC,5000000,500000
```

### price_feeds.csv
```
timestamp,oracle,pair,price,confidence
2025-10-09T16:00:00Z,chainlink,ETH/USD,2450.50,99.9
```

This is much cleaner and Fivetran handles it perfectly!
