# OMK Hive Deployment Guide

## Overview

This guide covers deploying OMK Hive to various environments from local development to production on Google Cloud Platform (GCP).

## Prerequisites

### Required Tools
- **Docker** (20.0+)
- **Docker Compose** (2.0+)
- **kubectl** (1.28+)
- **gcloud CLI** (latest)
- **Terraform** (1.5+)
- **Node.js** (20+)
- **Python** (3.11+)

### Required Accounts
- Google Cloud Platform account
- GitHub account (for CI/CD)
- Domain name (for production)
- Infura/Alchemy account (for blockchain RPC)

## Local Development Deployment

### Quick Start
```bash
# Clone repository
git clone https://github.com/mromk94/omakh-Hive.git
cd omakh-Hive

# Run setup
./scripts/setup/init.sh

# Start services
docker-compose up -d

# Verify
docker ps
```

### Individual Services
```bash
# Databases only
docker-compose up -d postgres redis

# API Gateway
cd backend/api-gateway
npm run start:dev

# Queen AI
cd backend/queen-ai
source venv/bin/activate
uvicorn main:app --reload

# Frontend
cd frontend/web
npm run dev
```

### Access Services
- Frontend: http://localhost:3001
- API Gateway: http://localhost:3000
- API Docs: http://localhost:3000/api/docs
- GraphQL: http://localhost:3000/graphql
- Queen AI: http://localhost:8000
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## Google Cloud Platform Setup

### 1. Create GCP Project
```bash
# Set project ID
export PROJECT_ID="omk-hive-prod"
export REGION="us-central1"

# Create project
gcloud projects create $PROJECT_ID

# Set as default
gcloud config set project $PROJECT_ID

# Enable billing (required)
gcloud beta billing accounts list
gcloud beta billing projects link $PROJECT_ID \
  --billing-account=BILLING_ACCOUNT_ID
```

### 2. Enable Required APIs
```bash
gcloud services enable \
  container.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  secretmanager.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  cloudresourcemanager.googleapis.com \
  compute.googleapis.com \
  servicenetworking.googleapis.com \
  vpcaccess.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com
```

### 3. Create Service Account
```bash
# Create service account
gcloud iam service-accounts create omk-hive-deployer \
  --display-name="OMK Hive Deployer"

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:omk-hive-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/container.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:omk-hive-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudsql.admin"

# Create key
gcloud iam service-accounts keys create ~/gcp-key.json \
  --iam-account=omk-hive-deployer@$PROJECT_ID.iam.gserviceaccount.com
```

## Infrastructure as Code (Terraform)

### Initialize Terraform
```bash
cd infrastructure/terraform

# Initialize
terraform init

# Plan
terraform plan -var="project_id=$PROJECT_ID" -var="region=$REGION"

# Apply
terraform apply -var="project_id=$PROJECT_ID" -var="region=$REGION"
```

### Terraform Creates
- GKE cluster (auto-scaling)
- Cloud SQL (PostgreSQL)
- Memorystore (Redis)
- VPC network
- Load balancers
- Artifact Registry
- Secret Manager secrets
- IAM roles and bindings

## Kubernetes Deployment

### 1. Connect to Cluster
```bash
gcloud container clusters get-credentials omk-hive-prod \
  --region=$REGION \
  --project=$PROJECT_ID
```

### 2. Create Namespaces
```bash
kubectl create namespace staging
kubectl create namespace production
```

### 3. Create Secrets
```bash
# Database credentials
kubectl create secret generic db-credentials \
  --from-literal=username=omk_user \
  --from-literal=password=$(openssl rand -base64 32) \
  -n production

# API keys
kubectl create secret generic api-keys \
  --from-literal=jwt-secret=$(openssl rand -base64 32) \
  --from-literal=gemini-api-key=$GEMINI_API_KEY \
  --from-literal=openai-api-key=$OPENAI_API_KEY \
  -n production
```

### 4. Deploy Services
```bash
# Deploy to staging
kubectl apply -f infrastructure/k8s/base/ -n staging

# Deploy to production
kubectl apply -f infrastructure/k8s/base/ -n production
```

### 5. Verify Deployment
```bash
# Check pods
kubectl get pods -n production

# Check services
kubectl get services -n production

# Check ingress
kubectl get ingress -n production

# View logs
kubectl logs -f deployment/api-gateway -n production
```

## CI/CD with GitHub Actions

### 1. Configure GitHub Secrets
In GitHub repository settings, add:
- `GCP_PROJECT_ID` - Your GCP project ID
- `GCP_SA_KEY` - Service account JSON key
- `STAGING_DATABASE_URL` - Staging DB connection
- `PRODUCTION_DATABASE_URL` - Production DB connection
- `SEPOLIA_RPC_URL` - Testnet RPC endpoint
- `MAINNET_RPC_URL` - Mainnet RPC endpoint
- `STAGING_DEPLOYER_PRIVATE_KEY` - Testnet deployer key
- `PRODUCTION_DEPLOYER_PRIVATE_KEY` - Mainnet deployer key
- `ETHERSCAN_API_KEY` - For contract verification

### 2. Workflows
- **CI Workflows**: Run on every push
  - `ci-contracts.yml` - Test smart contracts
  - `ci-backend.yml` - Test backend
  - `ci-frontend.yml` - Test frontend
  - `ci-queen-ai.yml` - Test Queen AI

