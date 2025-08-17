#!/bin/bash

# Script để verify ArgoCD applications status
echo "🔍 Verifying ArgoCD Applications..."

echo "📋 Checking ArgoCD applications:"
kubectl get applications -n argocd -o wide

echo ""
echo "🔍 Detailed status for each app:"

APPS=("application-backend" "application-frontend" "legal-mongodb" "legal-redis" "legal-qdrant" "prometheus-stack" "loki" "promtail")

for app in "${APPS[@]}"; do
    echo ""
    echo "📊 Checking $app:"
    kubectl get application $app -n argocd -o jsonpath='{.status.sync.status}' && echo " (Sync Status)"
    kubectl get application $app -n argocd -o jsonpath='{.status.health.status}' && echo " (Health Status)"
    
    # Check if any error messages
    ERROR_MSG=$(kubectl get application $app -n argocd -o jsonpath='{.status.conditions[?(@.type=="ComparisonError")].message}')
    if [ ! -z "$ERROR_MSG" ]; then
        echo "❌ Error: $ERROR_MSG"
    fi
done

echo ""
echo "🔧 Checking ArgoCD repo server logs for plugin issues:"
echo "Recent logs from cmp-helmfile container:"
kubectl logs -n argocd deployment/argocd-repo-server -c cmp-helmfile --tail=20

echo ""
echo "✅ Verification completed!"
