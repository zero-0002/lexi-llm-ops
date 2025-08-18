#!/bin/bash
# 🔐 Create ONLY sensitive secrets - Clean approach
# =================================================
# Chỉ tạo sensitive data, non-secret env sẽ đặt trong chart values

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

NAMESPACE_APP="application"

echo -e "${BLUE}🔐 Creating ONLY sensitive secrets${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""
echo -e "${YELLOW}📋 Strategy: Tách biệt secrets vs config${NC}"
echo "   🔐 Sensitive data → Kubernetes Secrets (script này)"
echo "   📦 Non-secret config → Chart values.yaml"
echo ""

# Load .env if exists
if [ -f ".env" ]; then
    echo "📄 Loading .env..."
    set -a
    source .env
    set +a
    echo -e "${GREEN}✅ .env loaded${NC}"
else
    echo -e "${YELLOW}⚠️  .env not found, using dev defaults${NC}"
fi

# Create namespace
echo -e "${YELLOW}🏗️  Creating namespace...${NC}"
kubectl create namespace $NAMESPACE_APP --dry-run=client -o yaml | kubectl apply -f -
echo -e "${GREEN}✅ Namespace: $NAMESPACE_APP${NC}"

echo ""
echo -e "${YELLOW}🔐 Creating sensitive secrets...${NC}"

# Single shared secret containing all sensitive data
kubectl create secret generic legal-secrets \
    --from-literal=MONGO_PASSWORD="${MONGO_PASSWORD:-mongodb-dev-pass}" \
    --from-literal=REDIS_PASSWORD="${REDIS_PASSWORD:-redis-dev-pass}" \
    --from-literal=OPENAI_API_KEY="${OPENAI_API_KEY:-sk-fake-key-for-development}" \
    --from-literal=JWT_SECRET="${JWT_SECRET:-jwt-dev-secret-key}" \
    --from-literal=SECRET_KEY="${SECRET_KEY:-django-dev-secret-key}" \
    --from-literal=NEXTAUTH_SECRET="${NEXTAUTH_SECRET:-nextauth-dev-secret}" \
    --from-literal=SENTRY_DSN="${SENTRY_DSN:-}" \
    -n $NAMESPACE_APP \
    --dry-run=client -o yaml | kubectl apply -f -

echo -e "${GREEN}✅ Secret created: legal-secrets${NC}"

# Verification
echo ""
echo -e "${BLUE}🔍 Verification:${NC}"
echo "📊 Secret keys:"
kubectl get secret legal-secrets -n $NAMESPACE_APP -o jsonpath='{.data}' | jq -r 'keys[]' | sed 's/^/  - /'

echo ""
echo -e "${BLUE}📋 Usage trong Helm charts:${NC}"
echo "envFrom:"
echo "  - secretRef:"
echo "      name: legal-secrets"

echo ""
echo -e "${GREEN}🎊 Sensitive secrets ready!${NC}"
echo -e "${YELLOW}📝 Next: Đặt non-secret envs vào chart values.yaml${NC}"
