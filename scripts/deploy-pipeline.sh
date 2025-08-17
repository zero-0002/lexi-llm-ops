#!/bin/bash
# Legal Retrieval System - Complete Deployment Pipeline
# ====================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
DOCKER_REGISTRY="${DOCKER_REGISTRY:-docker.io}"
DOCKER_NAMESPACE="${DOCKER_NAMESPACE:-legalretrieval}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
PROJECT_NAME="legal-retrieval"

# Namespaces
DATA_NAMESPACE="data-service"
APP_NAMESPACE="application"

# Functions for logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌${NC} $1"
}

log_step() {
    echo -e "${CYAN}[$(date +'%Y-%m-%d %H:%M:%S')] 🚀${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    log_step "Checking prerequisites..."
    
    local required_tools=("docker" "kubectl" "helm" "helmfile")
    local missing_tools=()
    
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        else
            log_success "$tool is available"
        fi
    done
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log "Please install missing tools and try again"
        exit 1
    fi
    
    # Check Docker daemon
    if ! docker ps &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    # Check Kubernetes cluster
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Kubernetes cluster is not accessible"
        exit 1
    fi
    
    log_success "All prerequisites satisfied"
}

# Function to build Docker images
build_docker_images() {
    log_step "Building Docker images..."
    
    # Build backend image
    log "Building backend image..."
    docker build \
        -t "${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/backend:${IMAGE_TAG}" \
        -f src/app/Dockerfile \
        --build-arg PYTHON_VERSION=3.11 \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        src/app/
    
    if [ $? -eq 0 ]; then
        log_success "Backend image built successfully"
    else
        log_error "Failed to build backend image"
        exit 1
    fi
    
    # Build frontend image
    log "Building frontend image..."
    docker build \
        -t "${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/frontend:${IMAGE_TAG}" \
        -f src/legal-chatbot-fe/Dockerfile \
        --build-arg NODE_VERSION=18 \
        --build-arg NGINX_VERSION=1.25 \
        src/legal-chatbot-fe/
    
    if [ $? -eq 0 ]; then
        log_success "Frontend image built successfully"
    else
        log_error "Failed to build frontend image"
        exit 1
    fi
    
    # Show built images
    log "Built images:"
    docker images | grep "${DOCKER_NAMESPACE}" | grep "${IMAGE_TAG}"
}

# Function to push images to DockerHub
push_to_dockerhub() {
    log_step "Pushing images to DockerHub..."
    
    # Login to DockerHub if credentials are provided
    if [ -n "$DOCKERHUB_USERNAME" ] && [ -n "$DOCKERHUB_PASSWORD" ]; then
        log "Logging into DockerHub..."
        echo "$DOCKERHUB_PASSWORD" | docker login --username "$DOCKERHUB_USERNAME" --password-stdin
    else
        log_warning "DockerHub credentials not provided, assuming already logged in"
    fi
    
    # Push backend image
    log "Pushing backend image..."
    docker push "${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/backend:${IMAGE_TAG}"
    
    if [ $? -eq 0 ]; then
        log_success "Backend image pushed successfully"
    else
        log_error "Failed to push backend image"
        exit 1
    fi
    
    # Push frontend image
    log "Pushing frontend image..."
    docker push "${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/frontend:${IMAGE_TAG}"
    
    if [ $? -eq 0 ]; then
        log_success "Frontend image pushed successfully"
    else
        log_error "Failed to push frontend image"
        exit 1
    fi
    
    log_success "All images pushed to DockerHub"
}

