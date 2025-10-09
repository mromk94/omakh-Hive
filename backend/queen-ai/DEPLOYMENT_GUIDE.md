# DEPLOYMENT GUIDE - OMK Hive Queen AI

Complete guide for deploying the Queen AI to production.

---

## 📋 **PRE-DEPLOYMENT CHECKLIST**

### **1. Infrastructure Setup**

- [ ] PostgreSQL database (Cloud SQL or self-hosted)
- [ ] Redis server (Cloud Memorystore or self-hosted)
- [ ] Infura/Alchemy RPC endpoints
- [ ] Gemini API key (at minimum)
- [ ] Domain name configured
- [ ] SSL certificates ready

### **2. Security**

- [ ] Admin API keys generated
- [ ] Secrets moved to Secret Manager (GCP/AWS)
- [ ] Firewall rules configured
- [ ] Private keys in hardware wallet/HSM
- [ ] Emergency contacts configured

### **3. Testing**

- [ ] All unit tests passing (27/27)
- [ ] Integration tests run with testnet
- [ ] Load testing completed
- [ ] Security audit completed

---

## 🚀 **DEPLOYMENT OPTIONS**

### **Option 1: Local/Development**

```bash
# 1. Install dependencies
pip install -r core-requirements.txt

# 2. Set up PostgreSQL
createdb omk_hive
python3 setup_database.py

# 3. Set up Redis
brew install redis
brew services start redis

# 4. Configure environment
cp .env.example .env
# Edit .env with your values

# 5. Run migrations
alembic upgrade head

# 6. Start server
uvicorn main:app --reload
```

---

### **Option 2: Docker**

```bash
# 1. Build image
docker build -t omk-queen-ai:latest .

# 2. Run with docker-compose
docker-compose up -d

# 3. Check logs
docker-compose logs -f queen-ai
```

**docker-compose.yml** (see file below)

---

### **Option 3: Google Cloud Platform (Recommended)**

#### **A. Cloud SQL + Cloud Run**

```bash
# 1. Create Cloud SQL instance
gcloud sql instances create omk-hive-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# 2. Create database
gcloud sql databases create omk_hive --instance=omk-hive-db

# 3. Create Memorystore (Redis)
gcloud redis instances create omk-hive-redis \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_7_0

# 4. Deploy to Cloud Run
gcloud run deploy omk-queen-ai \
  --image gcr.io/PROJECT_ID/omk-queen-ai:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="DATABASE_URL=...,REDIS_URL=..." \
  --add-cloudsql-instances=PROJECT_ID:us-central1:omk-hive-db
```

#### **B. Google Kubernetes Engine (GKE)**

```bash
# 1. Create GKE cluster
gcloud container clusters create omk-hive-cluster \
  --num-nodes=3 \
  --machine-type=n1-standard-2 \
  --region=us-central1

# 2. Apply Kubernetes manifests
kubectl apply -f k8s/

# 3. Check deployment
kubectl get pods
kubectl logs -f deployment/queen-ai
```

---

## 📦 **CONFIGURATION FILES**

### **.env (Production)**

```bash
# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Database (Cloud SQL)
DATABASE_URL=postgresql://user:pass@/omk_hive?host=/cloudsql/PROJECT_ID:us-central1:omk-hive-db

# Redis (Memorystore)
REDIS_URL=redis://10.0.0.3:6379/0

# LLM Providers
DEFAULT_LLM_PROVIDER=gemini
GEMINI_API_KEY=${SECRET:gemini-api-key}  # From Secret Manager
OPENAI_API_KEY=${SECRET:openai-api-key}
ANTHROPIC_API_KEY=${SECRET:anthropic-api-key}

# Blockchain
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/${SECRET:infura-key}
QUEEN_WALLET_ADDRESS=0x...
# NEVER set QUEEN_PRIVATE_KEY in .env - use Secret Manager!

# Security
API_KEY_HEADER=X-API-Key
ADMIN_API_KEYS=${SECRET:admin-api-keys}

# CORS
CORS_ORIGINS=https://app.omk.network,https://admin.omk.network
```

---

