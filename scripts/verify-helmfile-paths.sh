#!/bin/bash
# 🔍 Legal-Retrieval Helmfile Path Verification
# ============================================

echo "🔍 Verifying Helmfile Configuration"
echo "==================================="

cd "$(dirname "$0")/../helm"

echo ""
echo "📁 Current working directory:"
pwd

echo ""
echo "🔧 Checking helmfile.yaml existence:"
if [ -f "helmfile.yaml" ]; then
    echo "✅ helmfile.yaml found"
else
    echo "❌ helmfile.yaml not found"
    echo "📂 Available files:"
    ls -la
    exit 1
fi

echo ""
echo "📋 Helmfile releases list:"
helmfile list

echo ""
echo "🔍 Checking ArgoCD configuration:"
helmfile --selector app=argocd list

echo ""
echo "📦 Available releases by labels:"
echo "================================"
for app in argocd setup-secrets legal-backend legal-frontend mongo redis qdrant prometheus-stack loki promtail; do
    echo -n "app=$app: "
    helmfile --selector app=$app list --quiet | wc -l | tr -d ' '
done

echo ""
echo "🧪 Testing ArgoCD Helmfile template generation:"
echo "=============================================="
helmfile --selector app=argocd template --skip-deps | head -20

echo ""
echo "✅ Helmfile path verification complete!"
