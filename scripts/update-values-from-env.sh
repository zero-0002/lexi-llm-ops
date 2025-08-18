#!/bin/bash
# Script để cập nhật values.yaml với values từ .env file

echo "🔧 Updating values.yaml with .env values..."

# Load .env file
if [ ! -f "../.env" ]; then
  echo "❌ .env file not found!"
  exit 1
fi

set -a
source ../.env
set +a

# Backup original values.yaml
cp ../helm/charts/setup-secrets/values.yaml ../helm/charts/setup-secrets/values.yaml.backup

# Update values.yaml với actual values từ .env
cat > ../helm/charts/setup-secrets/values.yaml << EOF
# Simple setup-secrets chart for Legal Retrieval
# Values được cập nhật từ .env file

# Environment configuration
environment: development

# Namespaces
namespaces:
  application: application

# Base secrets configuration từ .env file
baseSecrets:
  enabled: true
  
  mongodb:
    username: legal_user
    password: "${MONGODB_PASSWORD:-legal-mongo-dev-password-123}"
    
  redis:
    password: "${REDIS_PASSWORD:-legal-redis-dev-password-123}"
    
  openai:
    apiKey: "${OPENAI_API_KEY:-sk-your-openai-api-key-here}"
    
  auth:
    jwtSecret: "${JWT_SECRET:-legal-jwt-super-secret-key-development-only}"
    secretKey: "${SECRET_KEY:-legal-app-secret-key-development}"
    encryptionKey: "${ENCRYPTION_KEY:-legal-32-char-encryption-dev-key-12}"
    
  frontend:
    apiBaseUrl: "http://legal-backend-api.application.svc.cluster.local:8000"
    
  analytics:
    gaTrackingId: "GA-DEVELOPMENT-ID"
    enableAnalytics: false
EOF

echo "✅ values.yaml updated with .env values!"
echo "📄 Backup created: values.yaml.backup"
