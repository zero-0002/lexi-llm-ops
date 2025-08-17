#!/bin/bash
# 🧪 Test ArgoCD Helmfile Approach
# ===============================

echo "🧪 Testing ArgoCD Helmfile Direct Approach"
echo "=========================================="

cd "$(dirname "$0")/../helm/charts/argocd"

echo ""
echo "📁 Current directory: $(pwd)"
echo ""

echo "🔍 1. File Verification"
echo "======================="
echo "📋 Checking required files:"
echo "├── helmfile.yaml: $([ -f "helmfile.yaml" ] && echo "✅ Found" || echo "❌ Missing")"
echo "├── argocd-values.yaml: $([ -f "argocd-values.yaml" ] && echo "✅ Found" || echo "❌ Missing")"
echo "└── environments/development.yaml: $([ -f "../../environments/development.yaml" ] && echo "✅ Found" || echo "❌ Missing")"

echo ""
echo "🔍 2. Helmfile Configuration Check"
echo "=================================="
if [ -f "helmfile.yaml" ]; then
    echo "📋 Helmfile content:"
    echo "Repository:"
    grep -A 2 "repositories:" helmfile.yaml | head -3
    echo ""
    echo "Release:"
    grep -A 5 "releases:" helmfile.yaml | head -6
    echo ""
    echo "Chart version:"
    grep "version:" helmfile.yaml
else
    echo "❌ helmfile.yaml not found"
    exit 1
fi

echo ""
echo "🔍 3. Helm Repository Test" 
echo "=========================="
echo "📦 Adding ArgoCD repository..."
if helm repo add argocd https://argoproj.github.io/argo-helm; then
    echo "✅ ArgoCD repo added successfully"
    helm repo update
    echo "✅ Repositories updated"
else
    echo "❌ Failed to add ArgoCD repository"
fi

echo ""
echo "🔍 4. Chart Availability Test"
echo "============================="
echo "📋 Checking if ArgoCD chart version 7.3.6 is available..."
if helm search repo argocd/argo-cd --version 7.3.6; then
    echo "✅ ArgoCD chart version 7.3.6 is available"
else
    echo "⚠️ Specific version might not be available, checking latest:"
    helm search repo argocd/argo-cd | head -5
fi

echo ""
echo "🔍 5. Helmfile Dry Run Test"
echo "==========================="
echo "📋 Testing helmfile template generation..."
if command -v helmfile >/dev/null 2>&1; then
    echo "✅ Helmfile is available"
    
    echo ""
    echo "🧪 Dry run - Template generation:"
    if helmfile template --skip-deps | head -20; then
        echo ""
        echo "✅ Template generation successful"
    else
        echo "❌ Template generation failed"
    fi
    
    echo ""
    echo "🧪 Dry run - List releases:"
    helmfile list
    
else
    echo "❌ Helmfile not available for testing"
fi

echo ""
echo "🔍 6. Values File Check"
echo "======================"
if [ -f "argocd-values.yaml" ]; then
    echo "📋 ArgoCD values configuration:"
    echo "Global domain:"
    grep -A 2 "global:" argocd-values.yaml | head -3
    echo ""
    echo "CMP Plugin configuration:"
    if grep -q "extraContainers:" argocd-values.yaml; then
        echo "✅ Found CMP sidecar configuration"
    else
        echo "⚠️ No CMP sidecar found"
    fi
    echo ""
    echo "Tool installation:"
    if grep -q "initContainers:" argocd-values.yaml; then
        echo "✅ Found initContainers for tools"
    else
        echo "⚠️ No tool installation containers found"
    fi
else
    echo "❌ argocd-values.yaml not found"
fi

echo ""
echo "🎯 Comparison: Helmfile vs Direct Helm"
echo "======================================"
echo ""
echo "📊 Approach Comparison:"
echo "┌─────────────────┬──────────────┬─────────────────┐"
echo "│ Aspect          │ Direct Helm  │ Helmfile        │"
echo "├─────────────────┼──────────────┼─────────────────┤"
echo "│ Consistency     │ ⚠️  Manual    │ ✅ Declarative  │"
echo "│ Configuration   │ ❌ Script     │ ✅ YAML Config  │"
echo "│ Environment     │ ❌ Hardcoded  │ ✅ Multi-env    │"
echo "│ GitOps Ready    │ ❌ No         │ ✅ Yes          │"
echo "│ Maintenance     │ ❌ Complex    │ ✅ Simple       │"
echo "└─────────────────┴──────────────┴─────────────────┘"

echo ""
echo "🚀 Recommendation: USE HELMFILE!"
echo "================================"
echo "✅ Benefits:"
echo "  - Consistent with other components"
echo "  - Environment-specific configuration"  
echo "  - Declarative approach"
echo "  - Version controlled"
echo "  - Same tool for all deployments"

echo ""
echo "📝 Updated Deployment Command:"
echo "cd helm/charts/argocd"
echo "helmfile sync"

echo ""
echo "✅ ArgoCD Helmfile Test Complete!"
