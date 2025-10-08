#!/bin/bash
set -e

echo "🚀 Deploying OMK Hive to PRODUCTION..."
echo "========================================"
echo ""
echo "⚠️  WARNING: This will deploy to PRODUCTION!"
read -p "Are you sure you want to continue? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^yes$ ]]; then
    echo "Deployment cancelled."
    exit 1
fi

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
PROJECT_ID="${GCP_PROJECT_ID}"
REGION="us-central1"
CLUSTER_NAME="omk-hive-production"

# Verify we're on a tagged release
if ! git describe --exact-match --tags HEAD 2>/dev/null; then
    echo -e "${RED}Error: Must be on a tagged release to deploy to production${NC}"
    exit 1
fi

VERSION=$(git describe --tags --abbrev=0)
echo -e "${GREEN}Deploying version: ${VERSION}${NC}"

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI not found${NC}"
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites OK${NC}"

# Authenticate
echo -e "${YELLOW}Authenticating to GCP...${NC}"
gcloud config set project ${PROJECT_ID}
gcloud container clusters get-credentials ${CLUSTER_NAME} --region ${REGION}

# Build and push images
echo -e "${YELLOW}Building Docker images...${NC}"

IMAGE_TAG=${VERSION}

# Build API Gateway
docker build -t gcr.io/${PROJECT_ID}/api-gateway:${IMAGE_TAG} -f backend/api-gateway/Dockerfile backend/api-gateway
docker tag gcr.io/${PROJECT_ID}/api-gateway:${IMAGE_TAG} gcr.io/${PROJECT_ID}/api-gateway:latest
docker push gcr.io/${PROJECT_ID}/api-gateway:${IMAGE_TAG}
docker push gcr.io/${PROJECT_ID}/api-gateway:latest
echo -e "${GREEN}✓ API Gateway image pushed${NC}"

# Build Queen AI
docker build -t gcr.io/${PROJECT_ID}/queen-ai:${IMAGE_TAG} -f backend/queen-ai/Dockerfile backend/queen-ai
docker tag gcr.io/${PROJECT_ID}/queen-ai:${IMAGE_TAG} gcr.io/${PROJECT_ID}/queen-ai:latest
docker push gcr.io/${PROJECT_ID}/queen-ai:${IMAGE_TAG}
docker push gcr.io/${PROJECT_ID}/queen-ai:latest
echo -e "${GREEN}✓ Queen AI image pushed${NC}"

# Build Frontend
docker build -t gcr.io/${PROJECT_ID}/frontend:${IMAGE_TAG} -f frontend/web/Dockerfile frontend/web
docker tag gcr.io/${PROJECT_ID}/frontend:${IMAGE_TAG} gcr.io/${PROJECT_ID}/frontend:latest
docker push gcr.io/${PROJECT_ID}/frontend:${IMAGE_TAG}
docker push gcr.io/${PROJECT_ID}/frontend:latest
echo -e "${GREEN}✓ Frontend image pushed${NC}"

# Create backup of current deployment
echo -e "${YELLOW}Creating backup...${NC}"
kubectl get deployment api-gateway -n production -o yaml > backup-api-gateway-$(date +%Y%m%d-%H%M%S).yaml
kubectl get deployment queen-ai -n production -o yaml > backup-queen-ai-$(date +%Y%m%d-%H%M%S).yaml
kubectl get deployment frontend -n production -o yaml > backup-frontend-$(date +%Y%m%d-%H%M%S).yaml

# Deploy to Kubernetes
echo -e "${YELLOW}Deploying to Kubernetes...${NC}"

kubectl set image deployment/api-gateway api-gateway=gcr.io/${PROJECT_ID}/api-gateway:${IMAGE_TAG} -n production
kubectl set image deployment/queen-ai queen-ai=gcr.io/${PROJECT_ID}/queen-ai:${IMAGE_TAG} -n production
kubectl set image deployment/frontend frontend=gcr.io/${PROJECT_ID}/frontend:${IMAGE_TAG} -n production

# Wait for rollout
echo -e "${YELLOW}Waiting for rollout (timeout: 10 minutes)...${NC}"
kubectl rollout status deployment/api-gateway -n production --timeout=10m
kubectl rollout status deployment/queen-ai -n production --timeout=10m
kubectl rollout status deployment/frontend -n production --timeout=10m

# Health checks
echo -e "${YELLOW}Running health checks...${NC}"
sleep 30

API_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" https://api.omkhive.io/health)
if [ "$API_HEALTH" != "200" ]; then
    echo -e "${RED}API health check failed!${NC}"
    echo -e "${YELLOW}Rolling back...${NC}"
    kubectl rollout undo deployment/api-gateway -n production
    kubectl rollout undo deployment/queen-ai -n production
    kubectl rollout undo deployment/frontend -n production
    exit 1
fi

echo -e "${GREEN}✓ Health checks passed${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Production deployment complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Version: ${VERSION}"
echo "Services:"
echo "  - API Gateway: https://api.omkhive.io"
echo "  - Frontend: https://omkhive.io"
echo ""
echo "Monitoring:"
echo "  - Logs: https://console.cloud.google.com/logs"
echo "  - Metrics: https://console.cloud.google.com/monitoring"
echo ""
