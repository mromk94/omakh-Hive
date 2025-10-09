# 🚀 OMK HIVE - DEPLOYMENT GUIDE

**Elastic Search & Data Pipeline Integration**

## Prerequisites Installed ✅
- elasticsearch==8.11.0
- google-cloud-bigquery==3.14.1  
- google-cloud-aiplatform==1.40.0

---

## 🔍 ELASTIC SEARCH DEPLOYMENT

### 1. Sign Up for Elastic Cloud
```bash
# Visit: https://cloud.elastic.co/registration
# Get 14-day free trial
```

### 2. Create Deployment
1. Click "Create deployment"
2. Select region (closest to you)
3. Choose "Elasticsearch" template
4. Copy **Cloud ID** and **API Key**

### 3. Set Environment Variables
```bash
# Add to backend/queen-ai/.env
ELASTIC_CLOUD_ID=your_cloud_id_from_step_2
ELASTIC_API_KEY=your_api_key_from_step_2
ELASTIC_ENABLED=true
```

### 4. Initialize Indices
```bash
cd backend/queen-ai
python3 -c "
import asyncio
from app.integrations.elastic_search import ElasticSearchIntegration
import os

async def init():
    elastic = ElasticSearchIntegration()
    await elastic.initialize()
    print('✅ Elastic indices created!')

asyncio.run(init())
"
```

### 5. Test Search
```python
# Test conversational search
result = await elastic.conversational_search(
    'Show me recent blockchain bee activities'
)
print(result)
```

---

## 📊 FIVETRAN + BIGQUERY DEPLOYMENT

### 1. Set Up Google Cloud Project
```bash
# Create project: https://console.cloud.google.com/
# Enable BigQuery API
# Create dataset: omk_hive_blockchain_data
```

### 2. Sign Up for Fivetran
```bash
# Visit: https://fivetran.com/signup
# Use Google SSO for easy setup
```

### 3. Configure Connectors

#### A. Blockchain Connector
1. Fivetran Dashboard → "Add Connector"
2. Select "Custom Connector (Python)"
3. Upload `backend/fivetran_connectors/blockchain_connector.py`
4. Configure:
   - **ethereum_rpc_url**: Your Infura/Alchemy URL
   - **solana_rpc_url**: https://api.mainnet-beta.solana.com
5. Destination: BigQuery → `omk_hive_blockchain_data`
6. Sync frequency: Every 15 minutes
7. Click "Save & Test"

#### B. DEX Pools Connector
Same process with `dex_pools_connector.py`

#### C. Price Oracle Connector  
Same process with `price_oracle_connector.py`

### 4. Verify Data Flow
```sql
-- In BigQuery console
SELECT COUNT(*) FROM `omk_hive_blockchain_data.ethereum_transactions`;
SELECT COUNT(*) FROM `omk_hive_blockchain_data.dex_pools`;
SELECT COUNT(*) FROM `omk_hive_blockchain_data.chainlink_prices`;
```

---

## ✅ VERIFICATION CHECKLIST

- [ ] Elastic Cloud deployment created
- [ ] API credentials set in .env
- [ ] Indices initialized (3 indices)
- [ ] BigQuery dataset created
- [ ] Fivetran account created
- [ ] 3 connectors deployed
- [ ] Data syncing to BigQuery
- [ ] Queen AI can query both systems

---

## 🎬 QUICK START

```bash
# 1. Set credentials
cp backend/queen-ai/.env.example backend/queen-ai/.env
# Edit .env with your keys

# 2. Initialize Elastic
cd backend/queen-ai
python3 -c "from app.integrations import ElasticSearchIntegration; import asyncio; asyncio.run(ElasticSearchIntegration().initialize())"

# 3. Start Queen AI
python3 main.py
```

**Status**: Ready for production deployment! 🚀
