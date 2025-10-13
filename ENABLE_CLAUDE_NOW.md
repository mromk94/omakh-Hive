# 🚀 Enable Claude & All LLM Features - Quick Start

## ✅ **DONE:**
- Claude API key added to `.env`
- Real Claude analysis implemented
- System ready for AI-powered features

## 🔧 **FINAL STEP: Set Default LLM Provider**

Run this command:

```bash
cd backend/queen-ai
echo "DEFAULT_LLM_PROVIDER=anthropic" >> .env
```

Or manually edit `.env` and change:
```bash
# FROM:
DEFAULT_LLM_PROVIDER=gemini

# TO:
DEFAULT_LLM_PROVIDER=anthropic
```

## 🚀 **Start Backend:**

```bash
cd backend/queen-ai
python3 start.py --component queen
```

## ✅ **Test It Works:**

```bash
# Test Claude health
curl http://localhost:8001/api/v1/admin/claude/health

# Test Claude analysis (real AI!)
curl -H "Authorization: Bearer dev_token" \
  http://localhost:8001/api/v1/admin/claude/analysis

# Test Queen chat
curl -X POST http://localhost:8001/api/v1/queen/chat \
  -H "Authorization: Bearer dev_token" \
  -H "Content-Type: application/json" \
  -d '{"message": "Analyze the system performance"}'
```

## 📊 **What You Get:**

1. ✅ **Real Claude Analysis** - AI-powered system insights
2. ✅ **Queen AI Chat** - Intelligent conversations
3. ✅ **Development Assistant** - Code generation & reviews
4. ✅ **Security Analysis** - AI-powered security checks

## 💰 **Cost:**

- **Claude 3.5 Sonnet:** $3/$15 per 1M tokens (input/output)
- **Estimated:** $20-50/month for typical usage
- **Alternative:** Add Gemini key (FREE tier available)

## 🎯 **Ready to Go!**

Your Claude API key is configured. Just set the default provider and restart!
