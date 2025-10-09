# 🐝 DataPipelineBee - Automated Data Collection & Sync

**Fully automated blockchain data pipeline - no manual commands needed!**

## Overview

DataPipelineBee automatically handles the entire data collection and synchronization workflow:

1. **Collects** blockchain data (transactions, DEX pools, price oracles)
2. **Converts** to CSV format (Fivetran-compatible)
3. **Uploads** to GCS bucket
4. **Monitors** Fivetran sync status
5. **Reports** to Queen AI

**No more manual commands** - the bee does everything!

---

## Quick Start

### Manual Trigger (One-Time)

```python
# Run the pipeline once
await bee_manager.execute_bee("data_pipeline", {
    "type": "run_pipeline"
})
```

### Scheduled Automation (Recommended)

```python
# Schedule pipeline to run every 15 minutes
await bee_manager.execute_bee("data_pipeline", {
    "type": "schedule_pipeline",
    "interval_minutes": 15
})
```

**That's it!** The bee handles everything from now on.

---

## Architecture

```
┌─────────────────────────────────────────┐
│        Queen AI / Scheduler             │
│    (Triggers every 15 minutes)          │
└───────────────┬─────────────────────────┘
                │
                ▼
     ┌──────────────────────┐
     │  DataPipelineBee     │
     └──────────┬───────────┘
                │
    ┌───────────┼───────────┐
    │           │           │
    ▼           ▼           ▼
┌────────┐ ┌────────┐ ┌────────┐
│Collect │ │Convert │ │Upload  │
│ Data   │ │to CSV  │ │to GCS  │
└────────┘ └────────┘ └────────┘
                          │
                          ▼
                  ┌───────────────┐
                  │   Fivetran    │
                  │  (Auto-sync)  │
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │   BigQuery    │
                  │ (Data ready!) │
                  └───────────────┘
```

---

## Available Operations

### 1. Run Full Pipeline

**Executes the complete workflow**

```python
result = await bee_manager.execute_bee("data_pipeline", {
    "type": "run_pipeline"
})

# Returns:
{
    "success": True,
    "duration_seconds": 12.5,
    "total_records": 18,
    "csv_files_uploaded": 3,
    "gcs_bucket": "omk-hive-blockchain-data",
    "steps": {
        "collect": {...},
        "convert": {...},
        "upload": {...}
    }
}
```

### 2. Get Pipeline Status

**Check pipeline health**

```python
status = await bee_manager.execute_bee("data_pipeline", {
    "type": "get_pipeline_status"
})

# Returns:
{
    "success": True,
    "status": {
        "run_count": 5,
        "error_count": 0,
        "last_run": "2025-10-09T17:45:00Z",
        "last_success": "2025-10-09T17:45:00Z",
        "schedule_interval_minutes": 15,
        "gcs_bucket": "omk-hive-blockchain-data",
        "gcs_available": True
    }
}
```

### 3. Schedule Pipeline

**Automate recurring runs**

```python
schedule = await bee_manager.execute_bee("data_pipeline", {
    "type": "schedule_pipeline",
    "interval_minutes": 15  # Run every 15 minutes
})

# Returns:
{
    "success": True,
    "message": "Pipeline scheduled to run every 15 minutes",
    "next_run": "2025-10-09T18:00:00Z"
}
```

### 4. Collect Data Only

**Just collect without uploading**

```python
data = await bee_manager.execute_bee("data_pipeline", {
    "type": "collect_data"
})

# Returns:
{
    "success": True,
    "output_file": "data_sync_20251009_174500.json",
    "total_records": 18,
    "blockchain_records": 10,
    "dex_records": 3,
    "oracle_records": 5
}
```

### 5. Convert to CSV

**Convert existing JSON to CSV**

```python
csv = await bee_manager.execute_bee("data_pipeline", {
    "type": "convert_to_csv",
    "input_file": "data_sync_20251009_174500.json"
})

# Returns:
{
    "success": True,
    "csv_files": [
        "data_sync_20251009_174500_blockchain.csv",
        "data_sync_20251009_174500_dex.csv",
        "data_sync_20251009_174500_oracle.csv"
    ],
    "count": 3
}
```

### 6. Upload to GCS

**Upload specific files**

```python
upload = await bee_manager.execute_bee("data_pipeline", {
    "type": "upload_to_gcs",
    "files": [
        "data_sync_20251009_174500_blockchain.csv",
        "data_sync_20251009_174500_dex.csv"
    ]
})

# Returns:
{
    "success": True,
    "uploaded_files": [
        {
            "file": "data_sync_20251009_174500_blockchain.csv",
            "gcs_path": "gs://omk-hive-blockchain-data/blockchain_data/...",
            "size_bytes": 1024
        }
    ],
    "count": 2,
    "bucket": "omk-hive-blockchain-data"
}
```

---

## Integration with Queen AI

DataPipelineBee can be scheduled by Queen AI's background loop:

