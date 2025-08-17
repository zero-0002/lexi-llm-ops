#!/bin/bash
# 🔧 Simple Secret Creation from .env.secrets file
# ================================================

echo "🔐 Creating Development Secrets from .env.secrets"
echo "================================================="

# Create secrets-store namespace
kubectl create namespace secrets-store --dry-run=client -o yaml | kubectl apply -f -

# Check if .env.secrets file exists
if [ ! -f "../.env.secrets" ]; then
  echo "⚠️  .env.secrets file not found. Creating sample file..."
  cat > ../.env.secrets << 'EOF'
# 🔐 SECRETS ONLY - Never commit to git
# ====================================

# Database Secrets
MONGODB_PASSWORD=legal-mongo-dev-password-123
REDIS_PASSWORD=legal-redis-dev-password-123

# API Keys
OPENAI_API_KEY=sk-your-openai-api-key-here
SERPER_API_KEY=your-serper-api-key-here

# Security Secrets
SECRET_KEY=legal-app-secret-key-development
JWT_SECRET=legal-jwt-super-secret-key-development
ENCRYPTION_KEY=legal-32-char-encryption-dev-key
EOF
  echo "✅ Sample .env file created. Please update with your values."
  echo "⚠️  Make sure to add .env.secrets to .gitignore!"
fi

# Load .env file
set -a
source ../.env
set +a

echo "📦 Creating secrets from .env  ..."

# MongoDB credentials
kubectl create secret generic mongodb-credentials \
  --from-literal=username="legal_user" \
  --from-literal=password="${MONGODB_PASSWORD}" \
  -n secrets-store \
  --dry-run=client -o yaml | kubectl apply -f -

# Redis credentials  
kubectl create secret generic redis-credentials \
  --from-literal=password="${REDIS_PASSWORD:-}" \
  -n secrets-store \
  --dry-run=client -o yaml | kubectl apply -f -

# OpenAI credentials
kubectl create secret generic openai-credentials \
  --from-literal=api_key="${OPENAI_API_KEY}" \
  -n secrets-store \
  --dry-run=client -o yaml | kubectl apply -f -

# SERPER credentials
kubectl create secret generic serper-credentials \
  --from-literal=api_key="${SERPER_API_KEY}" \
  -n secrets-store \
  --dry-run=client -o yaml | kubectl apply -f -

# Auth secrets
kubectl create secret generic auth-secrets \
  --from-literal=jwt_secret="${JWT_SECRET}" \
  --from-literal=secret_key="${SECRET_KEY}" \
  --from-literal=encryption_key="${ENCRYPTION_KEY}" \
  -n secrets-store \
  --dry-run=client -o yaml | kubectl apply -f -

# System configuration (from .env.config)
if [ -f "../.env.config" ]; then
  # Frontend config (non-secret URLs)
  kubectl create secret generic frontend-config \
    --from-literal=api_base_url="http://legal-backend-api.application.svc.cluster.local:8000" \
    --from-literal=ws_url="ws://legal-backend-api.application.svc.cluster.local:8000" \
    -n secrets-store \
    --dry-run=client -o yaml | kubectl apply -f -
fi

echo ""
echo "✅ Development secrets created from .env.secrets!"
echo ""
echo "🔍 Verifying created secrets:"
kubectl get secrets -n secrets-store

echo ""
echo "📝 Note: System configuration should be managed via Helm values files"
