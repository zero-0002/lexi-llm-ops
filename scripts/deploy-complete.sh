#!/bin/bash
#!/bin/bash
# � Legal Retrieval System - Complete Deployment Fix
# ====================================================

echo "🔄 Legal Retrieval System - Complete Deployment Fix"
echo "===================================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

echo ""
print_info "Step 1: Force refresh all applications to ensure proper sync"
echo "============================================================="

# Force refresh all applications to resync
APPS=(
    "application-backend"
    "application-frontend" 
    "legal-mongodb"
    "legal-qdrant"
    "legal-redis"
    "prometheus-stack"
    "loki"
    "promtail"
    "setup-secrets"
)

for app in "${APPS[@]}"; do
    print_info "Refreshing application: $app"
    kubectl patch application $app -n argocd -p '{"operation":{"initiatedBy":{"username":"admin"},"sync":{}}}' --type=merge
    sleep 2
done

echo ""
print_info "Step 2: Wait for applications to sync (2 minutes)"
echo "=================================================="
print_warning "Waiting for applications to sync and create resources..."

for i in {1..24}; do
    echo -n "."
    sleep 5
    
    # Check every 30 seconds
    if [ $((i % 6)) -eq 0 ]; then
        echo ""
        SYNCED_COUNT=$(kubectl get applications -n argocd --no-headers | grep Synced | wc -l)
        TOTAL_COUNT=$(kubectl get applications -n argocd --no-headers | wc -l)
        print_info "Progress: $SYNCED_COUNT/$TOTAL_COUNT applications synced"
        
        # Check if we have pods
        PODS_COUNT=$(kubectl get pods -A | grep -E "(legal-|mongo|redis|qdrant|prometheus|grafana)" | wc -l)
        print_info "Pods created: $PODS_COUNT"
    fi
done

echo ""
echo ""
print_info "Step 3: Deployment Status Check"
echo "================================"

echo ""
echo "📊 ArgoCD Applications Status:"
kubectl get applications -n argocd

echo ""
echo "🏢 Pods by Namespace:"
echo "====================="

for ns in application data-service platform-services monitoring; do
    if kubectl get namespace $ns &>/dev/null; then
        POD_COUNT=$(kubectl get pods -n $ns --no-headers 2>/dev/null | wc -l)
        if [ "$POD_COUNT" -gt 0 ]; then
            print_success "Namespace $ns: $POD_COUNT pods"
            kubectl get pods -n $ns
            echo ""
        else
            print_warning "Namespace $ns: No pods"
        fi
    else
        print_warning "Namespace $ns: Not found"
    fi
done

echo ""
echo "🎯 Legal Application Components:"
echo "================================"
LEGAL_PODS=$(kubectl get pods -A | grep legal- 2>/dev/null || echo "")
if [ -n "$LEGAL_PODS" ]; then
    print_success "Legal components found:"
    echo "$LEGAL_PODS"
else
    print_warning "No legal components found yet"
fi

echo ""
echo "📈 Infrastructure Components:"
echo "============================="
kubectl get pods -A | grep -E "(redis|mongo|qdrant|prometheus|grafana|loki|promtail)" 2>/dev/null || print_warning "No infrastructure pods found"

echo ""
print_info "Step 4: Application Health Check"
echo "================================="

# Check for any applications that are not healthy
UNHEALTHY=$(kubectl get applications -n argocd --no-headers | grep -v "Synced.*Healthy" || echo "")
if [ -n "$UNHEALTHY" ]; then
    print_warning "Applications needing attention:"
    echo "$UNHEALTHY"
    echo ""
    print_info "Suggested fixes:"
    echo "1. kubectl describe application <app-name> -n argocd"
    echo "2. kubectl logs -n argocd deployment/argocd-application-controller | grep <app-name>"
    echo "3. kubectl patch application <app-name> -n argocd -p '{"operation":{"sync":{}}}' --type=merge"
else
    print_success "All applications are healthy!"
fi

echo ""
print_info "Step 5: Final Summary"
echo "===================="

TOTAL_APPS=$(kubectl get applications -n argocd --no-headers | wc -l)
SYNCED_APPS=$(kubectl get applications -n argocd --no-headers | grep Synced | wc -l)
HEALTHY_APPS=$(kubectl get applications -n argocd --no-headers | grep Healthy | wc -l)
TOTAL_PODS=$(kubectl get pods -A --no-headers | wc -l)
RUNNING_PODS=$(kubectl get pods -A --no-headers | grep Running | wc -l)

echo "📊 Deployment Statistics:"
echo "├── Applications: $SYNCED_APPS/$TOTAL_APPS synced"
echo "├── Health Status: $HEALTHY_APPS/$TOTAL_APPS healthy" 
echo "├── Total Pods: $TOTAL_PODS"
echo "└── Running Pods: $RUNNING_PODS"

if [ "$SYNCED_APPS" -eq "$TOTAL_APPS" ] && [ "$HEALTHY_APPS" -eq "$TOTAL_APPS" ]; then
    print_success "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!"
    echo ""
    print_info "Next steps:"
    echo "1. 🌐 Access ArgoCD UI: kubectl port-forward svc/argocd-server -n argocd 8080:443"
    echo "2. 📊 Monitor applications: kubectl get apps -n argocd -w"
    echo "3. 🧪 Test application endpoints once all pods are Running"
elif [ "$SYNCED_APPS" -gt $((TOTAL_APPS * 2 / 3)) ]; then
    print_warning "🔄 DEPLOYMENT MOSTLY SUCCESSFUL"
    echo ""
    print_info "Some applications may need manual attention"
    print_info "Run: kubectl get applications -n argocd"
else
    print_error "🚨 DEPLOYMENT NEEDS ATTENTION"
    echo ""
    print_info "Multiple applications are not synced properly"
    print_info "Check ArgoCD UI or run individual application debugging commands"
fi

echo ""
print_info "Deployment fix completed: $(date)"
echo ""echo ""
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