### **Dockerfile**

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY core-requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r core-requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 queen && chown -R queen:queen /app
USER queen

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### **docker-compose.yml**

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: omk_user
      POSTGRES_PASSWORD: omk_password
      POSTGRES_DB: omk_hive
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U omk_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  queen-ai:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://omk_user:omk_password@postgres:5432/omk_hive
      REDIS_URL: redis://redis:6379/0
      GEMINI_API_KEY: ${GEMINI_API_KEY}
      ETHEREUM_RPC_URL: ${ETHEREUM_RPC_URL}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

---

### **Kubernetes Deployment (k8s/deployment.yaml)**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: queen-ai
  labels:
    app: queen-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: queen-ai
  template:
    metadata:
      labels:
        app: queen-ai
    spec:
      containers:
      - name: queen-ai
        image: gcr.io/PROJECT_ID/omk-queen-ai:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: queen-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: queen-secrets
              key: redis-url
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: queen-secrets
              key: gemini-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: queen-ai-service
spec:
  selector:
    app: queen-ai
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

## 🔒 **SECRET MANAGEMENT**

### **GCP Secret Manager**

```bash
# Store secrets
echo -n "your-gemini-key" | gcloud secrets create gemini-api-key --data-file=-
echo -n "postgresql://..." | gcloud secrets create database-url --data-file=-
echo -n "admin-key-1,admin-key-2" | gcloud secrets create admin-api-keys --data-file=-

# Grant access to service account
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:queen-ai@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## 📊 **MONITORING & LOGGING**

### **Set up Cloud Monitoring**

```bash
# Enable APIs
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com

# Create alert policies (in console or via Terraform)
```

### **Key Metrics to Monitor**

- Request latency (p50, p95, p99)
- Error rate
- Database connection pool
- Redis memory usage
- LLM API costs
- Bee task queue depth
- System health score

### **Log Aggregation**

Structured logs are automatically sent to Cloud Logging. Query with:

```
resource.type="cloud_run_revision"
resource.labels.service_name="omk-queen-ai"
severity>=ERROR
```

---

## 🚨 **EMERGENCY PROCEDURES**

### **Emergency Shutdown**

```bash
# Via API (requires admin key)
curl -X POST https://api.omk.network/admin/emergency-shutdown \
  -H "X-API-Key: ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Security incident detected"}'

# Via kubectl
kubectl scale deployment queen-ai --replicas=0
```

### **Rollback**

```bash
# Cloud Run
gcloud run services update-traffic omk-queen-ai \
  --to-revisions=omk-queen-ai-00001-abc=100

# Kubernetes
kubectl rollout undo deployment/queen-ai
```

---

## 🧪 **POST-DEPLOYMENT VERIFICATION**

```bash
# 1. Health check
curl https://api.omk.network/health

# 2. Check database
curl https://api.omk.network/admin/stats -H "X-API-Key: ADMIN_KEY"

# 3. Test bee functionality
curl https://api.omk.network/bees/maths/health -H "X-API-Key: ADMIN_KEY"

# 4. Check logs
kubectl logs -f deployment/queen-ai | grep ERROR
```

---

## 💰 **COST ESTIMATION (Monthly)**

| Component | Cost |
|-----------|------|
| Cloud SQL (db-f1-micro) | $25 |
| Memorystore Redis (1GB) | $35 |
| Cloud Run (3 instances) | $50-100 |
| Gemini API (avg usage) | $10-30 |
| Infura/Alchemy | $0 (free tier) |
| **Total** | **$120-190/month** |

---

## 📞 **SUPPORT & TROUBLESHOOTING**

### **Common Issues**

1. **Database connection failed**
   - Check Cloud SQL instance is running
   - Verify DATABASE_URL is correct
   - Check IAM permissions

2. **Redis connection failed**
   - Verify Memorystore IP is correct
   - Check VPC network connectivity
   - Verify REDIS_URL format

3. **LLM API errors**
   - Check API key is valid
   - Verify not rate-limited
   - Check API key has credits

### **Getting Help**

- Check logs: `kubectl logs deployment/queen-ai`
- Review metrics: Cloud Console → Monitoring
- Emergency contact: [Your contact info]

---

**Last Updated**: October 9, 2025  
**Version**: 1.0.0  
**Status**: Production Ready (after completing PHASE 2 integrations)
