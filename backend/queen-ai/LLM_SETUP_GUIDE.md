# LLM SETUP GUIDE - OMK HIVE
**Complete guide to setting up AI intelligence for Queen and Bees**

---

## 🧠 LLM INTEGRATION OVERVIEW

The OMK Hive uses LLM (Large Language Models) to power:
1. **Queen AI** - Intelligent orchestration and decision-making
2. **LogicBee** - Complex multi-criteria decisions
3. **PatternBee** - Advanced market analysis and predictions
4. **GovernanceBee** - DAO proposal analysis and voting recommendations
5. **SecurityBee** - Threat analysis and risk assessment

---

## 🎯 QUICK START (Gemini - Recommended)

### Step 1: Get Gemini API Key (FREE)
1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### Step 2: Configure Environment
```bash
cd backend/queen-ai
cp .env.example .env
```

Edit `.env`:
```bash
# Set Gemini as default (best cost/performance)
DEFAULT_LLM_PROVIDER=gemini
GEMINI_API_KEY=your_actual_api_key_here
```

###  Step 3: Verify Setup
```bash
# Test LLM connection
python3 -c "
import asyncio
from app.llm.abstraction import LLMAbstraction

async def test():
    llm = LLMAbstraction()
    await llm.initialize()
    response = await llm.generate('Say hello!')
    print(f'LLM Response: {response}')

asyncio.run(test())
"
```

✅ **You're ready!** The Queen and bees now have AI intelligence.

---

## 📊 SUPPORTED LLM PROVIDERS

### 1. **Gemini (Google AI)** - RECOMMENDED ⭐

**Why Choose Gemini:**
- ✅ **FREE tier**: 15 requests/min, 1500 requests/day
- ✅ **Cheapest**: $0.075/$0.30 per 1M tokens (input/output)
- ✅ **Fast**: Gemini 1.5 Flash is optimized for speed
- ✅ **Good quality**: Excellent for most tasks
- ✅ **Easy setup**: Just an API key

**Get API Key:**
- URL: https://makersuite.google.com/app/apikey
- Free tier limits: 15 RPM, 1500 RPD

**Configuration:**
```bash
DEFAULT_LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSy...  # Your key here
```

**Models Available:**
- `gemini-1.5-flash` (default) - Fast & cheap
- `gemini-1.5-pro` - More powerful reasoning

---

### 2. **OpenAI (GPT-4, GPT-3.5)**

**Why Choose OpenAI:**
- ✅ **Best quality**: GPT-4 is state-of-the-art
- ✅ **Reliable**: Industry standard
- ⚠️ **Expensive**: $30/$60 per 1M tokens (GPT-4)
- ⚠️ **No free tier**: Pay per use

**Get API Key:**
- URL: https://platform.openai.com/api-keys
- Need credit card for billing

**Configuration:**
```bash
DEFAULT_LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...  # Your key here
```

**Models Available:**
- `gpt-4` - Best quality, expensive
- `gpt-3.5-turbo` - Cheaper, good quality

---

### 3. **Anthropic (Claude 3.5 Sonnet)**

**Why Choose Anthropic:**
- ✅ **Excellent reasoning**: Best for complex logic
- ✅ **Long context**: 200K tokens context window
- ⚠️ **Mid-priced**: $3/$15 per 1M tokens
- ⚠️ **No free tier**: Pay per use

**Get API Key:**
- URL: https://console.anthropic.com/settings/keys
- Need credit card for billing

**Configuration:**
```bash
DEFAULT_LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...  # Your key here
```

**Models Available:**
- `claude-3-5-sonnet-20241022` - Latest & best

---

## 🔄 SWITCHING BETWEEN PROVIDERS

You can switch providers anytime:

```bash
# In .env file
DEFAULT_LLM_PROVIDER=gemini  # or openai or anthropic
```

Or programmatically:
```python
await queen.llm.switch_provider("openai")
```

**Conversation memory persists** across provider switches!

---

## 💰 COST COMPARISON

For **1 million tokens** (input/output):

