#!/bin/bash
# Legal Retrieval System - Kubernetes Secrets Management
# ======================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
NAMESPACES=("data-service" "application")
SECRET_TYPES=("app-secrets" "db-secrets" "registry-secrets")

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

# Function to check if kubectl is available
check_kubectl() {
    if ! command -v kubectl >/dev/null 2>&1; then
        log_error "kubectl is not installed or not in PATH"
        return 1
    fi
    
    # Check if cluster is accessible
    if ! kubectl cluster-info >/dev/null 2>&1; then
        log_error "Cannot connect to Kubernetes cluster"
        return 1
    fi
    
    local context=$(kubectl config current-context)
    log_success "Connected to cluster: $context"
    return 0
}

# Function to create namespace if not exists
create_namespace() {
    local namespace="$1"
    
    if kubectl get namespace "$namespace" >/dev/null 2>&1; then
        log "Namespace exists: $namespace"
    else
        log_step "Creating namespace: $namespace"
        kubectl create namespace "$namespace"
        log_success "Namespace created: $namespace"
    fi
}

# Function to create application secrets
create_app_secrets() {
    local namespace="$1"
    
    log_step "Creating application secrets for namespace: $namespace"
    
    # Load environment variables
    local env_vars=(
        "OPENAI_API_KEY"
        "JWT_SECRET_KEY"
        "CELERY_BROKER_URL"
        "CELERY_RESULT_BACKEND"
        "LOG_LEVEL"
        "API_VERSION"
        "CORS_ORIGINS"
        "MAX_WORKERS"
        "WORKER_TIMEOUT"
    )
    
    # Build kubectl command
    local kubectl_cmd="kubectl create secret generic app-secrets --namespace=$namespace"
    local secret_created=false
    
    for var in "${env_vars[@]}"; do
        if [ -n "${!var}" ]; then
            kubectl_cmd="$kubectl_cmd --from-literal=$var=${!var}"
            secret_created=true
        else
            log_warning "Environment variable not set: $var"
        fi
    done
    
    # Create the secret if we have any data
    if [ "$secret_created" = true ]; then
        # Delete existing secret if it exists
        kubectl delete secret app-secrets --namespace="$namespace" 2>/dev/null || true
        
        # Create new secret
        eval "$kubectl_cmd"
        log_success "Application secrets created in namespace: $namespace"
    else
        log_warning "No application environment variables found"
    fi
}

# Function to create database secrets
create_db_secrets() {
    local namespace="$1"
    
    log_step "Creating database secrets for namespace: $namespace"
    
    # Load database environment variables
    local db_vars=(
        "MONGODB_URI"
        "MONGODB_DATABASE"
        "MONGODB_USERNAME"
        "MONGODB_PASSWORD"
        "REDIS_HOST"
        "REDIS_PORT"
        "REDIS_PASSWORD"
        "QDRANT_HOST"
        "QDRANT_PORT"
        "QDRANT_API_KEY"
    )
    
    # Build kubectl command
    local kubectl_cmd="kubectl create secret generic db-secrets --namespace=$namespace"
    local secret_created=false
    
    for var in "${db_vars[@]}"; do
        if [ -n "${!var}" ]; then
            kubectl_cmd="$kubectl_cmd --from-literal=$var=${!var}"
            secret_created=true
        else
            log_warning "Database environment variable not set: $var"
        fi
    done
    
    # Create the secret if we have any data
    if [ "$secret_created" = true ]; then
        # Delete existing secret if it exists
        kubectl delete secret db-secrets --namespace="$namespace" 2>/dev/null || true
        
        # Create new secret
        eval "$kubectl_cmd"
        log_success "Database secrets created in namespace: $namespace"
    else
        log_warning "No database environment variables found"
    fi
}

# Function to create Docker registry secrets
create_registry_secrets() {
    local namespace="$1"
    
    log_step "Creating registry secrets for namespace: $namespace"
    
    # Check if Docker credentials are available
    if [ -n "$DOCKERHUB_USERNAME" ] && [ -n "$DOCKERHUB_PASSWORD" ]; then
        # Delete existing secret if it exists
        kubectl delete secret registry-secrets --namespace="$namespace" 2>/dev/null || true
        
        # Create Docker registry secret
        kubectl create secret docker-registry registry-secrets \
            --namespace="$namespace" \
            --docker-server=docker.io \
            --docker-username="$DOCKERHUB_USERNAME" \
            --docker-password="$DOCKERHUB_PASSWORD" \
            --docker-email="${DOCKERHUB_EMAIL:-$DOCKERHUB_USERNAME@docker.io}"
        
        log_success "Registry secrets created in namespace: $namespace"
    else
        log_warning "Docker registry credentials not found (DOCKERHUB_USERNAME, DOCKERHUB_PASSWORD)"
    fi
}

