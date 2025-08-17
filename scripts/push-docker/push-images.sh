#!/bin/bash
# Legal Retrieval System - Docker Push Script
# ===========================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
DOCKER_REGISTRY="${DOCKER_REGISTRY:-docker.io}"
DOCKER_NAMESPACE="${DOCKER_NAMESPACE:-legalretrieval}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

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

# Function to check Docker login
check_docker_login() {
    log_step "Checking Docker authentication..."
    
    # Check if already logged in
    if docker info | grep -q "Username:"; then
        local username=$(docker info | grep "Username:" | awk '{print $2}')
        log_success "Already logged in as: $username"
        return 0
    fi
    
    # Try to login with environment variables
    if [ -n "$DOCKERHUB_USERNAME" ] && [ -n "$DOCKERHUB_PASSWORD" ]; then
        log "Logging in with provided credentials..."
        echo "$DOCKERHUB_PASSWORD" | docker login --username "$DOCKERHUB_USERNAME" --password-stdin
        
        if [ $? -eq 0 ]; then
            log_success "Logged in successfully as: $DOCKERHUB_USERNAME"
            return 0
        else
            log_error "Failed to login with provided credentials"
            return 1
        fi
    fi
    
    # Try to login with Docker token
    if [ -n "$DOCKERHUB_TOKEN" ]; then
        log "Logging in with access token..."
        echo "$DOCKERHUB_TOKEN" | docker login --username "$DOCKERHUB_USERNAME" --password-stdin
        
        if [ $? -eq 0 ]; then
            log_success "Logged in successfully with token"
            return 0
        else
            log_error "Failed to login with access token"
            return 1
        fi
    fi
    
    # Interactive login
    log_warning "No credentials provided, attempting interactive login..."
    docker login
    
    if [ $? -eq 0 ]; then
        log_success "Interactive login successful"
        return 0
    else
        log_error "Interactive login failed"
        return 1
    fi
}

# Function to check if image exists locally
check_image_exists() {
    local image_name="$1"
    
    if docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "^$image_name$"; then
        return 0
    else
        return 1
    fi
}

# Function to push single image
push_image() {
    local image_name="$1"
    local image_type="$2"
    
    log_step "Pushing $image_type image..."
    
    # Check if image exists locally
    if ! check_image_exists "$image_name"; then
        log_error "Image not found locally: $image_name"
        log "Please build the image first: ./build-images.sh"
        return 1
    fi
    
    # Get image size for logging
    local image_size=$(docker images "$image_name" --format "{{.Size}}")
    log "Image: $image_name ($image_size)"
    
    # Push the image
    log "Pushing to registry..."
    docker push "$image_name"
    
    if [ $? -eq 0 ]; then
        log_success "$image_type image pushed successfully"
        
        # Verify the push by trying to pull digest
        local digest=$(docker images --digests "$image_name" --format "{{.Digest}}")
        if [ -n "$digest" ] && [ "$digest" != "<none>" ]; then
            log "Digest: $digest"
        fi
        
        return 0
    else
        log_error "Failed to push $image_type image"
        return 1
    fi
}

# Function to push backend image
push_backend() {
    local image_name="${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/backend:${IMAGE_TAG}"
    push_image "$image_name" "backend"
}

# Function to push frontend image
push_frontend() {
    local image_name="${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/frontend:${IMAGE_TAG}"
    push_image "$image_name" "frontend"
}

# Function to create additional tags
create_additional_tags() {
    log_step "Creating additional tags..."
    
    local backend_image="${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/backend:${IMAGE_TAG}"
    local frontend_image="${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/frontend:${IMAGE_TAG}"
    
    # Create 'latest' tag if not already latest
    if [ "$IMAGE_TAG" != "latest" ]; then
        log "Creating 'latest' tags..."
        
        docker tag "$backend_image" "${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/backend:latest"
        docker tag "$frontend_image" "${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/frontend:latest"
        
        # Push latest tags
        docker push "${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/backend:latest"
        docker push "${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/frontend:latest"
        
        log_success "Latest tags created and pushed"
    fi
    
    # Create date-based tag
    local date_tag=$(date +%Y%m%d)
    log "Creating date-based tags: $date_tag"
    
    docker tag "$backend_image" "${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/backend:$date_tag"
    docker tag "$frontend_image" "${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/frontend:$date_tag"
    
    # Push date tags
    docker push "${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/backend:$date_tag"
    docker push "${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/frontend:$date_tag"
    
    log_success "Date-based tags created and pushed"
}

