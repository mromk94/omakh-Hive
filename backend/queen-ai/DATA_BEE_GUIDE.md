# 🐝 DataBee - Enterprise Data Operations

**Unified data access layer for Queen AI and the Hive**

## Overview

DataBee provides seamless integration with:
- **Elastic Search**: Real-time activity logs & RAG-powered search
- **BigQuery**: Historical blockchain data analytics
- **Local cache**: Performance optimization

---

## Capabilities

### 1. Elastic Search Operations

**Search Bee Activities**
```python
result = await bee_manager.execute_bee("data", {
    "type": "search_activities",
    "query": "liquidity operations",
    "bee_name": "liquidity_sentinel",  # Optional filter
    "limit": 10
})
```

**Conversational Query (RAG)**
```python
result = await bee_manager.execute_bee("data", {
    "type": "conversational_query",
    "question": "Why did the last transaction fail?"
})
# Returns AI-generated answer with context
```

**Get Bee Statistics**
```python
result = await bee_manager.execute_bee("data", {
    "type": "get_bee_stats",
    "bee_name": "blockchain",
    "time_range": "24h"
})
# Returns: success_rate, action_breakdown, total_activities
```

---

### 2. BigQuery Operations

**Query Blockchain Transactions**
```python
result = await bee_manager.execute_bee("data", {
    "type": "query_transactions",
    "chain": "ethereum",  # or "solana"
    "address": "0x123...",  # Optional filter
    "limit": 100
})
```

**Query DEX Pools**
```python
result = await bee_manager.execute_bee("data", {
    "type": "query_dex_pools",
    "dex": "uniswap",  # or "raydium"
    "limit": 50
})
```

**Query Price Oracles**
```python
result = await bee_manager.execute_bee("data", {
    "type": "query_prices",
    "pair": "ETH/USD",
    "oracle": "chainlink",  # or "pyth"
    "limit": 100
})
# Returns: current_price, avg_price, min/max, price_history
```

**Get Blockchain Statistics**
```python
result = await bee_manager.execute_bee("data", {
    "type": "get_blockchain_stats",
    "time_range": "24h"
})
# Returns: transaction counts, gas prices, TVL, etc.
```

---

### 3. Analytics & Reporting

**Aggregate Data**
```python
result = await bee_manager.execute_bee("data", {
    "type": "aggregate_data",
    "metric": "platform_health",
    "time_range": "24h"
})
# Combines Elastic + BigQuery data
```

**Generate Insights (AI-Powered)**
```python
result = await bee_manager.execute_bee("data", {
    "type": "generate_insights",
    "topic": "liquidity management"
})
# Returns RAG-generated insights
```

**Create Report**
```python
result = await bee_manager.execute_bee("data", {
    "type": "create_report",
    "report_type": "daily"  # or "weekly", "monthly"
})
# Returns comprehensive platform report with recommendations
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│           Queen AI                      │
│                                         │
│  "Show me liquidity pool performance"   │
└───────────────┬─────────────────────────┘
                │
                ▼
        ┌───────────────┐
        │   DataBee     │
        └───┬───────┬───┘
            │       │
  ┌─────────┘       └──────────┐
  │                            │
  ▼                            ▼
┌────────────────┐    ┌──────────────────┐
│ Elastic Search │    │    BigQuery      │
│                │    │                  │
│ • Bee logs     │    │ • Transactions   │
│ • RAG/Search   │    │ • DEX pools      │
│ • Real-time    │    │ • Price oracles  │
└────────────────┘    └──────────────────┘
```

---

## Data Sources

### Elastic Search Indices

1. **omk_hive_bee_activities**
   - All bee actions logged automatically
   - Searchable with hybrid search (vector + keyword)
   - Enables conversational queries

2. **omk_hive_knowledge_base**
   - Platform documentation
   - Best practices
   - Historical insights

3. **omk_hive_transactions**
   - Critical transaction logs
   - Cross-referenced with blockchain data

### BigQuery Tables

1. **ethereum_transactions**
   - Transaction hash, from/to addresses
   - Gas prices, block timestamps
   - Value transfers

2. **solana_transactions**
   - Signature, slot, block time
   - Signer, fee, status

3. **dex_pools**
   - Pool addresses, liquidity
   - Token reserves, prices
   - 24h volume

4. **chainlink_prices** / **pyth_prices**
   - Price pairs (ETH/USD, BTC/USD, etc.)
   - Timestamps, confidence intervals
   - Historical price data

---

## Example Workflows

### Workflow 1: Investigate Failed Transaction

```python
# 1. Ask conversational question
answer = await bee_manager.execute_bee("data", {
    "type": "conversational_query",
    "question": "Why did transaction 0xabc... fail?"
})

# 2. Get transaction details from BigQuery
tx_details = await bee_manager.execute_bee("data", {
    "type": "query_transactions",
    "chain": "ethereum",
    "limit": 1
})

# 3. Check related bee activities
activities = await bee_manager.execute_bee("data", {
    "type": "search_activities",
    "query": "transaction execution",
    "bee_name": "blockchain"
})
```

### Workflow 2: Platform Health Report

```python
# Generate daily report
report = await bee_manager.execute_bee("data", {
    "type": "create_report",
    "report_type": "daily"
})

# Report includes:
# - Bee activity stats
# - Blockchain metrics
# - TVL and volume
# - Price data
# - AI-generated recommendations
```

### Workflow 3: Price Analysis

```python
# Get ETH price history
prices = await bee_manager.execute_bee("data", {
    "type": "query_prices",
    "pair": "ETH/USD",
    "oracle": "chainlink",
    "limit": 24  # Last 24 hours
})

# Generate insights
insights = await bee_manager.execute_bee("data", {
    "type": "generate_insights",
    "topic": "ETH price trends"
})
```

---

## Configuration

DataBee automatically configures from environment variables:

```bash
# BigQuery
GCP_PROJECT_ID=omk-hive-prod
BIGQUERY_DATASET=omk_hive_brain

# Elastic Search (set by BeeManager)
ELASTIC_CLOUD_ID=your_cloud_id
ELASTIC_API_KEY=your_api_key
```

---

## Performance

- **Caching**: 5-minute TTL for frequently accessed data
- **Query Optimization**: Indexed searches in Elastic
- **BigQuery**: Optimized queries with date partitioning
- **Async**: All operations are non-blocking

---

## Integration with Other Bees

DataBee can be queried by:
- **Queen AI**: Natural language queries
- **LogicBee**: Data-driven decisions
- **PatternBee**: ML model training data
- **MathsBee**: Statistical analysis
- **LiquiditySentinelBee**: Pool performance tracking

---

## Status

✅ **Production Ready**
- Elastic Search: Connected & logging
- BigQuery: Ready for data sync
- Cache: Active
- RAG: Powered by Gemini

---

## Next Steps

1. **Unpause Fivetran** to start BigQuery data sync
2. **Query real data** once Fivetran syncs
3. **Generate reports** for platform insights
4. **Enable Queen AI** conversational data access

**DataBee transforms raw data into actionable intelligence for the Queen and Hive!** 🐝📊
