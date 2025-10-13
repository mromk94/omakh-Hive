# Backend Deployment - Issues & Solutions

**Last Updated:** October 10, 2025, 6:35 PM

---

## Issues Encountered

### Issue 1: Missing `pydantic-settings`
**Error:** `ModuleNotFoundError: No module named 'pydantic_settings'`  
**Cause:** Package not in requirements-prod.txt  
**Solution:** ✅ Added `pydantic-settings==2.1.0`

### Issue 2: Missing `solders` (Rust dependency)
**Error:** `ModuleNotFoundError: No module named 'solders'`  
**Cause:** `solders` requires Rust compiler to build from source  
**Solution:** ✅ Temporarily disabled Solana packages, made imports optional

### Issue 3: httpx Version Conflict
**Error:** `solana 0.30.2 depends on httpx<0.24.0 but requested httpx==0.25.0`  
**Cause:** Version mismatch between dependencies  
**Solution:** ✅ Changed `httpx==0.25.0` → `httpx==0.23.3`

---

## Current Status

**Deployment:** 🔄 Building (attempt #6)

**Changes Applied:**
- ✅ Solana packages commented out
- ✅ Solana imports made optional in code
- ✅ httpx downgraded to 0.23.3 (compatible version)
- ✅ Dockerfile simplified (no Rust)
- ✅ Memory increased to 2GB
- ✅ CPU increased to 2 cores
- ✅ Timeout increased to 600s

**Expected:** Should deploy successfully this time

---

## If This Fails Again

### Option 1: Simplify Further
Remove more optional dependencies until we get a minimal working deployment:
```python
# Could temporarily disable:
# - google-cloud-aiplatform (use openai only)
# - asyncpg (use sqlite temporarily)
# - redis (disable caching)
```

### Option 2: Use Docker Directly
Build and push image manually:
```bash
docker build -t gcr.io/omk-hive/omk-queen-ai .
docker push gcr.io/omk-hive/omk-queen-ai
gcloud run deploy omk-queen-ai --image gcr.io/omk-hive/omk-queen-ai
```

### Option 3: Use Cloud Build Trigger
Set up automatic builds from GitHub:
- Longer build timeout (20 min)
- More resources
- Better caching

---

## Once Deployed Successfully

### Test Endpoints:
```bash
# Health check
curl https://omk-queen-ai-475745165557.us-central1.run.app/

# API docs
curl https://omk-queen-ai-475745165557.us-central1.run.app/docs

# Queen status
curl https://omk-queen-ai-475745165557.us-central1.run.app/api/v1/queen/status
```

### Next Steps:
1. Deploy frontend with backend URL
2. Test end-to-end
3. Re-enable Solana (later, when needed)

---

**Status:** Waiting for build to complete...