# Function to verify pushed images
verify_pushed_images() {
    log_step "Verifying pushed images..."
    
    local backend_image="${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/backend:${IMAGE_TAG}"
    local frontend_image="${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/frontend:${IMAGE_TAG}"
    
    # Try to pull the images to verify they're accessible
    log "Verifying backend image..."
    if docker pull "$backend_image" >/dev/null 2>&1; then
        log_success "Backend image verified on registry"
    else
        log_warning "Could not verify backend image on registry"
    fi
    
    log "Verifying frontend image..."
    if docker pull "$frontend_image" >/dev/null 2>&1; then
        log_success "Frontend image verified on registry"
    else
        log_warning "Could not verify frontend image on registry"
    fi
}

# Function to show pushed images info
show_pushed_images() {
    log_step "Pushed images summary..."
    
    local backend_image="${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/backend:${IMAGE_TAG}"
    local frontend_image="${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/frontend:${IMAGE_TAG}"
    
    echo -e "\n${CYAN}Pushed Images:${NC}"
    echo "  Backend:  $backend_image"
    echo "  Frontend: $frontend_image"
    
    if [ "$IMAGE_TAG" != "latest" ]; then
        echo "  Backend:  ${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/backend:latest"
        echo "  Frontend: ${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/frontend:latest"
    fi
    
    local date_tag=$(date +%Y%m%d)
    echo "  Backend:  ${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/backend:$date_tag"
    echo "  Frontend: ${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/frontend:$date_tag"
    
    echo -e "\n${CYAN}Registry URLs:${NC}"
    echo "  Backend:  https://hub.docker.com/r/${DOCKER_NAMESPACE}/backend"
    echo "  Frontend: https://hub.docker.com/r/${DOCKER_NAMESPACE}/frontend"
    
    echo -e "\n${CYAN}Pull Commands:${NC}"
    echo "  docker pull $backend_image"
    echo "  docker pull $frontend_image"
}

# Main function
main() {
    echo -e "${GREEN}"
    echo "📤 Legal Retrieval System - Docker Push"
    echo "========================================"
    echo -e "${NC}"
    
    # Load environment if available
    if [ -f ".env" ]; then
        log "Loading environment variables..."
        set -a
        source .env
        set +a
    fi
    
    # Show configuration
    echo -e "${CYAN}Push Configuration:${NC}"
    echo "  Registry: $DOCKER_REGISTRY"
    echo "  Namespace: $DOCKER_NAMESPACE"
    echo "  Tag: $IMAGE_TAG"
    echo ""
    
    # Execute push steps
    local push_errors=0
    
    # Check Docker login
    if ! check_docker_login; then
        log_error "Docker authentication failed"
        exit 1
    fi
    
    # Push backend
    if ! push_backend; then
        push_errors=$((push_errors + 1))
    fi
    
    # Push frontend
    if ! push_frontend; then
        push_errors=$((push_errors + 1))
    fi
    
    # Create additional tags if main pushes succeeded
    if [ $push_errors -eq 0 ]; then
        create_additional_tags
        verify_pushed_images
    fi
    
    # Show results
    show_pushed_images
    
    # Summary
    if [ $push_errors -eq 0 ]; then
        echo -e "\n${GREEN}🎉 All images pushed successfully!${NC}"
        echo -e "${CYAN}Next steps:${NC}"
        echo "  1. Update Helm values: ./update-helm-values.sh"
        echo "  2. Deploy to Kubernetes: ./deploy-pipeline.sh"
        echo "  3. Or continue with full pipeline: ./deploy-pipeline.sh"
    else
        echo -e "\n${RED}❌ Push completed with $push_errors error(s)${NC}"
        exit 1
    fi
}

# Handle arguments
case "${1:-all}" in
    "backend")
        check_docker_login
        push_backend
        ;;
    "frontend")
        check_docker_login
        push_frontend
        ;;
    "verify")
        verify_pushed_images
        ;;
    "tags")
        create_additional_tags
        ;;
    "all")
        main
        ;;
    *)
        echo "Usage: $0 {backend|frontend|verify|tags|all}"
        echo ""
        echo "Commands:"
        echo "  backend  - Push backend image only"
        echo "  frontend - Push frontend image only"
        echo "  verify   - Verify pushed images"
        echo "  tags     - Create additional tags"
        echo "  all      - Push all images (default)"
        exit 1
        ;;
esac
