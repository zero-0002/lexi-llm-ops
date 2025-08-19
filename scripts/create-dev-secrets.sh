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

# ONLY sensitive values - Non-sensitive configs moved to Helm values.yaml:
# ❌ MONGO_HOST, MONGO_USER, MONGO_DATABASE, MONGO_AUTH_SOURCE → values.yaml
# ❌ CELERY_BROKER_URL, CELERY_RESULT_BACKEND → values.yaml (with IP fallback)
# ❌ Database URLs, Service endpoints → values.yaml
# ✅ Passwords, API keys, secrets → Kubernetes Secrets

# Single shared secret containing ONLY sensitive data
kubectl create secret generic legal-secrets \
    --from-literal=MONGODB_PASSWORD="${MONGODB_PASSWORD:-password123}" \
    --from-literal=REDIS_PASSWORD="${REDIS_PASSWORD:-}" \
    --from-literal=OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
    --from-literal=SERPER_API_KEY="${SERPER_API_KEY:-}" \
    --from-literal=SECRET_KEY="${SECRET_KEY:-dev_secret_key_change_in_production}" \
    --from-literal=JWT_SECRET="${JWT_SECRET:-legal-jwt-super-secret-key-development}" \
    --from-literal=ENCRYPTION_KEY="${ENCRYPTION_KEY:-legal-32-char-encryption-dev-key}" \
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
echo -e "${BLUE}📦 Non-sensitive configs in values.yaml:${NC}"
echo "env:"
echo "  MONGO_HOST: \"legal-mongodb.data-service.svc.cluster.local\""
echo "  MONGO_PORT: \"27017\""
echo "  MONGO_DB: \"legal_database\""
echo "  CELERY_BROKER_URL: \"redis://10.96.203.203:6379/3\""
echo "  REDIS_HOST: \"legal-redis-master.data-service.svc.cluster.local\""

echo ""
echo -e "${GREEN}🎊 Sensitive secrets ready!${NC}"
echo -e "${YELLOW}📝 Next: Đặt non-secret envs vào chart values.yaml${NC}"