# Function to create TLS secrets
create_tls_secrets() {
    local namespace="$1"
    
    log_step "Creating TLS secrets for namespace: $namespace"
    
    # Check if TLS files exist
    local cert_file="certs/tls.crt"
    local key_file="certs/tls.key"
    
    if [ -f "$cert_file" ] && [ -f "$key_file" ]; then
        # Delete existing secret if it exists
        kubectl delete secret tls-secrets --namespace="$namespace" 2>/dev/null || true
        
        # Create TLS secret
        kubectl create secret tls tls-secrets \
            --namespace="$namespace" \
            --cert="$cert_file" \
            --key="$key_file"
        
        log_success "TLS secrets created in namespace: $namespace"
    else
        log_warning "TLS certificate files not found ($cert_file, $key_file)"
    fi
}

# Function to list secrets in namespace
list_secrets() {
    local namespace="$1"
    
    log_step "Listing secrets in namespace: $namespace"
    
    if kubectl get namespace "$namespace" >/dev/null 2>&1; then
        echo -e "\n${CYAN}Secrets in namespace: $namespace${NC}"
        kubectl get secrets --namespace="$namespace" -o wide
    else
        log_warning "Namespace does not exist: $namespace"
    fi
}

# Function to describe secret
describe_secret() {
    local namespace="$1"
    local secret_name="$2"
    
    log_step "Describing secret: $secret_name in namespace: $namespace"
    
    if kubectl get secret "$secret_name" --namespace="$namespace" >/dev/null 2>&1; then
        kubectl describe secret "$secret_name" --namespace="$namespace"
    else
        log_warning "Secret does not exist: $secret_name in namespace: $namespace"
    fi
}

# Function to delete secrets
delete_secrets() {
    local namespace="$1"
    local secret_type="${2:-all}"
    
    log_step "Deleting secrets in namespace: $namespace"
    
    case "$secret_type" in
        "app")
            kubectl delete secret app-secrets --namespace="$namespace" 2>/dev/null || true
            log_success "Application secrets deleted"
            ;;
        "db")
            kubectl delete secret db-secrets --namespace="$namespace" 2>/dev/null || true
            log_success "Database secrets deleted"
            ;;
        "registry")
            kubectl delete secret registry-secrets --namespace="$namespace" 2>/dev/null || true
            log_success "Registry secrets deleted"
            ;;
        "tls")
            kubectl delete secret tls-secrets --namespace="$namespace" 2>/dev/null || true
            log_success "TLS secrets deleted"
            ;;
        "all")
            for secret in "app-secrets" "db-secrets" "registry-secrets" "tls-secrets"; do
                kubectl delete secret "$secret" --namespace="$namespace" 2>/dev/null || true
            done
            log_success "All secrets deleted"
            ;;
        *)
            log_error "Unknown secret type: $secret_type"
            return 1
            ;;
    esac
}

# Function to validate secrets
validate_secrets() {
    local namespace="$1"
    
    log_step "Validating secrets in namespace: $namespace"
    
    local validation_errors=0
    local expected_secrets=("app-secrets" "db-secrets" "registry-secrets")
    
    for secret in "${expected_secrets[@]}"; do
        if kubectl get secret "$secret" --namespace="$namespace" >/dev/null 2>&1; then
            log_success "Secret exists: $secret"
            
            # Check if secret has data
            local data_count=$(kubectl get secret "$secret" --namespace="$namespace" -o jsonpath='{.data}' | jq '. | length' 2>/dev/null || echo "0")
            
            if [ "$data_count" -gt 0 ]; then
                log "Secret has $data_count data entries"
            else
                log_warning "Secret is empty: $secret"
                validation_errors=$((validation_errors + 1))
            fi
        else
            log_error "Secret missing: $secret"
            validation_errors=$((validation_errors + 1))
        fi
    done
    
    return $validation_errors
}

# Function to create all secrets for all namespaces
create_all_secrets() {
    log_step "Creating all secrets for all namespaces..."
    
    for namespace in "${NAMESPACES[@]}"; do
        echo -e "\n${CYAN}Processing namespace: $namespace${NC}"
        
        # Create namespace
        create_namespace "$namespace"
        
        # Create secrets
        create_app_secrets "$namespace"
        create_db_secrets "$namespace"
        create_registry_secrets "$namespace"
        create_tls_secrets "$namespace"
        
        # Validate
        validate_secrets "$namespace"
    done
}