# Function to update Helm values with new image paths
update_helm_values() {
    log_step "Updating Helm values with new image paths..."
    
    # Update backend-api values
    log "Updating backend-api values..."
    sed -i "s|repository:.*|repository: ${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/backend|g" helm/values/backend-api.yaml
    sed -i "s|tag:.*|tag: ${IMAGE_TAG}|g" helm/values/backend-api.yaml
    sed -i "s|pullPolicy:.*|pullPolicy: Always|g" helm/values/backend-api.yaml
    
    # Update celery-worker values
    log "Updating celery-worker values..."
    sed -i "s|repository:.*|repository: ${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/backend|g" helm/values/celery-worker.yaml
    sed -i "s|tag:.*|tag: ${IMAGE_TAG}|g" helm/values/celery-worker.yaml
    sed -i "s|pullPolicy:.*|pullPolicy: Always|g" helm/values/celery-worker.yaml
    
    # Update frontend values
    log "Updating frontend values..."
    sed -i "s|repository:.*|repository: ${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/frontend|g" helm/values/frontend.yaml
    sed -i "s|tag:.*|tag: ${IMAGE_TAG}|g" helm/values/frontend.yaml
    sed -i "s|pullPolicy:.*|pullPolicy: Always|g" helm/values/frontend.yaml
    
    log_success "Helm values updated successfully"
}

# Function to create namespaces
create_namespaces() {
    log_step "Creating namespaces..."
    
    # Create data-service namespace
    kubectl create namespace "$DATA_NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    log_success "Namespace '$DATA_NAMESPACE' created/updated"
    
    # Create application namespace
    kubectl create namespace "$APP_NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    log_success "Namespace '$APP_NAMESPACE' created/updated"
}

