#!/bin/bash
# 🚀 Complete Legal-Retrieval Deployment - Correct Approach
# ========================================================

set -e

echo "🏁 Starting Complete Legal-Retrieval Deployment"
echo "=============================================="

# Check if required tools are available
echo "🔍 Pre-flight Checks"
echo "==================="

for tool in kubectl helm helmfile; do
    if ! command -v $tool &> /dev/null; then
        echo "❌ $tool is not installed or not in PATH"
        exit 1
    fi
done

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster"
    echo "Please ensure your kubeconfig is set up correctly"
    exit 1
fi

echo "✅ All tools available and cluster accessible"

echo ""
echo "🔐 Step 1: Create Development Secrets from .env.secrets"
echo "======================================================"
./create-dev-secrets.sh

echo ""
echo "📦 Step 2: Deploy ArgoCD via existing Helmfile"
echo "=============================================="

# Create ArgoCD namespace
if kubectl get namespace argocd &> /dev/null; then
    echo "✅ ArgoCD namespace already exists"
else
    echo "📦 Creating ArgoCD namespace..."
    kubectl create namespace argocd
fi

# Check if ArgoCD is already installed
if kubectl get deployment argocd-server -n argocd &> /dev/null; then
    echo "✅ ArgoCD is already installed"
else
    echo "📦 Installing ArgoCD via existing Helmfile..."
    cd ../helm/charts/argocd
    
    # Verify helmfile exists
    if [ ! -f "helmfile.yaml" ]; then
        echo "❌ helmfile.yaml not found in helm/charts/argocd/"
        exit 1
    fi
    
    echo "🔧 Using ArgoCD Helmfile configuration:"
    echo "   Chart: argocd/argo-cd version 7.3.6"
    echo "   Values: argocd-values.yaml"
    echo "   Namespace: argocd"
    
    # Add repo and deploy
    helm repo add argocd https://argoproj.github.io/argo-helm || true
    helm repo update
    
    # Deploy via helmfile
    helmfile sync
    
    echo "✅ ArgoCD deployed successfully via Helmfile"
    cd ../scripts
fi

echo ""
echo "🔧 Step 3: Configure ArgoCD Helmfile Plugin"
echo "==========================================="
kubectl apply -f ../argocd-manifests/cmp-helmfile-plugin.yaml

echo "⏳ Waiting for ArgoCD components to restart with plugin..."
sleep 30

echo ""
echo "🚀 Step 4: Deploy Root App-of-Apps (GitOps Phase)"
echo "================================================="
kubectl apply -f ../argocd-manifests/root-app.yaml

echo ""
echo "⏳ Step 5: Wait for ArgoCD Auto-Sync"
echo "===================================="
echo "ArgoCD will automatically deploy applications in sync-wave order:"
echo "  Wave -2: External Secrets (setup-secrets)"
echo "  Wave -1: Databases (mongo, redis, qdrant)"
echo "  Wave  0: Applications (backend, frontend)"
echo "  Wave  1: Monitoring (prometheus, loki, promtail)"

echo ""
echo "⏳ Waiting 90 seconds for initial sync..."
sleep 90

echo ""
echo "🔍 Step 6: Check Deployment Status"
echo "==================================="
echo ""
echo "📋 ArgoCD Applications:"
kubectl get applications -n argocd -o wide || echo "⚠️ No applications found yet"

echo ""
echo "📋 All Pods Status:"
kubectl get pods -A | grep -E "(legal-|argocd|qdrant|mongo|redis)" || echo "⚠️ No application pods found yet"

echo ""
echo "🔧 ArgoCD Access Information:"
echo "=============================================="
echo "🌐 Access ArgoCD UI:"
echo "   kubectl port-forward svc/argocd-server -n argocd 8080:443"
echo "   Open: https://localhost:8080"
echo ""
echo "🔑 Get ArgoCD admin password:"
echo "   kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath='{.data.password}' | base64 -d"
echo ""
echo "✅ Deployment Complete!"
echo "======================="
echo "🎯 Architecture:"
echo "   ⚡ ArgoCD: Bootstrap deployment (outside GitOps)"
echo "   📦 Applications: Managed by ArgoCD (GitOps)"
echo "   🔧 Plugin: Helmfile CMP for template generation"
echo ""
echo "Next steps:"
echo "   1. Access ArgoCD UI to monitor application sync"
echo "   2. All applications managed via Git changes"
echo "   3. ArgoCD itself managed manually (correct approach)"
