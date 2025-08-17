#!/bin/bash
# Legal Retrieval System - Docker Build Script
# ============================================

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
BUILD_CONTEXT="pw$(pwd)"

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

log_step() {
    echo -e "${CYAN}[$(date +'%Y-%m-%d %H:%M:%S')] 🚀${NC} $1"
}

# Function to check Docker environment
check_docker() {
    log_step "Checking Docker environment..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! docker ps &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    log_success "Docker environment is ready"
}

# Function to build backend image
build_backend() {
    log_step "Building backend Docker image..."
    
    local image_name="${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/backend:${IMAGE_TAG}"
    
    log "Building image: $image_name"
    log "Build context: $BUILD_CONTEXT/src/app"
    
    # Check if Dockerfile exists
    if [ ! -f "src/app/Dockerfile" ]; then
        log_error "Backend Dockerfile not found: src/app/Dockerfile"
        exit 1
    fi
    
    # Build the image
    docker build \
        --tag "$image_name" \
        --file src/app/Dockerfile \
        --build-arg PYTHON_VERSION=3.11 \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        --build-arg BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        --build-arg VCS_REF="$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" \
        --build-arg VERSION="$IMAGE_TAG" \
        --progress=plain \
        src/app/
    
    if [ $? -eq 0 ]; then
        log_success "Backend image built successfully"
        
        # Show image info
        local image_size=$(docker images "$image_name" --format "{{.Size}}")
        log "Image size: $image_size"
        
        return 0
    else
        log_error "Failed to build backend image"
        return 1
    fi
}

# Function to build frontend image
build_frontend() {
    log_step "Building frontend Docker image..."
    
    local image_name="${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/frontend:${IMAGE_TAG}"
    
    log "Building image: $image_name"
    log "Build context: $BUILD_CONTEXT/src/legal-chatbot-fe"
    
    # Check if Dockerfile exists
    if [ ! -f "src/legal-chatbot-fe/Dockerfile" ]; then
        log_error "Frontend Dockerfile not found: src/legal-chatbot-fe/Dockerfile"
        exit 1
    fi
    
    # Build the image
    docker build \
        --tag "$image_name" \
        --file src/legal-chatbot-fe/Dockerfile \
        --build-arg NODE_VERSION=18 \
        --build-arg NGINX_VERSION=1.25 \
        --build-arg BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        --build-arg VCS_REF="$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" \
        --build-arg VERSION="$IMAGE_TAG" \
        --progress=plain \
        src/legal-chatbot-fe/
    
    if [ $? -eq 0 ]; then
        log_success "Frontend image built successfully"
        
        # Show image info
        local image_size=$(docker images "$image_name" --format "{{.Size}}")
        log "Image size: $image_size"
        
        return 0
    else
        log_error "Failed to build frontend image"
        return 1
    fi
}

# Function to test images
test_images() {
    log_step "Testing built images..."
    
    local backend_image="${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/backend:${IMAGE_TAG}"
    local frontend_image="${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/frontend:${IMAGE_TAG}"
    
    # Test backend image
    log "Testing backend image..."
    if docker run --rm --entrypoint="" "$backend_image" python --version; then
        log_success "Backend image test passed"
    else
        log_error "Backend image test failed"
        return 1
    fi
    
    # Test frontend image
    log "Testing frontend image..."
    if docker run --rm --entrypoint="" "$frontend_image" nginx -v; then
        log_success "Frontend image test passed"
    else
        log_error "Frontend image test failed"
        return 1
    fi
    
    return 0
}

# Function to cleanup dangling images
cleanup_images() {
    log_step "Cleaning up dangling images..."
    
    local dangling_images=$(docker images -f "dangling=true" -q)
    
    if [ -n "$dangling_images" ]; then
        docker rmi $dangling_images
        log_success "Dangling images cleaned up"
    else
        log "No dangling images to clean up"
    fi
}

# Function to show built images
show_images() {
    log_step "Built images summary..."
    
    echo -e "\n${CYAN}Built Images:${NC}"
    docker images | grep "$DOCKER_NAMESPACE" | grep "$IMAGE_TAG"
    
    echo -e "\n${CYAN}Image Details:${NC}"
    local backend_image="${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/backend:${IMAGE_TAG}"
    local frontend_image="${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/frontend:${IMAGE_TAG}"
    
    if docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" | grep -E "(backend|frontend)" | grep "$IMAGE_TAG"; then
        echo ""
    fi
    
    echo -e "${CYAN}Usage Examples:${NC}"
    echo "  Backend API: docker run --rm -p 8000:8000 $backend_image api"
    echo "  Celery Worker: docker run --rm $backend_image worker"
    echo "  Frontend: docker run --rm -p 3000:80 $frontend_image"
}

# Main function
main() {
    echo -e "${GREEN}"
    echo "🐳 Legal Retrieval System - Docker Build"
    echo "========================================="
    echo -e "${NC}"
    
    # Load environment if available
    if [ -f ".env" ]; then
        log "Loading environment variables..."
        set -a
        source .env
        set +a
    fi
    
    # Show configuration
    echo -e "${CYAN}Build Configuration:${NC}"
    echo "  Registry: $DOCKER_REGISTRY"
    echo "  Namespace: $DOCKER_NAMESPACE"
    echo "  Tag: $IMAGE_TAG"
    echo "  Context: $BUILD_CONTEXT"
    echo ""
    
    # Execute build steps
    check_docker
    
    local build_errors=0
    
    # Build backend
    if ! build_backend; then
        build_errors=$((build_errors + 1))
    fi
    
    # Build frontend
    if ! build_frontend; then
        build_errors=$((build_errors + 1))
    fi
    
    # Test images if builds succeeded
    if [ $build_errors -eq 0 ]; then
        if ! test_images; then
            build_errors=$((build_errors + 1))
        fi
    fi
    
    # Cleanup
    cleanup_images
    
    # Show results
    show_images
    
    # Summary
    if [ $build_errors -eq 0 ]; then
        echo -e "\n${GREEN}🎉 All images built successfully!${NC}"
        echo -e "${CYAN}Next steps:${NC}"
        echo "  1. Push to registry: ./push-images.sh"
        echo "  2. Update Helm values: ./update-helm-values.sh"
        echo "  3. Deploy to Kubernetes: ./deploy-pipeline.sh"
    else
        echo -e "\n${RED}❌ Build completed with $build_errors error(s)${NC}"
        exit 1
    fi
}

# Handle arguments
case "${1:-all}" in
    "backend")
        check_docker
        build_backend
        ;;
    "frontend")
        check_docker
        build_frontend
        ;;
    "test")
        test_images
        ;;
    "clean")
        cleanup_images
        ;;
    "all")
        main
        ;;
    *)
        echo "Usage: $0 {backend|frontend|test|clean|all}"
        echo ""
        echo "Commands:"
        echo "  backend  - Build backend image only"
        echo "  frontend - Build frontend image only"
        echo "  test     - Test built images"
        echo "  clean    - Clean up dangling images"
        echo "  all      - Build all images (default)"
        exit 1
        ;;
esac
