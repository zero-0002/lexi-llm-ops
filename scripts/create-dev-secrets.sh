#!/bin/bash
# 🔧 Simple Secret Creation from .env files
# =========================================

echo "🔐 Creating Development Secrets from .env"
echo "========================================="

# Create secrets-store namespace
kubectl create namespace secrets-store --dry-run=client -o yaml | kubectl apply -f -

# Check if .env file exists
if [ ! -f "../.env" ]; then
  echo "⚠️  .env file not found. Creating sample .env file..."
  cat > ../.env << 'EOF'
# Database Configuration
MONGO_USERNAME=legaluser
MONGO_PASSWORD=legal-mongo-dev-password-123

REDIS_PASSWORD=legal-redis-dev-password-123

# API Keys
OPENAI_API_KEY=sk-your-openai-api-key-here

# Authentication
JWT_SECRET=legal-jwt-super-secret-key-development
SECRET_KEY=legal-app-secret-key-development
ENCRYPTION_KEY=legal-32-char-encryption-dev-key

# Frontend Configuration  
API_BASE_URL=http://legal-backend-api.application.svc.cluster.local:8000

# Analytics
GA_TRACKING_ID=GA-DEVELOPMENT-ID
ENABLE_ANALYTICS=false
EOF
  echo "✅ Sample .env file created. Please update with your values."
fi

# Load .env file
set -a
source ../.env
set +a

echo "📦 Creating secrets from .env..."

# MongoDB credentials
kubectl create secret generic mongodb-credentials \
  --from-literal=username="${MONGO_USERNAME}" \
  --from-literal=password="${MONGO_PASSWORD}" \
  -n secrets-store \
  --dry-run=client -o yaml | kubectl apply -f -

# Redis credentials  
kubectl create secret generic redis-credentials \
  --from-literal=password="${REDIS_PASSWORD}" \
  -n secrets-store \
  --dry-run=client -o yaml | kubectl apply -f -

# OpenAI credentials
kubectl create secret generic openai-credentials \
  --from-literal=api_key="${OPENAI_API_KEY}" \
  -n secrets-store \
  --dry-run=client -o yaml | kubectl apply -f -

# Auth secrets
kubectl create secret generic auth-secrets \
  --from-literal=jwt_secret="${JWT_SECRET}" \
  --from-literal=secret_key="${SECRET_KEY}" \
  --from-literal=encryption_key="${ENCRYPTION_KEY}" \
  -n secrets-store \
  --dry-run=client -o yaml | kubectl apply -f -

# Frontend config
kubectl create secret generic frontend-config \
  --from-literal=api_base_url="${API_BASE_URL}" \
  -n secrets-store \
  --dry-run=client -o yaml | kubectl apply -f -

# Analytics config
kubectl create secret generic analytics-config \
  --from-literal=ga_tracking_id="${GA_TRACKING_ID}" \
  --from-literal=enable_analytics="${ENABLE_ANALYTICS}" \
  -n secrets-store \
  --dry-run=client -o yaml | kubectl apply -f -

echo ""
echo "✅ Development secrets created from .env file!"
echo ""
echo "🔍 Verifying created secrets:"
kubectl get secrets -n secrets-store