# Function to inject secrets from environment variables
inject_secrets() {
    log_step "Injecting secrets into namespaces..."
    
    # Create secret for data services
    log "Creating secrets for data-service namespace..."
    kubectl create secret generic mongodb-secret \
        --from-literal=mongodb-root-username="${MONGODB_ROOT_USERNAME:-admin}" \
        --from-literal=mongodb-root-password="${MONGODB_ROOT_PASSWORD:-password123}" \
        --from-literal=mongodb-username="${MONGODB_USERNAME:-legal_user}" \
        --from-literal=mongodb-password="${MONGODB_PASSWORD:-legal_pass}" \
        --from-literal=mongodb-database="${MONGODB_DATABASE:-legal_retrieval}" \
        --namespace="$DATA_NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    kubectl create secret generic redis-secret \
        --from-literal=redis-password="${REDIS_PASSWORD:-redis123}" \
        --namespace="$DATA_NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Create secret for application services
    log "Creating secrets for application namespace..."
    kubectl create secret generic api-secrets \
        --from-literal=secret-key="${SECRET_KEY:-$(openssl rand -base64 32)}" \
        --from-literal=google-api-key="${GOOGLE_API_KEY:-}" \
        --from-literal=openai-api-key="${OPENAI_API_KEY:-}" \
        --namespace="$APP_NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    kubectl create secret generic database-secrets \
        --from-literal=mongodb-url="${MONGODB_URL:-mongodb://admin:password123@mongodb.$DATA_NAMESPACE.svc.cluster.local:27017/legal_retrieval?authSource=admin}" \
        --from-literal=redis-url="${REDIS_URL:-redis://:redis123@redis.$DATA_NAMESPACE.svc.cluster.local:6379/0}" \
        --from-literal=qdrant-url="${QDRANT_URL:-http://qdrant.$DATA_NAMESPACE.svc.cluster.local:6333}" \
        --from-literal=celery-broker-url="${CELERY_BROKER_URL:-redis://:redis123@redis.$DATA_NAMESPACE.svc.cluster.local:6379/1}" \
        --from-literal=celery-result-backend="${CELERY_RESULT_BACKEND:-redis://:redis123@redis.$DATA_NAMESPACE.svc.cluster.local:6379/2}" \
        --namespace="$APP_NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    log_success "Secrets injected successfully"
}

# Function to deploy databases via Helm
deploy_databases() {
    log_step "Deploying databases via Helm..."
    
    cd helm
    
    # Deploy data services using helmfile
    log "Deploying data services..."
    helmfile -f helmfile.yaml --selector component=data apply
    
    if [ $? -eq 0 ]; then
        log_success "Data services deployed successfully"
    else
        log_error "Failed to deploy data services"
        exit 1
    fi
    
    # Wait for data services to be ready
    log "Waiting for data services to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/mongodb -n "$DATA_NAMESPACE" || true
    kubectl wait --for=condition=available --timeout=300s deployment/redis -n "$DATA_NAMESPACE" || true
    kubectl wait --for=condition=available --timeout=300s deployment/qdrant -n "$DATA_NAMESPACE" || true
    
    cd ..
}

# Function to deploy applications via Helm
deploy_applications() {
    log_step "Deploying applications via Helm..."
    
    cd helm
    
    # Deploy application services using helmfile
    log "Deploying application services..."
    helmfile -f helmfile.yaml --selector component=application apply
    
    if [ $? -eq 0 ]; then
        log_success "Application services deployed successfully"
    else
        log_error "Failed to deploy application services"
        exit 1
    fi
    
    # Wait for application services to be ready
    log "Waiting for application services to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/legal-backend-api -n "$APP_NAMESPACE" || true
    kubectl wait --for=condition=available --timeout=300s deployment/legal-celery-worker -n "$APP_NAMESPACE" || true
    kubectl wait --for=condition=available --timeout=300s deployment/legal-frontend -n "$APP_NAMESPACE" || true
    
    cd ..
}

# Function to show deployment status
show_deployment_status() {
    log_step "Showing deployment status..."
    
    echo -e "\n${PURPLE}=== DATA SERVICES ===${NC}"
    kubectl get pods,svc -n "$DATA_NAMESPACE"
    
    echo -e "\n${PURPLE}=== APPLICATION SERVICES ===${NC}"
    kubectl get pods,svc -n "$APP_NAMESPACE"
    
    echo -e "\n${PURPLE}=== SECRETS ===${NC}"
    kubectl get secrets -n "$DATA_NAMESPACE"
    kubectl get secrets -n "$APP_NAMESPACE"
    
    echo -e "\n${PURPLE}=== ACCESS COMMANDS ===${NC}"
    echo -e "${CYAN}Frontend:${NC} kubectl port-forward svc/legal-frontend 3000:80 -n $APP_NAMESPACE"
    echo -e "${CYAN}Backend API:${NC} kubectl port-forward svc/legal-backend-api-api 8000:8000 -n $APP_NAMESPACE"
}

# Main execution function
main() {
    echo -e "${GREEN}"
    echo "🚀 Legal Retrieval System - Complete Deployment Pipeline"
    echo "========================================================="
    echo -e "${NC}"
    
    # Load environment variables if .env file exists
    if [ -f ".env" ]; then
        log "Loading environment variables from .env file..."
        set -a
        source .env
        set +a
    fi
    
    # Display configuration
    echo -e "\n${CYAN}Configuration:${NC}"
    echo "  Docker Registry: $DOCKER_REGISTRY"
    echo "  Docker Namespace: $DOCKER_NAMESPACE"
    echo "  Image Tag: $IMAGE_TAG"
    echo "  Data Namespace: $DATA_NAMESPACE"
    echo "  App Namespace: $APP_NAMESPACE"
    echo ""
    
    # Execute deployment steps
    check_prerequisites
    build_docker_images
    push_to_dockerhub
    update_helm_values
    create_namespaces
    inject_secrets
    deploy_databases
    deploy_applications
    show_deployment_status
    
    echo -e "\n${GREEN}🎉 Deployment completed successfully!${NC}"
    echo -e "${CYAN}Your Legal Retrieval System is now running on Kubernetes!${NC}"
}

# Handle script arguments
case "${1:-all}" in
    "build")
        check_prerequisites
        build_docker_images
        ;;
    "push")
        push_to_dockerhub
        ;;
    "helm")
        update_helm_values
        ;;
    "secrets")
        create_namespaces
        inject_secrets
        ;;
    "db")
        deploy_databases
        ;;
    "app")
        deploy_applications
        ;;
    "status")
        show_deployment_status
        ;;
    "all")
        main
        ;;
    *)
        echo "Usage: $0 {build|push|helm|secrets|db|app|status|all}"
        echo ""
        echo "Commands:"
        echo "  build   - Build Docker images only"
        echo "  push    - Push images to DockerHub only"
        echo "  helm    - Update Helm values only"
        echo "  secrets - Create namespaces and inject secrets only"
        echo "  db      - Deploy databases only"
        echo "  app     - Deploy applications only"
        echo "  status  - Show deployment status only"
        echo "  all     - Execute full deployment pipeline (default)"
        exit 1
        ;;
esac
