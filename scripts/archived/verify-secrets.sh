# 🔐 Secrets Verification Script
# ==============================

echo "🔍 Verifying Secrets Deployment Status"
echo "======================================"

# Check External Secrets Operator
echo "📊 External Secrets Operator Status:"
kubectl get deployment setup-secrets-external-secrets -n secrets-management

echo ""
echo "🏪 Secret Stores Status:"
kubectl get secretstore -A

echo ""
echo "🔐 External Secrets Status:"
kubectl get externalsecrets -A

echo ""
echo "📦 Generated Application Secrets:"
echo "Backend secrets:"
kubectl get secret legal-backend-secret -n application -o jsonpath='{.data}' | jq -r 'keys[]' 2>/dev/null || echo "Secret not yet created"

echo "Frontend secrets:"  
kubectl get secret legal-frontend-secret -n application -o jsonpath='{.data}' | jq -r 'keys[]' 2>/dev/null || echo "Secret not yet created"

echo "Celery Worker secrets:"
kubectl get secret legal-celery-worker-secret -n application -o jsonpath='{.data}' | jq -r 'keys[]' 2>/dev/null || echo "Secret not yet created"

echo ""
echo "🗄️ Base Secrets in secrets-management namespace:"
kubectl get secrets -n secrets-management --field-selector type=Opaque

echo ""
echo "📋 Secret Reconciliation Status:"
kubectl get externalsecrets -A -o custom-columns="NAMESPACE:.metadata.namespace,NAME:.metadata.name,STATUS:.status.conditions[0].reason,READY:.status.conditions[0].status"