```python
# In Queen AI's main loop
async def background_data_pipeline():
    """Run data pipeline every 15 minutes"""
    while True:
        try:
            result = await bee_manager.execute_bee("data_pipeline", {
                "type": "run_pipeline"
            })
            
            if result.get("success"):
                logger.info(
                    "Data pipeline completed",
                    records=result.get("total_records"),
                    duration=result.get("duration_seconds")
                )
            else:
                logger.error(
                    "Data pipeline failed",
                    error=result.get("error")
                )
        
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
        
        # Wait 15 minutes
        await asyncio.sleep(900)
```

---

## Data Flow

### Input: Blockchain Connectors

DataPipelineBee uses existing data collectors:
- `BlockchainTransactionsConnector` → Ethereum & Solana transactions
- `DEXPoolsConnector` → Uniswap, Raydium pools
- `PriceOraclesConnector` → Chainlink, Pyth price feeds

### Output: CSV Files

**blockchain_transactions.csv**
```csv
timestamp,table,transaction_hash,block_number,from_address,to_address,value,gas_price,status
2025-10-09T17:45:00Z,ethereum_transactions,0xabc...,18500000,0x123...,0x456...,1.5,30,success
```

**dex_pools.csv**
```csv
timestamp,table,pool_address,dex,token_a,token_b,liquidity_usd,volume_24h,reserve_a,reserve_b
2025-10-09T17:45:00Z,dex_pools,0xpool...,uniswap,ETH,USDC,5000000,500000,2500,2500000
```

**price_feeds.csv**
```csv
timestamp,table,oracle,pair,price,confidence,feed_address
2025-10-09T17:45:00Z,chainlink_prices,chainlink,ETH/USD,2450.50,99.9,0xfeed...
```

### Destination: BigQuery Tables

Fivetran automatically syncs CSV files to these BigQuery tables:
- `omk_hive_brain.blockchain_transactions`
- `omk_hive_brain.dex_pools`
- `omk_hive_brain.price_feeds`

---

## Error Handling

DataPipelineBee tracks errors and retries:

```python
{
    "success": False,
    "error": "GCS upload failed: Connection timeout",
    "pipeline_run": 5,
    "started_at": "2025-10-09T17:45:00Z"
}
```

**Error Recovery**:
- Logs all errors to Elastic Search
- Tracks error count in status
- Continues with next scheduled run
- Alerts Queen AI if error_count > threshold

---

## Monitoring

### Check Pipeline Health

```python
status = await bee_manager.execute_bee("data_pipeline", {
    "type": "get_pipeline_status"
})

# Monitor these metrics:
run_count = status["status"]["run_count"]
error_count = status["status"]["error_count"]
success_rate = (run_count - error_count) / run_count * 100

if success_rate < 95:
    alert_queen_ai("Data pipeline unhealthy!")
```

### Activity Logging

All pipeline runs are logged to Elastic Search:
- Activity type: `data_pipeline_run`
- Status: success/failure
- Duration, records, files uploaded
- Error messages (if failed)

Query via DataBee:
```python
activities = await bee_manager.execute_bee("data", {
    "type": "search_activities",
    "bee_name": "DataPipelineBee",
    "limit": 10
})
```

---

## Configuration

Set via environment variables:

```bash
# GCS Configuration
GCS_BUCKET=omk-hive-blockchain-data
GCS_PREFIX=blockchain_data/
GCP_PROJECT_ID=omk-hive-prod

# Pipeline Schedule (optional)
DATA_PIPELINE_INTERVAL_MINUTES=15
```

---

## Testing

Run the test script:

```bash
cd backend/queen-ai
python3 test_data_pipeline_bee.py
```

Expected output:
```
✅ DataPipelineBee initialized
✅ Pipeline completed in 12.5s
✅ Total records: 18
✅ CSV files uploaded: 3
✅ Scheduled to run every 15 minutes
```

---

## Benefits

### Before (Manual)
```bash
# Every 15 minutes, you had to run:
python3 sync_to_gcs.py          # Step 1
python3 convert_to_csv.py       # Step 2
python3 upload_to_gcs.py *.csv  # Step 3
```

### After (Automated)
```python
# One-time setup:
await bee_manager.execute_bee("data_pipeline", {
    "type": "schedule_pipeline",
    "interval_minutes": 15
})

# That's it! Runs automatically forever.
```

---

## Roadmap

**Future Enhancements**:
1. **Fivetran API Integration** - Check sync status, trigger manual syncs
2. **Data Quality Checks** - Validate data before upload
3. **Alerting** - Notify Queen AI of pipeline failures
4. **Dynamic Scheduling** - Adjust frequency based on blockchain activity
5. **Incremental Syncs** - Only upload new/changed data

---

## Summary

**DataPipelineBee** eliminates manual data collection by automating:
- ✅ Data collection from blockchain
- ✅ Format conversion to CSV
- ✅ Upload to GCS
- ✅ Monitoring and error handling
- ✅ Integration with Fivetran & BigQuery

**Set it and forget it!** 🐝📊✨

The bee runs every 15 minutes, keeping your data fresh and queryable via DataBee.
