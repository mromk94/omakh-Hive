# 🔐 ENVIRONMENT VARIABLES CONFIGURATION GUIDE

**Last Updated:** October 13, 2025

---

## 📂 `.env` FILE LOCATIONS

Your project has **3** different `.env` files for different components:

### **1. Backend Queen AI** ⭐ **MAIN CONFIG**
```
📁 /Users/mac/CascadeProjects/omakh-Hive/backend/queen-ai/.env
```

**Purpose:** Queen AI backend configuration (FastAPI server)  
**Port:** 8001

**Required Variables:**
```bash
# === DATABASE ===
DATABASE_URL=mysql+pymysql://user:pass@localhost/omk_hive

# === REDIS ===
REDIS_URL=redis://localhost:6379/0
MESSAGE_BUS_TYPE=redis  # or 'memory' for fallback

# === ELASTICSEARCH === ⚠️ YOU NEED TO ADD THESE
ELASTIC_CLOUD_ID=your_cloud_id_here
ELASTIC_API_KEY=your_api_key_here

# === BIGQUERY ===
GCP_PROJECT_ID=omk-hive-prod
BIGQUERY_PROJECT_ID=omk-hive-prod
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# === LLM PROVIDERS ===
GEMINI_API_KEY=your_gemini_key
ANTHROPIC_API_KEY=your_claude_key
OPENAI_API_KEY=your_openai_key
XAI_API_KEY=your_grok_key

# === BLOCKCHAIN ===
ETHEREUM_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/your_key
SOLANA_RPC_URL=https://api.devnet.solana.com
PRIVATE_KEY=your_private_key_for_deploying_contracts

# === FIVETRAN ===
FIVETRAN_API_KEY=your_fivetran_api_key
FIVETRAN_API_SECRET=your_fivetran_secret

# === SECURITY ===
JWT_SECRET=your_super_secret_jwt_key
ADMIN_PASSWORD=your_admin_password

# === MISC ===
ENVIRONMENT=development  # or 'production'
DEBUG=true
LOG_LEVEL=INFO
```

---

### **2. Smart Contracts (Ethereum)**
```
📁 /Users/mac/CascadeProjects/omakh-Hive/contracts/ethereum/.env
```

**Purpose:** Hardhat deployment configuration  
**Port:** N/A (deployment only)

**Required Variables:**
```bash
# === ETHEREUM DEPLOYMENT ===
SEPOLIA_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/your_key
PRIVATE_KEY=your_deployer_private_key
ETHERSCAN_API_KEY=your_etherscan_key_for_verification

# === CONTRACT ADDRESSES (auto-populated after deployment) ===
OMK_TOKEN_ADDRESS=0x...
OMK_BRIDGE_ADDRESS=0x...
PROPERTY_NFT_ADDRESS=0x...
```

---

### **3. Smart Contracts (Solana)** 
```
📁 /Users/mac/CascadeProjects/omakh-Hive/contracts/solana/.env
```

**Purpose:** Anchor deployment configuration  
**Port:** N/A (deployment only)

**Required Variables:**
```bash
# === SOLANA DEPLOYMENT ===
ANCHOR_PROVIDER_URL=https://api.devnet.solana.com
ANCHOR_WALLET=~/.config/solana/id.json

# === PROGRAM IDs (auto-populated after deployment) ===
OMK_PROGRAM_ID=...
BRIDGE_PROGRAM_ID=...
```

---

## 🎯 **FOR YOUR CURRENT ERRORS**

### **Error 1: Elastic Search not configured**

**Edit this file:**
```
/Users/mac/CascadeProjects/omakh-Hive/backend/queen-ai/.env
```

**Add these lines:**
```bash
ELASTIC_CLOUD_ID=your_elastic_cloud_id_from_elastic.co
ELASTIC_API_KEY=your_api_key_from_elastic.co
```

**How to get these values:**
1. Go to https://cloud.elastic.co/
2. Log in to your account
3. Go to your deployment → "Cloud ID" (copy this)
4. Go to "API Keys" → Create API key → Copy the key

**Example:**
```bash
ELASTIC_CLOUD_ID=omk-hive:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvJGFiYzEyMw==
ELASTIC_API_KEY=VnVhQ2ZHY0JDZGJrUW0tZTVoT3o6dWkybHBfUVJSeml0UTZ3LXRaY1w==
```

---

### **Error 2: BigQuery SQL Syntax Error**

The SQL error `Unexpected identifier "eth"` is already fixed in the code.

**The issue was:**
```sql
-- ❌ WRONG (missing backticks and dataset)
SELECT * FROM ethereum_transactions
```

**Fixed to:**
```sql
-- ✅ CORRECT (fully qualified table name)
SELECT * FROM `omk-hive-prod.fivetran_blockchain_data.ethereum_transactions`
```

---

### **Error 3: Data collectors missing**

✅ **FIXED** - Created all data collector modules:
- `app/integrations/data_collectors/blockchain_transactions.py`
- `app/integrations/data_collectors/dex_pools.py`
- `app/integrations/data_collectors/price_oracles.py`

---

## 🔄 **HOW TO APPLY CHANGES**

After editing `.env` files:

1. **Stop the backend**
   ```bash
   # Press Ctrl+C in the terminal running the backend
   ```

2. **Restart the backend**
   ```bash
   cd /Users/mac/CascadeProjects/omakh-Hive/backend/queen-ai
   python3 start.py --component queen
   ```

3. **Verify configuration**
   ```bash
   python3 check_env.py
   ```

---

## ✅ **QUICK CHECKLIST**

Before starting the system, verify:

- [ ] `/backend/queen-ai/.env` exists and has all required keys
- [ ] `ELASTIC_CLOUD_ID` is set (for Elastic Search to work)
- [ ] `ELASTIC_API_KEY` is set (for Elastic Search to work)
- [ ] `GEMINI_API_KEY` is set (for LLM to work)
- [ ] `GCP_PROJECT_ID=omk-hive-prod` (for BigQuery)
- [ ] `DATABASE_URL` points to valid MySQL database
- [ ] `REDIS_URL` points to Redis server (or use `MESSAGE_BUS_TYPE=memory`)

---

## 🚨 **SECURITY WARNING**

**NEVER commit `.env` files to Git!**

All `.env` files are in `.gitignore`. If you accidentally commit secrets:
1. Rotate all API keys immediately
2. Remove from Git history: `git filter-branch`
3. Force push: `git push --force`

---

## 📝 **EXAMPLE `.env` TEMPLATE**

Create a file `/backend/queen-ai/.env.example` (safe to commit):

```bash
# Copy this file to .env and fill in your actual values
DATABASE_URL=mysql+pymysql://user:pass@localhost/omk_hive
REDIS_URL=redis://localhost:6379/0
ELASTIC_CLOUD_ID=your_cloud_id_here
ELASTIC_API_KEY=your_api_key_here
GEMINI_API_KEY=your_gemini_key
# ... etc
```

---

## 💡 **TIP: Use Environment Manager**

For easier management, use:

```bash
cd /Users/mac/CascadeProjects/omakh-Hive/backend/queen-ai
python3 manage.py config --show
```

This shows all current configuration values (without revealing secrets).

---

## ✅ **ALL SET!**

After configuring the `.env` file in `/backend/queen-ai/`, restart the backend and all services should work!
