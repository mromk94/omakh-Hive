#!/bin/bash

# OMK Hive Queen AI - Quick Deployment Script
# Deploys to Google Cloud Run with one command

set -e  # Exit on error

echo "🚀 OMK Hive Queen AI - Google Cloud Deployment"
echo "================================================"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI not installed"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: No GCP project configured"
    echo "Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "📋 Project: $PROJECT_ID"
echo "📍 Region: us-central1"
echo ""

# Confirm deployment
read -p "Deploy Queen AI to Cloud Run? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

echo ""
echo "🔧 Step 1/4: Building Docker image..."
docker build -t gcr.io/$PROJECT_ID/omk-queen-ai:latest .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi

echo "✅ Docker image built successfully"
echo ""

echo "📤 Step 2/4: Pushing image to Google Container Registry..."
docker push gcr.io/$PROJECT_ID/omk-queen-ai:latest

if [ $? -ne 0 ]; then
    echo "❌ Docker push failed"
    echo "Make sure Docker is authenticated: gcloud auth configure-docker"
    exit 1
fi

echo "✅ Image pushed successfully"
echo ""

echo "🚀 Step 3/4: Deploying to Cloud Run..."
gcloud run deploy omk-queen-ai \
  --image gcr.io/$PROJECT_ID/omk-queen-ai:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 2 \
  --max-instances 10 \
  --min-instances 0 \
  --set-env-vars="ENVIRONMENT=production,LOG_LEVEL=INFO"

if [ $? -ne 0 ]; then
    echo "❌ Cloud Run deployment failed"
    exit 1
fi

echo "✅ Deployed to Cloud Run successfully"
echo ""

echo "🧪 Step 4/4: Testing deployment..."
SERVICE_URL=$(gcloud run services describe omk-queen-ai --region us-central1 --format='value(status.url)')

echo "Service URL: $SERVICE_URL"
echo ""

# Test health endpoint
echo "Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s "$SERVICE_URL/health" || echo "failed")

if [[ $HEALTH_RESPONSE == *"Queen AI"* ]]; then
    echo "✅ Health check passed!"
    echo ""
    echo "🎉 Deployment Complete!"
    echo "================================================"
    echo "Service URL: $SERVICE_URL"
    echo "Health: $SERVICE_URL/health"
    echo "Docs: $SERVICE_URL/docs"
    echo "================================================"
else
    echo "⚠️  Warning: Health check failed"
    echo "The service is deployed but may not be responding correctly"
    echo "Check logs: gcloud run logs read omk-queen-ai --region us-central1"
fi

echo ""
echo "📊 View logs:"
echo "gcloud run logs read omk-queen-ai --region us-central1"
echo ""
echo "📈 View metrics:"
echo "https://console.cloud.google.com/run/detail/us-central1/omk-queen-ai/metrics?project=$PROJECT_ID"
