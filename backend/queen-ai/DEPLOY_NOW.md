# 🚀 Deploy Now - Quick Start

**All deployment issues are FIXED. Deploy with one command!**

---

## ⚡ **ONE-COMMAND DEPLOYMENT**

```bash
cd backend/queen-ai && ./deploy.sh
```

**That's it!** The script will:
1. ✅ Build Docker image
2. ✅ Push to Google Container Registry  
3. ✅ Deploy to Cloud Run
4. ✅ Test health endpoint
5. ✅ Show your service URL

---

## 🔧 **FIRST TIME SETUP** (5 minutes)

If this is your first deployment:

```bash
# 1. Login to Google Cloud
gcloud auth login

# 2. Set your project
gcloud config set project YOUR_PROJECT_ID

# 3. Enable required services
gcloud services enable \
  run.googleapis.com \
  containerregistry.googleapis.com \
  cloudbuild.googleapis.com

# 4. Configure Docker
gcloud auth configure-docker

# 5. Deploy!
cd backend/queen-ai && ./deploy.sh
```

---

## 🐛 **WHAT WAS FIXED**

✅ Python version (3.11 → 3.13)  
✅ Requirements file mismatch  
✅ Docker layer caching  
✅ Redundant push steps  
✅ Real-time logging  
✅ Python paths  

**Status:** All 6 issues resolved ✅

---

## 📚 **DOCUMENTATION**

**Quick Start:** This file  
**Complete Guide:** `GCP_DEPLOYMENT_FIXES_COMPLETE.md` (80KB)  
**Summary:** `/DEPLOYMENT_FIXED_READY.md` (at project root)

---

## 🧪 **VERIFY DEPLOYMENT**

After deployment completes:

```bash
# Get service URL
gcloud run services describe omk-queen-ai \
  --region us-central1 \
  --format='value(status.url)'

# Test health
curl https://YOUR-SERVICE-URL/health

# Expected:
# {
#   "service": "Queen AI Orchestrator",
#   "version": "1.0.0",
#   "status": "healthy"
# }
```

---

## 💡 **TROUBLESHOOTING**

**Build fails?**
```bash
# Check Docker is running
docker ps

# Re-authenticate
gcloud auth configure-docker
```

**Deploy fails?**
```bash
# Check project is set
gcloud config get-value project

# Enable APIs
gcloud services list --enabled
```

**Service not responding?**
```bash
# Check logs
gcloud run logs read omk-queen-ai --region us-central1
```

---

## 💰 **COST**

**Free Tier:** 2M requests/month  
**After Free:** ~$40-55/month for 1M requests  
**Idle Cost:** $0 (scales to zero)

---

## 🎯 **READY TO DEPLOY?**

```bash
cd backend/queen-ai && ./deploy.sh
```

**Questions?** Read `GCP_DEPLOYMENT_FIXES_COMPLETE.md`