# Function to show secrets summary
show_summary() {
    log_step "Secrets summary..."
    
    for namespace in "${NAMESPACES[@]}"; do
        echo -e "\n${CYAN}Namespace: $namespace${NC}"
        
        if kubectl get namespace "$namespace" >/dev/null 2>&1; then
            kubectl get secrets --namespace="$namespace" --no-headers 2>/dev/null | while read -r line; do
                if [ -n "$line" ]; then
                    local secret_name=$(echo "$line" | awk '{print $1}')
                    local secret_type=$(echo "$line" | awk '{print $2}')
                    local data_count=$(echo "$line" | awk '{print $3}')
                    echo "  ✅ $secret_name ($secret_type) - $data_count keys"
                fi
            done
        else
            echo "  ❌ Namespace does not exist"
        fi
    done
}

# Main function
main() {
    echo -e "${GREEN}"
    echo "🔐 Legal Retrieval System - Kubernetes Secrets"
    echo "=============================================="
    echo -e "${NC}"
    
    # Load environment if available
    if [ -f ".env" ]; then
        log "Loading environment variables..."
        set -a
        source .env
        set +a
    fi
    
    # Check prerequisites
    if ! check_kubectl; then
        exit 1
    fi
    
    # Show configuration
    echo -e "${CYAN}Configuration:${NC}"
    echo "  Namespaces: ${NAMESPACES[*]}"
    echo "  Secret Types: ${SECRET_TYPES[*]}"
    echo ""
    
    # Create all secrets
    create_all_secrets
    
    # Show summary
    show_summary
    
    echo -e "\n${GREEN}🎉 Secrets management completed!${NC}"
    echo -e "${CYAN}Usage in Helm:${NC}"
    echo "  envFrom:"
    echo "    - secretRef:"
    echo "        name: app-secrets"
    echo "    - secretRef:"
    echo "        name: db-secrets"
    echo "  imagePullSecrets:"
    echo "    - name: registry-secrets"
}

# Handle arguments
case "${1:-all}" in
    "create")
        namespace="${2:-all}"
        secret_type="${3:-all}"
        
        if [ "$namespace" = "all" ]; then
            create_all_secrets
        else
            create_namespace "$namespace"
            case "$secret_type" in
                "app") create_app_secrets "$namespace" ;;
                "db") create_db_secrets "$namespace" ;;
                "registry") create_registry_secrets "$namespace" ;;
                "tls") create_tls_secrets "$namespace" ;;
                "all") 
                    create_app_secrets "$namespace"
                    create_db_secrets "$namespace"
                    create_registry_secrets "$namespace"
                    create_tls_secrets "$namespace"
                    ;;
                *) log_error "Unknown secret type: $secret_type"; exit 1 ;;
            esac
        fi
        ;;
    "delete")
        namespace="${2:-all}"
        secret_type="${3:-all}"
        
        if [ "$namespace" = "all" ]; then
            for ns in "${NAMESPACES[@]}"; do
                delete_secrets "$ns" "$secret_type"
            done
        else
            delete_secrets "$namespace" "$secret_type"
        fi
        ;;
    "list")
        namespace="${2:-all}"
        
        if [ "$namespace" = "all" ]; then
            for ns in "${NAMESPACES[@]}"; do
                list_secrets "$ns"
            done
        else
            list_secrets "$namespace"
        fi
        ;;
    "describe")
        namespace="$2"
        secret_name="$3"
        
        if [ -z "$namespace" ] || [ -z "$secret_name" ]; then
            log_error "Usage: $0 describe <namespace> <secret-name>"
            exit 1
        fi
        
        describe_secret "$namespace" "$secret_name"
        ;;
    "validate")
        namespace="${2:-all}"
        
        if [ "$namespace" = "all" ]; then
            for ns in "${NAMESPACES[@]}"; do
                validate_secrets "$ns"
            done
        else
            validate_secrets "$namespace"
        fi
        ;;
    "summary")
        show_summary
        ;;
    "all")
        main
        ;;
    *)
        echo "Usage: $0 {create|delete|list|describe|validate|summary|all} [namespace] [secret-type]"
        echo ""
        echo "Commands:"
        echo "  create [namespace] [secret-type] - Create secrets"
        echo "  delete [namespace] [secret-type] - Delete secrets"
        echo "  list [namespace]                 - List secrets"
        echo "  describe <namespace> <secret>    - Describe specific secret"
        echo "  validate [namespace]             - Validate secrets"
        echo "  summary                          - Show secrets summary"
        echo "  all                             - Create all secrets (default)"
        echo ""
        echo "Namespaces: all, ${NAMESPACES[*]}"
        echo "Secret Types: all, app, db, registry, tls"
        exit 1
        ;;
esac
