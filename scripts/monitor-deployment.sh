#!/bin/bash
# Legal Retrieval System - Deployment Monitoring
# ==============================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Configuration
NAMESPACES=("data-service" "application")
DEPLOYMENTS=("mongodb" "redis" "qdrant" "legal-backend" "legal-celery-worker" "legal-frontend")
CHECK_INTERVAL=5
MAX_WAIT_TIME=300

# Functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️${NC} $1"
}

log_step() {
    echo -e "${CYAN}[$(date +'%Y-%m-%d %H:%M:%S')] 🚀${NC} $1"
}

log_info() {
    echo -e "${PURPLE}[$(date +'%Y-%m-%d %H:%M:%S')] 📊${NC} $1"
}

# Function to check kubectl availability
check_kubectl() {
    if ! command -v kubectl >/dev/null 2>&1; then
        log_error "kubectl is not installed or not in PATH"
        return 1
    fi
    
    if ! kubectl cluster-info >/dev/null 2>&1; then
        log_error "Cannot connect to Kubernetes cluster"
        return 1
    fi
    
    local context=$(kubectl config current-context)
    log_success "Connected to cluster: $context"
    return 0
}

# Function to wait for deployment to be ready
wait_for_deployment() {
    local namespace="$1"
    local deployment="$2"
    local timeout="${3:-$MAX_WAIT_TIME}"
    
    log_step "Waiting for deployment: $deployment in namespace: $namespace"
    
    local start_time=$(date +%s)
    local end_time=$((start_time + timeout))
    
    while [ $(date +%s) -lt $end_time ]; do
        # Check if deployment exists
        if ! kubectl get deployment "$deployment" -n "$namespace" >/dev/null 2>&1; then
            log_warning "Deployment not found: $deployment (waiting...)"
            sleep $CHECK_INTERVAL
            continue
        fi
        
        # Get deployment status
        local ready_replicas=$(kubectl get deployment "$deployment" -n "$namespace" -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
        local desired_replicas=$(kubectl get deployment "$deployment" -n "$namespace" -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "1")
        local available=$(kubectl get deployment "$deployment" -n "$namespace" -o jsonpath='{.status.conditions[?(@.type=="Available")].status}' 2>/dev/null || echo "False")
        
        # Handle empty values
        ready_replicas=${ready_replicas:-0}
        desired_replicas=${desired_replicas:-1}
        
        log_info "Deployment $deployment: $ready_replicas/$desired_replicas ready, Available: $available"
        
        # Check if deployment is ready
        if [ "$ready_replicas" = "$desired_replicas" ] && [ "$available" = "True" ]; then
            local elapsed=$(($(date +%s) - start_time))
            log_success "Deployment ready: $deployment (${elapsed}s)"
            return 0
        fi
        
        sleep $CHECK_INTERVAL
    done
    
    log_error "Timeout waiting for deployment: $deployment"
    return 1
}

# Function to check pod status
check_pod_status() {
    local namespace="$1"
    local deployment="$2"
    
    log_step "Checking pods for deployment: $deployment"
    
    # Get pods for the deployment
    local pods=$(kubectl get pods -n "$namespace" -l app="$deployment" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || true)
    
    if [ -z "$pods" ]; then
        log_warning "No pods found for deployment: $deployment"
        return 1
    fi
    
    local pod_count=0
    local ready_count=0
    
    for pod in $pods; do
        pod_count=$((pod_count + 1))
        
        # Get pod status
        local phase=$(kubectl get pod "$pod" -n "$namespace" -o jsonpath='{.status.phase}' 2>/dev/null || echo "Unknown")
        local ready=$(kubectl get pod "$pod" -n "$namespace" -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "False")
        local restart_count=$(kubectl get pod "$pod" -n "$namespace" -o jsonpath='{.status.containerStatuses[0].restartCount}' 2>/dev/null || echo "0")
        
        if [ "$ready" = "True" ] && [ "$phase" = "Running" ]; then
            ready_count=$((ready_count + 1))
            log_success "Pod ready: $pod (restarts: $restart_count)"
        else
            log_warning "Pod not ready: $pod (phase: $phase, ready: $ready, restarts: $restart_count)"
            
            # Show recent events for problematic pods
            log_info "Recent events for pod: $pod"
            kubectl describe pod "$pod" -n "$namespace" | grep -A 10 "Events:" || true
        fi
    done
    
    log_info "Pods status for $deployment: $ready_count/$pod_count ready"
    
    if [ $ready_count -eq $pod_count ] && [ $pod_count -gt 0 ]; then
        return 0
    else
        return 1
    fi
}

# Function to check service status
check_service_status() {
    local namespace="$1"
    local service="$2"
    
    log_step "Checking service: $service"
    
    if ! kubectl get service "$service" -n "$namespace" >/dev/null 2>&1; then
        log_warning "Service not found: $service"
        return 1
    fi
    
    # Get service details
    local service_type=$(kubectl get service "$service" -n "$namespace" -o jsonpath='{.spec.type}' 2>/dev/null || echo "Unknown")
    local cluster_ip=$(kubectl get service "$service" -n "$namespace" -o jsonpath='{.spec.clusterIP}' 2>/dev/null || echo "None")
    local ports=$(kubectl get service "$service" -n "$namespace" -o jsonpath='{.spec.ports[*].port}' 2>/dev/null || echo "None")
    
    log_success "Service ready: $service (type: $service_type, IP: $cluster_ip, ports: $ports)"
    return 0
}

# Function to test connectivity
test_connectivity() {
    local namespace="$1"
    local service="$2"
    local port="$3"
    
    log_step "Testing connectivity to $service:$port"
    
    # Create a temporary test pod
    local test_pod="connectivity-test-$(date +%s)"
    
    kubectl run "$test_pod" --rm -i --restart=Never --image=busybox:1.35 --namespace="$namespace" -- \
        sh -c "timeout 10 nc -zv $service.$namespace.svc.cluster.local $port" >/dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        log_success "Connectivity test passed: $service:$port"
        return 0
    else
        log_warning "Connectivity test failed: $service:$port"
        return 1
    fi
}

# Function to check namespace resources
check_namespace_resources() {
    local namespace="$1"
    
    log_step "Checking resources in namespace: $namespace"
    
    if ! kubectl get namespace "$namespace" >/dev/null 2>&1; then
        log_error "Namespace not found: $namespace"
        return 1
    fi
    
    echo -e "\n${CYAN}Deployments in $namespace:${NC}"
    kubectl get deployments -n "$namespace" -o wide 2>/dev/null || log_warning "No deployments found"
    
    echo -e "\n${CYAN}Services in $namespace:${NC}"
    kubectl get services -n "$namespace" -o wide 2>/dev/null || log_warning "No services found"
    
    echo -e "\n${CYAN}Pods in $namespace:${NC}"
    kubectl get pods -n "$namespace" -o wide 2>/dev/null || log_warning "No pods found"
    
    echo -e "\n${CYAN}Secrets in $namespace:${NC}"
    kubectl get secrets -n "$namespace" 2>/dev/null || log_warning "No secrets found"
    
    echo -e "\n${CYAN}ConfigMaps in $namespace:${NC}"
    kubectl get configmaps -n "$namespace" 2>/dev/null || log_warning "No configmaps found"
}

# Function to get deployment logs
get_deployment_logs() {
    local namespace="$1"
    local deployment="$2"
    local lines="${3:-50}"
    
    log_step "Getting logs for deployment: $deployment (last $lines lines)"
    
    # Get pods for the deployment
    local pods=$(kubectl get pods -n "$namespace" -l app="$deployment" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || true)
    
    if [ -z "$pods" ]; then
        log_warning "No pods found for deployment: $deployment"
        return 1
    fi
    
    for pod in $pods; do
        echo -e "\n${CYAN}Logs for pod: $pod${NC}"
        kubectl logs "$pod" -n "$namespace" --tail="$lines" --timestamps || log_warning "Could not get logs for pod: $pod"
    done
}

# Function to monitor deployment health
monitor_deployment_health() {
    local namespace="$1"
    local deployment="$2"
    
    log_step "Monitoring health for deployment: $deployment"
    
    # Wait for deployment to be ready
    if ! wait_for_deployment "$namespace" "$deployment"; then
        log_error "Deployment failed to become ready: $deployment"
        get_deployment_logs "$namespace" "$deployment" 20
        return 1
    fi
    
    # Check pod status
    if ! check_pod_status "$namespace" "$deployment"; then
        log_warning "Some pods are not ready for deployment: $deployment"
    fi
    
    # Check service if it exists
    if kubectl get service "$deployment" -n "$namespace" >/dev/null 2>&1; then
        check_service_status "$namespace" "$deployment"
    fi
    
    return 0
}

# Function to run health checks
run_health_checks() {
    log_step "Running comprehensive health checks..."
    
    local total_checks=0
    local passed_checks=0
    
    for namespace in "${NAMESPACES[@]}"; do
        echo -e "\n${CYAN}Health checks for namespace: $namespace${NC}"
        
        # Get all deployments in namespace
        local deployments=$(kubectl get deployments -n "$namespace" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || true)
        
        if [ -z "$deployments" ]; then
            log_warning "No deployments found in namespace: $namespace"
            continue
        fi
        
        for deployment in $deployments; do
            total_checks=$((total_checks + 1))
            
            if monitor_deployment_health "$namespace" "$deployment"; then
                passed_checks=$((passed_checks + 1))
            fi
        done
    done
    
    # Summary
    echo -e "\n${CYAN}Health Check Summary:${NC}"
    echo "  Total Checks: $total_checks"
    echo "  Passed: $passed_checks"
    echo "  Failed: $((total_checks - passed_checks))"
    
    if [ $passed_checks -eq $total_checks ]; then
        log_success "All health checks passed!"
        return 0
    else
        log_warning "Some health checks failed"
        return 1
    fi
}

# Function to show cluster status
show_cluster_status() {
    log_step "Showing cluster status..."
    
    echo -e "\n${CYAN}Cluster Information:${NC}"
    kubectl cluster-info
    
    echo -e "\n${CYAN}Node Status:${NC}"
    kubectl get nodes -o wide
    
    echo -e "\n${CYAN}Namespace Status:${NC}"
    kubectl get namespaces
    
    echo -e "\n${CYAN}Storage Classes:${NC}"
    kubectl get storageclass
    
    echo -e "\n${CYAN}Persistent Volumes:${NC}"
    kubectl get pv
    
    echo -e "\n${CYAN}Top Nodes (CPU/Memory):${NC}"
    kubectl top nodes 2>/dev/null || log_warning "Metrics server not available"
    
    echo -e "\n${CYAN}Top Pods (CPU/Memory):${NC}"
    kubectl top pods --all-namespaces 2>/dev/null || log_warning "Metrics server not available"
}

# Function for continuous monitoring
continuous_monitor() {
    local interval="${1:-30}"
    
    log_step "Starting continuous monitoring (interval: ${interval}s)"
    log "Press Ctrl+C to stop..."
    
    while true; do
        clear
        echo -e "${GREEN}Legal Retrieval System - Live Monitor${NC}"
        echo "========================================"
        echo "$(date)"
        echo ""
        
        run_health_checks
        
        echo -e "\n${CYAN}Next check in ${interval}s...${NC}"
        sleep "$interval"
    done
}

# Function to export monitoring report
export_report() {
    local report_file="monitoring-report-$(date +%Y%m%d_%H%M%S).txt"
    
    log_step "Exporting monitoring report to: $report_file"
    
    {
        echo "Legal Retrieval System - Monitoring Report"
        echo "=========================================="
        echo "Generated: $(date)"
        echo ""
        
        echo "Cluster Information:"
        kubectl cluster-info
        echo ""
        
        for namespace in "${NAMESPACES[@]}"; do
            echo "Namespace: $namespace"
            echo "===================="
            kubectl get all -n "$namespace" -o wide
            echo ""
        done
        
        echo "Events (last 50):"
        kubectl get events --all-namespaces --sort-by='.lastTimestamp' | tail -50
        
    } > "$report_file"
    
    log_success "Report exported: $report_file"
}

# Main function
main() {
    echo -e "${GREEN}"
    echo "📊 Legal Retrieval System - Deployment Monitor"
    echo "=============================================="
    echo -e "${NC}"
    
    # Check prerequisites
    if ! check_kubectl; then
        exit 1
    fi
    
    # Run health checks
    run_health_checks
    
    # Show cluster status
    show_cluster_status
    
    echo -e "\n${GREEN}🎉 Monitoring completed!${NC}"
    echo -e "${CYAN}Available commands:${NC}"
    echo "  ./monitor-deployment.sh health      - Run health checks"
    echo "  ./monitor-deployment.sh watch       - Continuous monitoring"
    echo "  ./monitor-deployment.sh status      - Show cluster status"
    echo "  ./monitor-deployment.sh logs <ns> <deploy> - Get deployment logs"
    echo "  ./monitor-deployment.sh report      - Export monitoring report"
}

# Handle arguments
case "${1:-health}" in
    "health")
        run_health_checks
        ;;
    "watch")
        interval="${2:-30}"
        continuous_monitor "$interval"
        ;;
    "status")
        show_cluster_status
        ;;
    "logs")
        namespace="$2"
        deployment="$3"
        lines="${4:-50}"
        
        if [ -z "$namespace" ] || [ -z "$deployment" ]; then
            log_error "Usage: $0 logs <namespace> <deployment> [lines]"
            exit 1
        fi
        
        get_deployment_logs "$namespace" "$deployment" "$lines"
        ;;
    "check")
        namespace="$2"
        deployment="$3"
        
        if [ -z "$namespace" ] || [ -z "$deployment" ]; then
            log_error "Usage: $0 check <namespace> <deployment>"
            exit 1
        fi
        
        monitor_deployment_health "$namespace" "$deployment"
        ;;
    "namespace")
        namespace="$2"
        
        if [ -z "$namespace" ]; then
            log_error "Usage: $0 namespace <namespace>"
            exit 1
        fi
        
        check_namespace_resources "$namespace"
        ;;
    "report")
        export_report
        ;;
    "all")
        main
        ;;
    *)
        echo "Usage: $0 {health|watch|status|logs|check|namespace|report|all}"
        echo ""
        echo "Commands:"
        echo "  health                          - Run health checks (default)"
        echo "  watch [interval]                - Continuous monitoring"
        echo "  status                          - Show cluster status"
        echo "  logs <namespace> <deployment>   - Get deployment logs"
        echo "  check <namespace> <deployment>  - Check specific deployment"
        echo "  namespace <namespace>           - Check namespace resources"
        echo "  report                          - Export monitoring report"
        echo "  all                             - Full monitoring suite"
        exit 1
        ;;
esac
