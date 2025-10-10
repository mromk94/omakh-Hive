# 🚀# 👑 OMK Hive - Quick Start Guide

## 🚀 **ONE-COMMAND STARTUP**

Start everything (Queen AI + Frontend) with one command:

## Prerequisites
- ✅ Elastic Search configured (already done)
- ✅ Fivetran GCS connector set up (already done)
- ✅ Google Cloud authentication
---

## Step 1: Authenticate with Google Cloud

```bash
gcloud auth application-default login
```

---

## Step 2: Collect Blockchain Data

```bash
python3 sync_to_gcs.py
```

This collects:
- Ethereum & Solana transactions
- DEX pool data (Uniswap)
- Price oracle feeds (Chainlink/Pyth)

Output: `data_sync_YYYYMMDD_HHMMSS.json`

---

## Step 3: Upload to GCS

```bash
python3 upload_to_gcs.py data_sync_*.json
```

This uploads to: `gs://omk-hive-blockchain-data/blockchain_data/`

---

## Step 4: Unpause Fivetran

1. Go to: https://fivetran.com/dashboard/connectors/ballad_monde
2. Click **"Resume Connector"**
3. Fivetran will automatically sync GCS → BigQuery every 15 minutes

---

## Step 5: Start Queen AI

```bash
cd backend/queen-ai
python3 main.py
```

All bee activities are automatically logged to Elastic Search!

---

## Verification

**Check Elastic:**
```bash
cd backend/queen-ai
python3 test_elastic_connection.py
```

**Check BigQuery:**
Go to: https://console.cloud.google.com/bigquery
- Look for dataset: `omk_hive_brain.hive_mind`
- Tables should appear after first Fivetran sync

---

## Automation (Optional)

Schedule data collection every 15 minutes:

```bash
# Add to crontab
crontab -e

# Add this line:
*/15 * * * * cd /path/to/omakh-Hive && python3 sync_to_gcs.py && python3 upload_to_gcs.py data_sync_*.json
```

---

## Support

**Elastic Search**: All bee activities logged automatically
**Data Pipeline**: GCS → Fivetran → BigQuery
**Queen AI**: Conversational search + RAG with Gemini

**Status**: ✅ Production Ready
