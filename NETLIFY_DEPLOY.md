# 🚀 Deploy to Netlify

## Quick Deploy Steps

### 1. Push to GitHub
```bash
cd /Users/mac/CascadeProjects/omakh-Hive
git add .
git commit -m "Ready for Netlify deployment"
git push origin main
```

### 2. Deploy on Netlify

**Option A: Netlify CLI (Fastest)**
```bash
cd omk-frontend
npm install -g netlify-cli
netlify login
netlify init
netlify deploy --prod
```

**Option B: Netlify Dashboard**
1. Go to https://app.netlify.com
2. Click "Add new site" → "Import existing project"
3. Connect GitHub repository
4. Configure:
   - **Base directory:** `omk-frontend`
   - **Build command:** `npm run build`
   - **Publish directory:** `.next`
5. Click "Deploy site"

### 3. Environment Variables (In Netlify Dashboard)

Go to: Site settings → Environment variables

Add:
```
NEXT_PUBLIC_QUEEN_API_URL = https://your-backend-url.com
```

**Note:** Backend must be deployed separately (not on Netlify - use Railway, Render, or GCP)

### 4. Custom Domain (Optional)

Site settings → Domain management → Add custom domain

## Files Created
- ✅ `netlify.toml` - Build config
- ✅ `.env.production` - Production env vars

## Important Notes

⚠️ **Backend Deployment Required**
- Netlify only hosts frontend
- Deploy backend to Railway/Render/GCP
- Update `NEXT_PUBLIC_QUEEN_API_URL` with backend URL

⚠️ **WalletConnect**
- WalletConnect removed (was causing errors)
- Only injected wallets (MetaMask) work
- Add back when you have valid project ID

## Test Local Production Build
```bash
cd omk-frontend
npm run build
npm start
```

## Live URL
After deployment: `https://your-site-name.netlify.app`

## Backend Deployment Options

### Railway (Recommended)
```bash
cd backend/queen-ai
railway login
railway init
railway up
```

### Render
1. Connect GitHub repo
2. Set root: `backend/queen-ai`
3. Build: `pip install -r requirements.txt`
4. Start: `python main.py`

### Google Cloud Run
```bash
cd backend/queen-ai
gcloud run deploy queen-ai --source .
```

## Status
- ✅ Frontend ready for Netlify
- ⏳ Backend needs separate hosting
- ⏳ Update API URL after backend deployed
