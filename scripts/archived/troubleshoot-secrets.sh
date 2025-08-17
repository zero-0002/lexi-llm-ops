#!/bin/bash

# 🔧 Secrets Troubleshooting Guide
# =================================

echo "🔍 Secrets Troubleshooting Diagnostics"
echo "======================================"

echo "1️⃣ Checking External Secrets Operator status..."
kubectl get deployment -n secrets-management

echo ""
echo "2️⃣ Checking Secret Stores..."
kubectl get secretstore -A -o wide

echo ""  
echo "3️⃣ Checking External Secrets and their status..."
kubectl get externalsecrets -A -o wide

echo ""
echo "4️⃣ Checking base secrets in secrets-management namespace..."
kubectl get secrets -n secrets-management

echo ""
echo "5️⃣ Checking application secrets..."
kubectl get secrets -n application | grep legal- || echo "No application secrets found"

echo ""
echo "6️⃣ Checking External Secrets Operator logs..."
echo "Recent operator logs:"
kubectl logs -n secrets-management deployment/setup-secrets-external-secrets --tail=20

echo ""
echo "7️⃣ Checking specific External Secret status..."
kubectl describe externalsecret legal-backend-external-secret -n application 2>/dev/null || echo "Backend external secret not found"

echo ""
echo "🔧 Common Issues and Solutions:"
echo "================================"
echo ""
echo "❌ Issue: External Secrets not reconciling"
echo "✅ Solution: Check RBAC permissions and Secret Store configuration"
echo ""
echo "❌ Issue: Base secrets not found"  
echo "✅ Solution: Run ./scripts/create-dev-secrets.sh to create base secrets"
echo ""
echo "❌ Issue: Applications failing to start"
echo "✅ Solution: Ensure secrets are created before deploying applications"
echo ""
echo "❌ Issue: Secret Store authentication failed"
echo "✅ Solution: Check Service Account and ClusterRole bindings"

echo ""
echo "🚀 Quick Fix Commands:"
echo "====================="
echo ""
echo "# Recreate base secrets:"
echo "./scripts/create-dev-secrets.sh"
echo ""
echo "# Restart External Secrets Operator:"
echo "kubectl rollout restart deployment/setup-secrets-external-secrets -n secrets-management"
echo ""
echo "# Force reconcile External Secrets:"
echo "kubectl annotate externalsecret legal-backend-external-secret -n application force-sync=\$(date +%s)"
echo ""
echo "# Check specific pod logs for secret mount issues:"
echo "kubectl logs -n application deployment/legal-backend-api"
