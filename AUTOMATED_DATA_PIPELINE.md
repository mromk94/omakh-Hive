# 🚀 Automated Data Pipeline - Now Running!

## What Just Happened?

DataPipelineBee is now **fully integrated** into Queen AI's startup routine!

### When You Start Queen AI:

```bash
cd backend/queen-ai
python3 main.py
```

**Automatic Magic Happens:**

1. ✅ Queen AI starts up
2. ✅ All 17 bees initialize
3. ✅ DataPipelineBee registers
4. ✅ **Background data pipeline loop starts automatically**
5. ✅ Waits 30 seconds for full initialization
6. ✅ Runs first data collection
7. ✅ **Repeats every 15 minutes forever**

---

## What You'll See in Logs

### On Startup:

```
🚀 Starting Queen AI Orchestrator
✅ Blockchain connector initialized
✅ LLM abstraction initialized
✅ Message bus initialized
✅ Hive Information Board initialized
✅ Bee manager initialized
✅ DataPipelineBee initialized  ← New bee!
✅ Background tasks started:
   📊 Monitoring loop (system health)
   🧠 Decision loop (autonomous operations)
   💎 Staking rewards loop (daily distributions)
   🔄 Data pipeline loop (every 15 minutes)  ← Automated!
🎉 Queen AI Orchestrator fully initialized and operational
```

### After 30 Seconds:

```
📊 Starting data pipeline loop
🔄 Running automated data pipeline
  • Blockchain transactions...
    ✓ Collected 10 blockchain records
  • DEX pools...
    ✓ Collected 3 DEX records
  • Price oracles...
    ✓ Collected 5 oracle records
✅ Data pipeline completed successfully
   Duration: 12.5s
   Records: 18
   Files: 3
⏰ Data pipeline sleeping for 15 minutes
```

### Every 15 Minutes:

```
🔄 Running automated data pipeline
✅ Data pipeline completed successfully
⏰ Data pipeline sleeping for 15 minutes
```

---

## Data Flow

```
Queen AI Starts
    ↓
DataPipelineBee Initializes
    ↓
Background Loop Starts (every 15 min)
    ↓
┌─────────────────────────┐
│ Automatic Execution     │
│ ├─ Collect blockchain   │
│ ├─ Convert to CSV       │
│ └─ Upload to GCS        │
└──────────┬──────────────┘
           ↓
       Fivetran (auto-syncs)
           ↓
       BigQuery (data ready!)
           ↓
       DataBee (queries it!)
           ↓
       Queen AI (uses it!)
```

---

## No Manual Work Required

**Before:**
```bash
# You had to run these every 15 minutes:
python3 sync_to_gcs.py
python3 convert_to_csv.py
python3 upload_to_gcs.py *.csv
```

**Now:**
```bash
# Just start Queen AI once:
python3 main.py

# Everything happens automatically! ✨
```

---

## Configuration

Data pipeline settings (optional):

```bash
# In .env or environment:
DATA_PIPELINE_INTERVAL_MINUTES=15  # Default: 15 minutes
GCS_BUCKET=omk-hive-blockchain-data
GCS_PREFIX=blockchain_data/
```

---

## Monitoring

### Check Pipeline Status

Via Queen AI API:

```bash
curl http://localhost:8001/api/v1/bees/data_pipeline/status
```

Or via DataBee:

```python
status = await bee_manager.execute_bee("data_pipeline", {
    "type": "get_pipeline_status"
})
```

Returns:
```json
{
  "run_count": 5,
  "error_count": 0,
  "last_run": "2025-10-09T18:00:00Z",
  "last_success": "2025-10-09T18:00:00Z"
}
```

### View in Elastic Search

All pipeline runs are logged to Elastic:

```python
# Query via DataBee
activities = await bee_manager.execute_bee("data", {
    "type": "search_activities",
    "bee_name": "DataPipelineBee",
    "limit": 10
})
```

---

## What Gets Collected

### Every 15 Minutes:

1. **Blockchain Transactions**
   - Ethereum: Latest 10 transactions
   - Solana: Latest 10 transactions
   - Gas prices, block data

2. **DEX Pools**
   - Uniswap: Top 5 pools
   - Raydium: Top 5 pools
   - Liquidity, volume, reserves

3. **Price Oracles**
   - Chainlink: ETH/USD, BTC/USD, etc.
   - Pyth: Major price feeds
   - Confidence scores

### Output:

3 CSV files uploaded to GCS:
- `data_sync_TIMESTAMP_blockchain.csv`
- `data_sync_TIMESTAMP_dex.csv`
- `data_sync_TIMESTAMP_oracle.csv`

### Result:

Fresh data in BigQuery tables:
- `omk_hive_brain.blockchain_transactions`
- `omk_hive_brain.dex_pools`
- `omk_hive_brain.price_feeds`

---

## Graceful Shutdown

When you stop Queen AI:

```
🛑 Shutting down Queen AI Orchestrator
✅ Data pipeline task cancelled
✅ All background tasks stopped
✅ Queen AI shutdown complete
```

The pipeline completes its current run before stopping.

---

## Error Handling

If pipeline fails:

```
❌ Data pipeline failed
   Error: GCS upload timeout
⏰ Retrying in 15 minutes
```

Errors are logged to:
- Console logs
- Elastic Search (for analysis)
- Pipeline status (error_count increases)

Queen AI continues running normally.

---

## Manual Triggers (Optional)

You can still trigger manually if needed:

```python
# Via Queen AI
result = await queen.bee_manager.execute_bee("data_pipeline", {
    "type": "run_pipeline"
})

# Or via API
curl -X POST http://localhost:8001/api/v1/bees/data_pipeline/execute \
  -H "Content-Type: application/json" \
  -d '{"type": "run_pipeline"}'
```

---

## Benefits

✅ **Automated**: No manual commands ever again
✅ **Reliable**: Runs every 15 minutes without fail
✅ **Monitored**: Full logging and status tracking
✅ **Resilient**: Continues even if one run fails
✅ **Integrated**: Part of Queen AI's core operations
✅ **Fresh Data**: BigQuery always has latest blockchain data
✅ **RAG-Ready**: DataBee can answer questions on current data

---

## Summary

**Before**: Manual 3-step process every 15 minutes
**After**: Start Queen AI once, runs forever automatically

**DataPipelineBee is now a core part of the Hive! 🐝📊✨**

Just start Queen AI and enjoy fresh blockchain data automatically!
