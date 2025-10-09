# Integration Tests - Real System Testing

These tests connect to **REAL external systems** and may incur costs or require setup.

---

## 🎯 Purpose

Integration tests verify that the hive works with actual:
- Ethereum/Polygon blockchains (testnet)
- LLM APIs (Gemini, OpenAI, Anthropic)
- PostgreSQL database
- Redis message queue
- External price feeds and oracles

**Unit tests** verify logic. **Integration tests** verify real-world connectivity.

---

## 📋 Available Tests

| Test File | What It Tests | Requirements |
|-----------|---------------|--------------|
| `test_blockchain_integration.py` | Ethereum RPC, pool queries, gas estimation | Infura/Alchemy API key |
| `test_llm_integration.py` | LLM API calls, cost tracking | Gemini/OpenAI API key |
| `test_database_integration.py` | PostgreSQL persistence | PostgreSQL server |
| `test_redis_integration.py` | Redis message queue | Redis server |

---

## ⚙️ Setup Instructions

### 1. Blockchain Tests

**Get RPC API Key:**
- Infura: https://infura.io (Free tier available)
- Alchemy: https://alchemy.com (Free tier available)

**Configure `.env`:**
```bash
ETHEREUM_RPC_URL=https://goerli.infura.io/v3/YOUR_KEY
```

**Get Testnet ETH (if testing transactions):**
- Goerli: https://goerlifaucet.com
- Mumbai (Polygon): https://mumbaifaucet.com

**Run:**
```bash
python3 integration_tests/test_blockchain_integration.py
```

---

### 2. LLM Tests

⚠️ **WARNING**: Makes real API calls! May incur costs.

**Get API Keys:**
- Gemini (FREE): https://makersuite.google.com/app/apikey
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/settings/keys

**Configure `.env`:**
```bash
GEMINI_API_KEY=your_gemini_key_here
# Optional:
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

**Run:**
```bash
python3 integration_tests/test_llm_integration.py
```

**Expected Cost:**
- Gemini: ~$0.001 per test run (very cheap!)
- OpenAI: ~$0.01-0.05 per test run
- Anthropic: ~$0.005-0.02 per test run

---

### 3. Database Tests

**Install PostgreSQL:**
```bash
# macOS
brew install postgresql
brew services start postgresql

# Ubuntu
sudo apt install postgresql
sudo service postgresql start
```

**Create Test Database:**
```bash
createdb omk_hive_test
```

**Configure `.env`:**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/omk_hive_test
```

**Run:**
```bash
python3 integration_tests/test_database_integration.py
```

---

### 4. Redis Tests

**Install Redis:**
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu
sudo apt install redis
sudo service redis-server start
```

**Configure `.env`:**
```bash
REDIS_URL=redis://localhost:6379/0
```

**Run:**
```bash
python3 integration_tests/test_redis_integration.py
```

---

## 🚀 Running All Integration Tests

```bash
# Run all tests at once
cd backend/queen-ai
python3 -m pytest integration_tests/ -v

# Or run individually
python3 integration_tests/test_blockchain_integration.py
python3 integration_tests/test_llm_integration.py
```

---

## 📊 Expected Results

### Blockchain Tests
```
✅ Web3 connection established
✅ Balance query successful
✅ ERC20 balance query successful
✅ Pool reserves query successful
✅ Gas price query successful
✅ Transaction simulation successful

Success Rate: 100%
```

### LLM Tests
```
✅ Gemini provider initialized
✅ Text generation successful
✅ Pool analysis generated
✅ Decision making successful
✅ Provider switching
✅ Conversation memory working
✅ Cost tracking functional

Total API Cost: $0.001234
Success Rate: 100%
```

---

## ⚠️ Important Notes

### Costs
- **Blockchain queries**: FREE (read-only)
- **Blockchain transactions**: Costs testnet gas (FREE)
- **LLM API calls**: ~$0.001-0.05 per test run
- **Database**: FREE (local)
- **Redis**: FREE (local)

### Rate Limits
- Infura Free: 100,000 requests/day
- Gemini Free: 15 requests/minute, 1500/day
- OpenAI: Depends on tier
- Anthropic: Depends on tier

### Security
- **NEVER commit `.env` file**
- **Use testnet only** for transaction tests
- **Monitor API costs** regularly
- **Rotate keys** periodically

---

## 🔍 Troubleshooting

### "Web3 connection failed"
- Check `ETHEREUM_RPC_URL` in `.env`
- Verify API key is valid
- Check internet connection

### "LLM generation failed"
- Check API key in `.env`
- Verify you're not rate-limited
- Check API key has credits/quota

### "Database connection failed"
- Ensure PostgreSQL is running: `pg_isready`
- Check DATABASE_URL format
- Verify database exists: `psql -l`

### "Redis connection failed"
- Check Redis is running: `redis-cli ping`
- Should return `PONG`
- Check REDIS_URL in `.env`

---

## 📝 Adding New Integration Tests

1. Create new test file in `integration_tests/`
2. Follow naming convention: `test_*_integration.py`
3. Include requirements in docstring
4. Add to this README
5. Test with real systems before committing

---

## ✅ CI/CD Integration

These tests should **NOT** run in CI/CD by default (they need external services).

**Option 1**: Run in separate CI job with secrets
**Option 2**: Run manually before releases
**Option 3**: Run in scheduled nightly builds

---

**Last Updated**: October 9, 2025  
**Status**: Ready for use
