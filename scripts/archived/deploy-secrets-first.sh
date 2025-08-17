#!/bin/bash
# 🔐 Legal Retrieval System - Secrets-First Deployment Guide
# =======================================================

echo "🚀 Legal Retrieval System - Secrets-First Deployment"
echo "===================================================="

# Step 1: Verify Prerequisites
echo ""
echo "📋 Step 1: Prerequisites Check"
echo "-----------------------------"

# Check if kubectl is configured
if ! kubectl cluster-info >/dev/null 2>&1; then
    echo "❌ ERROR: kubectl is not configured or cluster is not accessible"
    exit 1
else
    echo "✅ Kubernetes cluster accessible"
fi

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
    echo "❌ ERROR: Helm is not installed"
    exit 1
else
    echo "✅ Helm is installed: $(helm version --short)"
fi

# Check if ArgoCD is installed
if ! kubectl get namespace argocd >/dev/null 2>&1; then
    echo "⚠️  WARNING: ArgoCD namespace not found. Installing ArgoCD first..."
    
    # Install ArgoCD
    kubectl create namespace argocd
    kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
    
    # Wait for ArgoCD to be ready
    echo "⏳ Waiting for ArgoCD to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n argocd
    
    echo "✅ ArgoCD installed successfully"
else
    echo "✅ ArgoCD namespace exists"
fi

echo ""
echo "🔐 Step 2: Deploy External Secrets System (Sync Wave -2)"
echo "--------------------------------------------------------"

# Deploy External Secrets Operator first
echo "📦 Deploying External Secrets Operator..."
kubectl apply -f argocd-manifests/apps/setup-secrets.yaml

# Wait for External Secrets Operator to be ready
echo "⏳ Waiting for External Secrets Operator deployment..."
kubectl wait --for=condition=available --timeout=300s deployment/setup-secrets-external-secrets -n secrets-management 2>/dev/null || {
    echo "⏳ Still waiting for External Secrets Operator..."
    sleep 30
}

# Check if base secrets were created
echo "🔍 Verifying base secrets creation..."
kubectl get secrets -n secrets-management
if [ $? -eq 0 ]; then
    echo "✅ Base secrets created successfully"
else
    echo "⚠️  Base secrets creation in progress..."
fi

echo ""
echo "🗄️ Step 3: Deploy Database Services (Sync Wave -1)"  
echo "---------------------------------------------------"

# Deploy databases
echo "📦 Deploying MongoDB..."
kubectl apply -f argocd-manifests/apps/mongo.yaml

echo "📦 Deploying Redis..."
kubectl apply -f argocd-manifests/apps/redis.yaml

echo "📦 Deploying Qdrant..."
kubectl apply -f argocd-manifests/apps/qdrant.yaml

# Wait for databases to be ready
echo "⏳ Waiting for database services to be ready..."
sleep 60

echo ""
echo "📊 Step 4: Deploy Monitoring Stack (Sync Wave 0)"
echo "------------------------------------------------"

# Deploy monitoring
echo "📦 Deploying Prometheus Stack..."
kubectl apply -f argocd-manifests/apps/prometheus-stack.yaml

echo "📦 Deploying Loki..."
kubectl apply -f argocd-manifests/apps/loki.yaml

echo ""
echo "🚀 Step 5: Deploy Application Services (Sync Wave 0)"
echo "----------------------------------------------------"

# Deploy applications
echo "📦 Deploying Backend API..."
kubectl apply -f argocd-manifests/apps/application-backend.yaml

echo "📦 Deploying Frontend..."  
kubectl apply -f argocd-manifests/apps/application-frontend.yaml

echo ""
echo "📋 Step 6: Deploy Log Aggregation (Sync Wave 1)"
echo "-----------------------------------------------"

# Deploy promtail last
echo "📦 Deploying Promtail..."
kubectl apply -f argocd-manifests/apps/promtail.yaml

echo ""
echo "🔍 Step 7: Verification"
echo "----------------------"

echo "📊 Checking ArgoCD Applications status..."
kubectl get applications -n argocd

echo ""
echo "🔐 Checking External Secrets status..."
kubectl get externalsecrets -A

echo ""
echo "📦 Checking deployed secrets..."
kubectl get secrets -n application | grep legal-

echo ""
echo "🎉 Deployment completed!"
echo "======================="
echo ""
echo "📝 Next Steps:"
echo "1. Access ArgoCD UI: kubectl port-forward svc/argocd-server -n argocd 8080:443"
echo "2. Get ArgoCD admin password: kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath=\"{.data.password}\" | base64 -d"
echo "3. Monitor deployments: kubectl get pods -A"
echo ""