| Provider | Input | Output | Total (avg) | Free Tier |
|----------|-------|--------|-------------|-----------|
| **Gemini Flash** | $0.075 | $0.30 | $0.19 | ✅ Yes |
| GPT-3.5 Turbo | $0.50 | $1.50 | $1.00 | ❌ No |
| Claude 3.5 | $3.00 | $15.00 | $9.00 | ❌ No |
| GPT-4 | $30.00 | $60.00 | $45.00 | ❌ No |

**Recommendation**: Start with **Gemini** (free + cheap), upgrade if needed.

---

## 🏗️ ARCHITECTURE

### Queen AI (LLM-Powered)
```python
class QueenOrchestrator:
    def __init__(self):
        self.llm = LLMAbstraction()  # ✅ Queen has LLM
        self.bee_manager = BeeManager(llm_abstraction=self.llm)
        self.decision_engine = DecisionEngine(self.llm)
```

**Queen uses LLM for:**
- Task routing decisions
- Proposal generation
- Risk assessment
- Strategic planning

### Bees (Selective LLM Access)

**LLM-Enabled Bees:**
- ✅ **LogicBee** - Multi-criteria decisions, consensus building
- ✅ **PatternBee** - Market analysis, predictions
- ✅ **GovernanceBee** - Proposal analysis, voting recommendations
- ✅ **SecurityBee** - Threat analysis, risk assessment

**Standard Bees (No LLM):**
- MathsBee - Pure calculations
- DataBee - Data retrieval
- BlockchainBee - Transaction execution
- Others - Specific, deterministic tasks

### How Bees Use LLM

```python
class LogicBee(BaseBee):
    def __init__(self):
        super().__init__(llm_enabled=True)  # Enable LLM
    
    async def make_decision(self, data):
        # Use LLM for reasoning
        prompt = f"Analyze this decision: {data}"
        reasoning = await self.use_llm(prompt, temperature=0.3)
        return reasoning
```

---

## 🔒 SECURITY BEST PRACTICES

### 1. **Never Commit API Keys**
```bash
# .env is in .gitignore - NEVER commit it!
git status  # Should NOT show .env
```

### 2. **Use Environment Variables**
```bash
# Production: Set in GCP Secret Manager
gcloud secrets create GEMINI_API_KEY --data-file=- < key.txt
```

### 3. **Rotate Keys Regularly**
- Gemini: Regenerate in AI Studio
- OpenAI: Rotate in API settings
- Anthropic: Create new keys periodically

### 4. **Monitor Usage**
```python
# Check costs
costs = queen.llm.costs
print(f"Total spent: ${costs['total']:.4f}")
print(f"By provider: {costs['by_provider']}")
```

---

## 🧪 TESTING LLM INTEGRATION

### Test 1: LLM Availability
```bash
cd backend/queen-ai
python3 -c "
from app.llm.abstraction import LLMAbstraction
import asyncio

async def test():
    llm = LLMAbstraction()
    await llm.initialize()
    print(f'✅ Providers: {list(llm.providers.keys())}')
    print(f'✅ Current: {llm.current_provider}')

asyncio.run(test())
"
```

### Test 2: Queen AI with LLM
```bash
python3 -c "
from app.core.orchestrator import QueenOrchestrator
import asyncio

async def test():
    queen = QueenOrchestrator()
    await queen.initialize()
    print('✅ Queen initialized with LLM')
    print(f'✅ Bees with LLM: LogicBee, PatternBee, GovernanceBee, SecurityBee')

asyncio.run(test())
"
```

### Test 3: Bee LLM Usage
```bash
python3 -c "
from app.bees.logic_bee import LogicBee
from app.llm.abstraction import LLMAbstraction
import asyncio

async def test():
    llm = LLMAbstraction()
    await llm.initialize()
    
    bee = LogicBee()
    bee.llm_enabled = True
    bee.set_llm(llm)
    
    response = await bee.use_llm('Make a decision: approve or reject?')
    print(f'✅ LogicBee LLM response: {response}')

asyncio.run(test())
"
```