- **Deployment Workflows**: Run on specific branches
  - `deploy-staging.yml` - Deploy to staging (staging branch)
  - `deploy-production.yml` - Deploy to production (releases)

### 3. Deployment Process
```bash
# Deploy to staging
git checkout staging
git merge develop
git push origin staging
# GitHub Actions automatically deploys

# Deploy to production
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
# GitHub Actions automatically deploys
```

## Smart Contract Deployment

### Testnet (Sepolia)
```bash
cd contracts/ethereum

# Compile
npm run compile

# Deploy
npm run deploy:sepolia

# Verify
npm run verify
```

### Mainnet
```bash
# Must be on tagged release
git describe --exact-match --tags

# Deploy (requires approval)
npm run deploy:mainnet

# Verify on Etherscan
npm run verify
```

## Database Migrations

### Run Migrations
```bash
# Development
./scripts/database/migrate.sh development

# Staging
./scripts/database/migrate.sh staging

# Production (requires confirmation)
./scripts/database/migrate.sh production
```

## Monitoring & Logging

### Set Up Monitoring
```bash
# Deploy monitoring stack
kubectl apply -f infrastructure/k8s/monitoring/

# Access Grafana
kubectl port-forward svc/grafana 3000:3000 -n monitoring
```

### View Logs
```bash
# GCP Console
gcloud logging read "resource.type=k8s_container" --limit 50

# Kubectl
kubectl logs -f deployment/api-gateway -n production

# All containers in pod
kubectl logs -f deployment/queen-ai --all-containers -n production
```

### Alerts
Alerts are configured for:
- High error rates
- High response times
- Pod crashes
- Resource limits
- Database issues

## Backup & Disaster Recovery

### Database Backups
```bash
# Automated daily backups via Cloud SQL
# Manual backup
gcloud sql backups create --instance=omk-hive-db

# Restore from backup
gcloud sql backups restore BACKUP_ID --backup-instance=omk-hive-db
```

### Kubernetes Backup
```bash
# Backup all resources
kubectl get all --all-namespaces -o yaml > k8s-backup.yaml

# Backup specific namespace
kubectl get all -n production -o yaml > production-backup.yaml
```

## Scaling

### Auto-Scaling
```bash
# HPA (Horizontal Pod Autoscaler)
kubectl autoscale deployment api-gateway \
  --min=2 --max=10 --cpu-percent=70 \
  -n production

# Cluster autoscaling (configured in Terraform)
# Automatically adds/removes nodes
```

### Manual Scaling
```bash
# Scale deployment
kubectl scale deployment/api-gateway --replicas=5 -n production

# Scale GKE cluster
gcloud container clusters resize omk-hive-prod \
  --num-nodes=5 --region=$REGION
```

## SSL/TLS Certificates

### Using Google-Managed Certificates
```yaml
# In ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    networking.gke.io/managed-certificates: omk-hive-cert
```

### Using cert-manager (Let's Encrypt)
```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create issuer
kubectl apply -f infrastructure/k8s/cert-issuer.yaml
```

## Health Checks & Readiness

All services implement:
- **Liveness probe**: Is the service alive?
- **Readiness probe**: Can the service handle traffic?
- **Startup probe**: Has the service started?

## Rollback

### Kubernetes Rollback
```bash
# View rollout history
kubectl rollout history deployment/api-gateway -n production

# Rollback to previous version
kubectl rollout undo deployment/api-gateway -n production

# Rollback to specific revision
kubectl rollout undo deployment/api-gateway --to-revision=2 -n production
```

### Full System Rollback
```bash
# Revert to previous release tag
git checkout v1.0.0
./scripts/deploy/production.sh
```

## Cost Optimization

### Recommendations
1. Use preemptible nodes for non-critical workloads
2. Enable cluster autoscaling
3. Use Cloud SQL read replicas only when needed
4. Implement proper caching (Redis)
5. Use Cloud CDN for static assets
6. Set resource limits on pods
7. Clean up unused resources regularly

## Troubleshooting

### Common Issues

**Pods not starting**:
```bash
kubectl describe pod POD_NAME -n production
kubectl logs POD_NAME -n production
```

**Database connection issues**:
```bash
# Test connection from pod
kubectl run -it --rm debug --image=postgres:16 --restart=Never -- \
  psql -h DB_HOST -U omk_user -d omk_hive
```

**Image pull errors**:
```bash
# Verify image exists
gcloud artifacts docker images list $REGION-docker.pkg.dev/$PROJECT_ID/omk-hive

# Check permissions
kubectl get serviceaccount default -o yaml -n production
```

## Security Checklist

- [ ] Secrets stored in Secret Manager
- [ ] Network policies applied
- [ ] RBAC configured
- [ ] TLS enabled on all endpoints
- [ ] Database encrypted at rest
- [ ] Regular security scans enabled
- [ ] Container images scanned
- [ ] VPC configured with private IPs
- [ ] Firewall rules restrictive
- [ ] Monitoring and alerting configured

## Support

- **Documentation**: https://docs.omkhive.io
- **GitHub Issues**: https://github.com/mromk94/omakh-Hive/issues
- **DevOps Email**: devops@omkhive.io

---

**Last Updated**: October 8, 2025
