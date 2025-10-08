#!/bin/bash
set -e

echo "🚀 Deploying OMK Hive to Staging..."
echo "===================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
PROJECT_ID="${GCP_PROJECT_ID}"
REGION="us-central1"
CLUSTER_NAME="omk-hive-staging"

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

IMAGE_TAG=$(git rev-parse --short HEAD)

# Build API Gateway
docker build -t gcr.io/${PROJECT_ID}/api-gateway:${IMAGE_TAG} -f backend/api-gateway/Dockerfile backend/api-gateway
docker push gcr.io/${PROJECT_ID}/api-gateway:${IMAGE_TAG}
echo -e "${GREEN}✓ API Gateway image pushed${NC}"

# Build Queen AI
docker build -t gcr.io/${PROJECT_ID}/queen-ai:${IMAGE_TAG} -f backend/queen-ai/Dockerfile backend/queen-ai
docker push gcr.io/${PROJECT_ID}/queen-ai:${IMAGE_TAG}
echo -e "${GREEN}✓ Queen AI image pushed${NC}"

# Build Frontend
docker build -t gcr.io/${PROJECT_ID}/frontend:${IMAGE_TAG} -f frontend/web/Dockerfile frontend/web
docker push gcr.io/${PROJECT_ID}/frontend:${IMAGE_TAG}
echo -e "${GREEN}✓ Frontend image pushed${NC}"

# Deploy to Kubernetes
echo -e "${YELLOW}Deploying to Kubernetes...${NC}"

kubectl set image deployment/api-gateway api-gateway=gcr.io/${PROJECT_ID}/api-gateway:${IMAGE_TAG} -n staging
kubectl set image deployment/queen-ai queen-ai=gcr.io/${PROJECT_ID}/queen-ai:${IMAGE_TAG} -n staging
kubectl set image deployment/frontend frontend=gcr.io/${PROJECT_ID}/frontend:${IMAGE_TAG} -n staging

# Wait for rollout
echo -e "${YELLOW}Waiting for rollout...${NC}"
kubectl rollout status deployment/api-gateway -n staging
kubectl rollout status deployment/queen-ai -n staging
kubectl rollout status deployment/frontend -n staging

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Staging deployment complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Services:"
echo "  - API Gateway: https://api-staging.omkhive.io"
echo "  - Frontend: https://staging.omkhive.io"
echo ""
