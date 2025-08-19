#!/bin/bash
# 🚀 Quick Development Deployment
# ===============================

set -e

echo "⚡ Quick Legal-Retrieval Development Setup"
echo "=========================================="

cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Pre-flight checks
print_step "🔍 Pre-flight Checks"
for tool in kubectl helm helmfile; do
    if ! command -v $tool &> /dev/null; then
        print_error "$tool not found. Please install $tool first."
        exit 1
    fi
done

if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to Kubernetes cluster."
    print_warning "Please ensure your kubeconfig is set up correctly"
    exit 1
fi

print_success "All tools available and cluster accessible"

# Step 1: Create secrets
print_step "🔐 Step 1: Setting up secrets..."
./create-dev-secrets.sh

# Step 2: Install ArgoCD via existing Helmfile
print_step "⚙️ Step 2: Installing ArgoCD via Helmfile..."

if kubectl get namespace argocd &> /dev/null; then
    print_success "ArgoCD namespace exists"
else
    print_step "Creating ArgoCD namespace..."
    kubectl create namespace argocd
fi

# Check if ArgoCD is already installed
if kubectl get deployment argocd-server -n argocd &> /dev/null; then
    print_success "ArgoCD already installed"
else
    print_step "Installing ArgoCD via existing Helmfile (this may take a few minutes)..."
    cd ../helm/charts/argocd
    
    # Verify helmfile.yaml exists
    if [ ! -f "helmfile.yaml" ]; then
        print_error "helmfile.yaml not found in helm/charts/argocd/"
        exit 1
    fi
    
    # Verify argocd-values.yaml exists
    if [ ! -f "argocd-values.yaml" ]; then
        print_error "argocd-values.yaml not found in helm/charts/argocd/"
        exit 1
    fi
    
    print_step "Using existing ArgoCD helmfile configuration..."
    print_step "Chart: argocd/argo-cd version 7.3.6"
    
    # Add ArgoCD repo if not exists
    helm repo add argocd https://argoproj.github.io/argo-helm || true
    helm repo update
    
    # Deploy using helmfile
    helmfile sync
    
    print_success "ArgoCD installed via Helmfile"
    cd - # Return to scripts directory
fi

# Step 3: Configure Helmfile plugin with proper path
print_step "🔧 Step 3: Configuring Helmfile plugin..."

# Verify the ConfigMap file exists in the correct location
CONFIGMAP_FILE="../helm/charts/argocd/cmp-helmfile-plugin.yaml"
if [ ! -f "$CONFIGMAP_FILE" ]; then
    print_error "ConfigMap file not found: $CONFIGMAP_FILE"
    print_warning "Expected location: helm/charts/argocd/cmp-helmfile-plugin.yaml"
    exit 1
fi

print_step "✅ Found ConfigMap file: $CONFIGMAP_FILE"

# Validate ConfigMap structure
if grep -q "kind: ConfigMap" "$CONFIGMAP_FILE" && grep -q "name: cmp-helmfile-plugin" "$CONFIGMAP_FILE"; then
    print_success "ConfigMap structure validated"
else
    print_error "Invalid ConfigMap structure in $CONFIGMAP_FILE"
    exit 1
fi

# Apply ConfigMap
kubectl apply -f "$CONFIGMAP_FILE"

# Wait for ArgoCD to be ready and restart repo-server to pick up new plugin
print_step "Waiting for ArgoCD to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n argocd
kubectl wait --for=condition=available --timeout=300s deployment/argocd-repo-server -n argocd

print_step "Restarting ArgoCD repo-server to load new plugin..."
kubectl rollout restart deployment/argocd-repo-server -n argocd
kubectl rollout status deployment/argocd-repo-server -n argocd

print_success "Helmfile plugin configured and ArgoCD restarted"

# Step 3: Deploy root app
print_step "🚀 Step 4: Deploying applications..."
kubectl apply -f ../argocd-manifests/root-app.yaml

# Step 4: Deploy monitoring separately (optional for dev)
read -p "Deploy monitoring stack (Prometheus/Grafana/Loki)? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_step "📊 Step 4b: Deploying monitoring stack..."
    if kubectl apply -f ../argocd-manifests/monitoring-app.yaml; then
        print_success "Monitoring application deployed"
    else
        print_warning "Monitoring deployment failed (non-critical for development)"
    fi
else
    print_step "Skipping monitoring deployment for faster dev setup"
fi

# Step 5: Quick status check
print_step "📊 Step 5: Checking deployment status..."
sleep 30

echo ""
print_success "Deployment initiated! 🎉"
echo ""
echo "📋 ArgoCD Applications Status:"
kubectl get applications -n argocd 2>/dev/null || echo "  (Applications are being created...)"

echo ""
echo "🔧 Access ArgoCD UI:"
echo "   kubectl port-forward svc/argocd-server -n argocd 8080:443"
echo "   URL: https://localhost:8080"
echo ""
echo "🔑 Get admin password:"
echo "   kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath='{.data.password}' | base64 -d && echo"

echo ""
print_step "🎯 Next Steps:"
echo "   1. Access ArgoCD UI to monitor sync progress"
echo "   2. Wait for all applications to sync (may take 5-10 minutes)"
echo "   3. Check pods: kubectl get pods -A | grep legal-"
echo ""
print_step "🎯 Deployment Architecture:"
echo "   ⚡ ArgoCD: Bootstrap deployment (outside GitOps)"
echo "   📦 Applications: Managed by ArgoCD via Helmfile"
echo "   🔄 GitOps: All app changes via Git commits"
echo ""
print_success "Development environment deployment started! 🚀"
