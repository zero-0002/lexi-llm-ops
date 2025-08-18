#!/bin/bash
# Script để validate setup-secrets chart và secrets

echo "🔍 Validating setup-secrets chart and secrets..."
echo "=================================================="

# 1. Validate chart
echo "📋 1. Validating Helm chart..."
helm lint helm/charts/setup-secrets
if [ $? -eq 0 ]; then
    echo "✅ Chart validation passed"
else
    echo "❌ Chart validation failed"
    exit 1
fi

# 2. Check if secrets exist
echo ""
echo "📋 2. Checking if secrets exist..."
kubectl get secrets -n application -o name | grep legal-
if [ $? -eq 0 ]; then
    echo "✅ Secrets exist"
else
    echo "❌ Secrets not found"
    exit 1
fi

# 3. Validate secret contents
echo ""
echo "📋 3. Validating secret contents..."

# Check backend secret
echo "   🔍 Backend secret:"
MONGO_PASS=$(kubectl get secret legal-backend-secret -n application -o jsonpath='{.data.MONGO_PASSWORD}' | base64 -d)
OPENAI_KEY=$(kubectl get secret legal-backend-secret -n application -o jsonpath='{.data.OPENAI_API_KEY}' | base64 -d)
JWT_SECRET=$(kubectl get secret legal-backend-secret -n application -o jsonpath='{.data.JWT_SECRET}' | base64 -d)

if [[ -n "$MONGO_PASS" && -n "$OPENAI_KEY" && -n "$JWT_SECRET" ]]; then
    echo "      ✅ MONGO_PASSWORD: ${MONGO_PASS}"
    echo "      ✅ OPENAI_API_KEY: ${OPENAI_KEY:0:20}..."
    echo "      ✅ JWT_SECRET: ${JWT_SECRET}"
else
    echo "      ❌ Missing required fields"
    exit 1
fi

# Check frontend secret
echo "   🔍 Frontend secret:"
API_URL=$(kubectl get secret legal-frontend-secret -n application -o jsonpath='{.data.REACT_APP_API_BASE_URL}' | base64 -d)
if [[ -n "$API_URL" ]]; then
    echo "      ✅ REACT_APP_API_BASE_URL: ${API_URL}"
else
    echo "      ❌ Missing API_BASE_URL"
    exit 1
fi

# Check celery secret
echo "   🔍 Celery worker secret:"
CELERY_PASS=$(kubectl get secret legal-celery-worker-secret -n application -o jsonpath='{.data.CELERY_BROKER_PASSWORD}' | base64 -d)
if [[ -n "$CELERY_PASS" ]]; then
    echo "      ✅ CELERY_BROKER_PASSWORD: ${CELERY_PASS}"
else
    echo "      ❌ Missing CELERY_BROKER_PASSWORD"
    exit 1
fi

# 4. Test envFrom functionality
echo ""
echo "📋 4. Testing envFrom functionality..."

# Create test pod
kubectl apply -f - << 'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: envfrom-test-pod
  namespace: application
spec:
  containers:
  - name: test
    image: busybox
    command: ["/bin/sh", "-c"]
    args: ["env | grep -E '(MONGO|OPENAI|JWT|REACT_APP)' | sort; sleep 10"]
    envFrom:
    - secretRef:
        name: legal-backend-secret
    - secretRef:
        name: legal-frontend-secret
  restartPolicy: Never
EOF

# Wait and check logs
sleep 5
ENV_VARS=$(kubectl logs envfrom-test-pod -n application 2>/dev/null | wc -l)
if [ "$ENV_VARS" -gt 5 ]; then
    echo "✅ envFrom working - found $ENV_VARS environment variables"
    kubectl logs envfrom-test-pod -n application | head -5
else
    echo "❌ envFrom test failed"
fi

# Cleanup test pod
kubectl delete pod envfrom-test-pod -n application --ignore-not-found

echo ""
echo "🎉 Validation completed successfully!"
echo ""
echo "📝 Usage in your deployments:"
echo "   envFrom:"
echo "   - secretRef:"
echo "       name: legal-backend-secret      # For backend"
echo "       name: legal-frontend-secret     # For frontend"
echo "       name: legal-celery-worker-secret # For celery worker"
