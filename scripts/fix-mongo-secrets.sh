#!/bin/bash
# 🔐 Create secrets with CORRECT MongoDB password (temporary fix)
# =============================================================

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

NAMESPACE_APP="application"

echo -e "${BLUE}🔐 Creating secrets with CORRECT MongoDB password${NC}"
echo -e "${BLUE}================================================${NC}"

# Create namespace
kubectl create namespace $NAMESPACE_APP --dry-run=client -o yaml | kubectl apply -f -

echo -e "${YELLOW}🔐 Creating corrected secrets...${NC}"

# Single shared secret với MongoDB password ĐÚNG từ mongodb.yaml
kubectl create secret generic legal-secrets \
    --from-literal=MONGO_PASSWORD="password123" \
    --from-literal=REDIS_PASSWORD="redis-dev-pass" \
    --from-literal=OPENAI_API_KEY="sk-fake-key-for-development" \
    --from-literal=JWT_SECRET="legal-jwt-super-secret-key-development" \
    --from-literal=SECRET_KEY="django-dev-secret-key" \
    --from-literal=NEXTAUTH_SECRET="nextauth-dev-secret" \
    --from-literal=SENTRY_DSN="" \
    -n $NAMESPACE_APP \
    --dry-run=client -o yaml | kubectl apply -f -

echo -e "${GREEN}✅ Secret created with CORRECT MongoDB password: password123${NC}"

# Verification
echo ""
echo -e "${BLUE}🔍 Verification:${NC}"
echo "📊 Secret keys:"
kubectl get secret legal-secrets -n $NAMESPACE_APP -o jsonpath='{.data}' | jq -r 'keys[]' | sed 's/^/  - /'

echo ""
echo -e "${GREEN}🎊 Secrets fixed! MongoDB password now matches mongodb.yaml${NC}"