---

## 🎛️ ADVANCED CONFIGURATION

### Custom Temperature per Task
```python
# Low temperature (0.1-0.3) for factual/deterministic tasks
decision = await queen.llm.generate(prompt, temperature=0.1)

# Medium temperature (0.5-0.7) for balanced responses
analysis = await queen.llm.generate(prompt, temperature=0.7)

# High temperature (0.8-1.0) for creative/exploratory tasks
creative = await queen.llm.generate(prompt, temperature=0.9)
```

### Failover Configuration
LLM abstraction automatically fails over to backup providers:

```python
# If Gemini fails, tries OpenAI, then Anthropic
try:
    response = await llm.generate(prompt)
except AllProvidersFailedError:
    # All providers down - handle gracefully
    pass
```

### Cost Tracking
```python
# Get cost breakdown
costs = queen.llm.costs
{
    "total": 0.0234,  # $0.0234 total
    "by_provider": {
        "gemini": 0.0120,
        "openai": 0.0114
    }
}
```

---

## 🚨 TROUBLESHOOTING

### Error: "GEMINI_API_KEY not configured"
**Solution**: Set API key in `.env` file
```bash
GEMINI_API_KEY=your_key_here
```

### Error: "No LLM providers configured"
**Solution**: Set at least one provider's API key
```bash
# At minimum:
GEMINI_API_KEY=...
```

### Error: "Quota exceeded"
**Solution**:
1. **Free tier limit**: Wait for reset (daily)
2. **Upgrade**: Enable billing in GCP/OpenAI
3. **Switch provider**: Use `DEFAULT_LLM_PROVIDER=openai`

### Warning: "Bees running without AI reasoning"
**Cause**: LLM not passed to BeeManager
**Solution**: Already fixed - Queen passes LLM to BeeManager

---

## 📈 PERFORMANCE OPTIMIZATION

### 1. **Cache Common Responses**
```python
# Cache frequently asked questions
response_cache = {}

def get_cached_or_generate(prompt):
    if prompt in response_cache:
        return response_cache[prompt]
    response = await llm.generate(prompt)
    response_cache[prompt] = response
    return response
```

### 2. **Batch Requests**
```python
# Instead of 10 separate calls:
for item in items:
    await llm.generate(f"Analyze: {item}")

# Do:
batch_prompt = f"Analyze these items:\n" + "\n".join(items)
await llm.generate(batch_prompt)
```

### 3. **Use Appropriate Models**
```python
# Simple tasks: Use Flash (cheap & fast)
simple = await llm.generate(prompt, provider="gemini")

# Complex reasoning: Use GPT-4 (expensive but best)
complex = await llm.generate(prompt, provider="openai")
```

---

## ✅ VERIFICATION CHECKLIST

Before deploying:

- [ ] API key set in `.env`
- [ ] `.env` NOT in git
- [ ] LLM initializes successfully
- [ ] Queen has LLM access
- [ ] LLM-enabled bees working
- [ ] Failover tested
- [ ] Cost tracking enabled
- [ ] Rate limits understood

---

## 🎉 SUCCESS CRITERIA

Your LLM integration is successful when:

1. ✅ `queen.llm.initialized == True`
2. ✅ Queen can make intelligent decisions
3. ✅ LogicBee, PatternBee, GovernanceBee, SecurityBee have LLM access
4. ✅ Automatic failover works
5. ✅ Cost tracking shows usage
6. ✅ No API key errors

**Test Command:**
```bash
python3 full_pipeline_test.py  # Should show LLM-powered decisions
```

---

## 📞 SUPPORT

**Issues?**
- Check `.env` configuration
- Verify API key is valid
- Check rate limits
- Review logs: `tail -f logs/queen.log`

**Need help?**
- Gemini: https://ai.google.dev/gemini-api/docs
- OpenAI: https://platform.openai.com/docs
- Anthropic: https://docs.anthropic.com

---

**END OF LLM SETUP GUIDE**
