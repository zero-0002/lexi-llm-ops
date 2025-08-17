#!/bin/bash
# 🚀 Legal Retrieval Deployment Status Report
# ===========================================

echo "🚀 Legal Retrieval System - Deployment Status Report"
echo "====================================================="
echo "Generated: $(date)"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo "📊 ARGOCD APPLICATIONS STATUS"
echo "=============================="
echo ""
kubectl get applications -n argocd -o wide
echo ""

echo "🧮 APPLICATION STATISTICS"
echo "========================="
APP_COUNT=$(kubectl get applications -n argocd --no-headers | wc -l)
SYNCED_COUNT=$(kubectl get applications -n argocd --no-headers | grep Synced | wc -l)
UNKNOWN_COUNT=$(kubectl get applications -n argocd --no-headers | grep Unknown | wc -l)
OUTOFSINC_COUNT=$(kubectl get applications -n argocd --no-headers | grep OutOfSync | wc -l)
DEGRADED_COUNT=$(kubectl get applications -n argocd --no-headers | grep Degraded | wc -l)

echo "📈 Total Applications: $APP_COUNT"
echo "├── 🟢 Synced: $SYNCED_COUNT"
echo "├── 🟡 Unknown: $UNKNOWN_COUNT"
echo "├── 🔄 OutOfSync: $OUTOFSINC_COUNT"
echo "└── 🔴 Degraded: $DEGRADED_COUNT"
echo ""

if [ "$SYNCED_COUNT" -eq "$APP_COUNT" ]; then
    print_success "All applications are synced!"
elif [ "$SYNCED_COUNT" -gt 5 ]; then
    print_success "Most applications are synced ($SYNCED_COUNT/$APP_COUNT)"
else
    print_warning "Some applications need attention ($SYNCED_COUNT/$APP_COUNT synced)"
fi
echo ""

echo "🏢 KUBERNETES RESOURCES BY NAMESPACE"
echo "====================================="
echo ""
for ns in argocd application data-service platform-services monitoring secrets-management secrets-store; do
    if kubectl get namespace $ns &>/dev/null; then
        POD_COUNT=$(kubectl get pods -n $ns --no-headers 2>/dev/null | wc -l)
        RUNNING_COUNT=$(kubectl get pods -n $ns --no-headers 2>/dev/null | grep Running | wc -l)
        echo "📦 Namespace: $ns"
        echo "   ├── Pods: $POD_COUNT (Running: $RUNNING_COUNT)"
        
        if [ "$POD_COUNT" -gt 0 ]; then
            echo "   └── Pod Status:"
            kubectl get pods -n $ns --no-headers 2>/dev/null | awk '{print "       " $1 " - " $3}' | head -5
            if [ "$POD_COUNT" -gt 5 ]; then
                echo "       ... and $(($POD_COUNT - 5)) more pods"
            fi
        fi
        echo ""
    else
        echo "📦 Namespace: $ns - NOT FOUND"
        echo ""
    fi
done

echo "🎯 LEGAL RETRIEVAL COMPONENTS"
echo "============================="
echo ""
echo "📋 Legal Application Pods:"
LEGAL_PODS=$(kubectl get pods -A | grep legal- || echo "None found")
if echo "$LEGAL_PODS" | grep -q "legal-"; then
    echo "$LEGAL_PODS"
    print_success "Legal components are deployed!"
else
    print_warning "No legal- pods found yet"
fi
echo ""

echo "💾 DATABASE COMPONENTS"
echo "======================"
echo ""
echo "MongoDB:"
kubectl get pods -A | grep mongo || echo "  No MongoDB pods found"
echo ""
echo "Redis:"
kubectl get pods -A | grep redis || echo "  No Redis pods found"
echo ""
echo "Qdrant:"
kubectl get pods -A | grep qdrant || echo "  No Qdrant pods found"
echo ""

echo "📈 MONITORING STACK"
echo "=================="
echo ""
echo "Prometheus Stack:"
kubectl get pods -n monitoring | grep prometheus || echo "  No Prometheus pods found"
echo ""
echo "Grafana:"
kubectl get pods -n monitoring | grep grafana || echo "  No Grafana pods found"
echo ""
echo "Loki:"
kubectl get pods -n monitoring | grep loki || echo "  No Loki pods found"
echo ""

echo "🔧 TROUBLESHOOTING COMMANDS"
echo "============================"
echo ""
echo "🔍 Check specific application:"
echo "   kubectl describe application <app-name> -n argocd"
echo ""
echo "🔄 Force sync application:"
echo "   kubectl patch application <app-name> -n argocd -p '{\"operation\":{\"sync\":{}}}' --type=merge"
echo ""
echo "📋 Check application logs:"
echo "   kubectl logs -n argocd deployment/argocd-application-controller | grep <app-name>"
echo ""
echo "🔌 Check CMP plugin logs:"
echo "   kubectl logs -n argocd deployment/argocd-repo-server -c cmp-helmfile"
echo ""
echo "🌐 Access ArgoCD UI:"
echo "   kubectl port-forward svc/argocd-server -n argocd 8080:443"
echo "   URL: https://localhost:8080"
echo ""
echo "🔑 Get ArgoCD admin password:"
echo "   kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath='{.data.password}' | base64 -d"
echo ""

if [ "$UNKNOWN_COUNT" -gt 0 ] || [ "$OUTOFSINC_COUNT" -gt 0 ]; then
    echo "⚠️ APPLICATIONS NEEDING ATTENTION"
    echo "================================="
    echo ""
    
    if [ "$UNKNOWN_COUNT" -gt 0 ]; then
        print_warning "Applications with Unknown status:"
        kubectl get applications -n argocd --no-headers | grep Unknown | awk '{print "   " $1}'
    fi
    
    if [ "$OUTOFSINC_COUNT" -gt 0 ]; then
        print_warning "Applications with OutOfSync status:"
        kubectl get applications -n argocd --no-headers | grep OutOfSync | awk '{print "   " $1}'
    fi
    echo ""
    echo "💡 To fix Unknown/OutOfSync applications:"
    echo "   kubectl patch application <app-name> -n argocd -p '{\"operation\":{\"sync\":{}}}' --type=merge"
fi

echo ""
echo "🎯 DEPLOYMENT SUMMARY"
echo "===================="
echo ""
if [ "$SYNCED_COUNT" -ge 7 ]; then
    print_success "✅ Deployment is mostly successful!"
    print_info "Legal Retrieval system is ready for use"
elif [ "$SYNCED_COUNT" -ge 4 ]; then
    print_warning "⚠️ Deployment is partially successful"
    print_info "Some components may need manual intervention"
else
    print_error "❌ Deployment needs attention"
    print_info "Multiple applications are not synced"
fi
echo ""
echo "📅 Next steps:"
echo "1. 🔍 Check ArgoCD UI for detailed status"
echo "2. 🔄 Sync any OutOfSync applications"
echo "3. 📋 Monitor pod startup in relevant namespaces"
echo "4. 🧪 Test application endpoints once pods are Running"
echo ""
print_info "Report completed: $(date)"
