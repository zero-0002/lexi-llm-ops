#!/bin/bash
# Legal Retrieval System - Docker Build Script
# ============================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Default parameters
SERVICE="all"
TAG="latest"
REGISTRY="legal-retrieval"
SKIP_CLEANUP=false
PUSH=false
SHOW_VERBOSE=false

# Help function
show_help() {
    echo "Legal Retrieval System - Docker Build Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -s, --service SERVICE     Service to build: backend, frontend, all (default: all)"
    echo "  -t, --tag TAG            Docker image tag (default: latest)"
    echo "  -r, --registry REGISTRY  Docker registry prefix (default: legal-retrieval)"
    echo "  --skip-cleanup           Skip image cleanup"
    echo "  --push                   Push to registry after build"
    echo "  -v, --verbose            Show verbose output"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                       # Build all services with default settings"
    echo "  $0 -s backend            # Build only backend service"
    echo "  $0 -s frontend -t v1.0   # Build frontend with tag v1.0"
    echo "  $0 --push -v             # Build all, push to registry, verbose output"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--service)
            SERVICE="$2"
            shift 2
            ;;
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        --skip-cleanup)
            SKIP_CLEANUP=true
            shift
            ;;
        --push)
            PUSH=true
            shift
            ;;
        -v|--verbose)
            SHOW_VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate service parameter
if [[ ! "$SERVICE" =~ ^(backend|frontend|all)$ ]]; then
    echo -e "${RED}❌ Invalid service: $SERVICE${NC}"
    echo "Valid services: backend, frontend, all"
    exit 1
fi

echo -e "${GREEN}🐳 LEGAL RETRIEVAL SYSTEM - DOCKER BUILD${NC}"
echo -e "${YELLOW}=========================================${NC}"

# Check if Docker is available
if ! docker --version >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not available!${NC}"
    echo -e "${YELLOW}Please install Docker and make sure it's running${NC}"
    exit 1
fi

# Check if docker daemon is running
if ! docker ps >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker daemon is not running!${NC}"
    echo -e "${YELLOW}Please start Docker daemon${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is available and running${NC}"

# Build configuration using associative arrays
declare -A backend_config=(
    [name]="Backend API & Celery Worker"
    [context]="./src/app"
    [dockerfile]="Dockerfile"
    [image]="$REGISTRY/backend"
    [platforms]="linux/amd64,linux/arm64"
)

declare -A frontend_config=(
    [name]="Frontend Web Application"
    [context]="./src/legal-chatbot-fe"
    [dockerfile]="Dockerfile"
    [image]="$REGISTRY/frontend"
    [platforms]="linux/amd64,linux/arm64"
)

# Function to build a service
build_service() {
    local service_name="$1"
    local -n config_ref=$2
    
    echo -e "\n${CYAN}🔨 Building: ${config_ref[name]}${NC}"
    echo -e "${WHITE}===============================================${NC}"
    
    local image_full_name="${config_ref[image]}:$TAG"
    
    echo -e "  ${WHITE}📦 Image: $image_full_name${NC}"
    echo -e "  ${WHITE}📂 Context: ${config_ref[context]}${NC}"
    echo -e "  ${WHITE}📄 Dockerfile: ${config_ref[dockerfile]}${NC}"
    
    # Check if context directory exists
    if [[ ! -d "${config_ref[context]}" ]]; then
        echo -e "  ${RED}❌ Context directory not found: ${config_ref[context]}${NC}"
        return 1
    fi
    
    # Check if Dockerfile exists
    local dockerfile_path="${config_ref[context]}/${config_ref[dockerfile]}"
    if [[ ! -f "$dockerfile_path" ]]; then
        echo -e "  ${RED}❌ Dockerfile not found: $dockerfile_path${NC}"
        return 1
    fi
    
    echo -e "  ${WHITE}🚀 Starting build...${NC}"
    
    # Build command
    local build_args=(
        "build"
        "--tag" "$image_full_name"
        "--file" "$dockerfile_path"
    )
    
    if [[ "$SHOW_VERBOSE" == "true" ]]; then
        build_args+=("--progress=plain")
    fi
    
    # Add build arguments for different services
    case "$service_name" in
        "backend")
            build_args+=(
                "--build-arg" "BUILDKIT_INLINE_CACHE=1"
                "--build-arg" "PYTHON_VERSION=3.11"
            )
            ;;
        "frontend")
            build_args+=(
                "--build-arg" "NODE_VERSION=18"
                "--build-arg" "NGINX_VERSION=1.25"
            )
            ;;
    esac
    
    # Add context at the end
    build_args+=("${config_ref[context]}")
    
    if [[ "$SHOW_VERBOSE" == "true" ]]; then
        echo -e "  ${GRAY}🔍 Build command: docker ${build_args[*]}${NC}"
    fi
    
    # Execute build
    if docker "${build_args[@]}"; then
        echo -e "  ${GREEN}✅ Build successful!${NC}"
        
        # Show image info
        local image_info=$(docker images "$image_full_name" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}")
        echo -e "  ${BLUE}📊 Image Info:${NC}"
        echo -e "     ${GRAY}$image_info${NC}"
        
        return 0
    else
        echo -e "  ${RED}❌ Build failed!${NC}"
        return 1
    fi
}

# Function to push a service
push_service() {
    local service_name="$1"
    local -n config_ref=$2
    
    if [[ "$PUSH" != "true" ]]; then
        return 0
    fi
    
    local image_full_name="${config_ref[image]}:$TAG"
    
    echo -e "\n${CYAN}📤 Pushing: ${config_ref[name]}${NC}"
    echo -e "  ${WHITE}📦 Image: $image_full_name${NC}"
    
    if docker push "$image_full_name"; then
        echo -e "  ${GREEN}✅ Push successful!${NC}"
        return 0
    else
        echo -e "  ${RED}❌ Push failed!${NC}"
        return 1
    fi
}

# Function to clean up dangling images
clean_images() {
    if [[ "$SKIP_CLEANUP" == "true" ]]; then
        return
    fi
    
    echo -e "\n${CYAN}🧹 Cleaning up dangling images...${NC}"
    
    local dangling_images=$(docker images -f "dangling=true" -q)
    if [[ -n "$dangling_images" ]]; then
        if docker rmi $dangling_images >/dev/null 2>&1; then
            echo -e "  ${GREEN}✅ Cleanup completed${NC}"
        else
            echo -e "  ${YELLOW}⚠️ Cleanup warning: Some images could not be removed${NC}"
        fi
    else
        echo -e "  ${BLUE}ℹ️ No dangling images to clean${NC}"
    fi
}

# Main build process
start_time=$(date +%s)
declare -A build_results

# Determine services to build
if [[ "$SERVICE" == "all" ]]; then
    services_to_build=("backend" "frontend")
else
    services_to_build=("$SERVICE")
fi

echo -e "\n${CYAN}🎯 Building services: ${services_to_build[*]}${NC}"
echo -e "${WHITE}🏷️ Tag: $TAG${NC}"
echo -e "${WHITE}🏪 Registry: $REGISTRY${NC}"

# Build each service
for service_name in "${services_to_build[@]}"; do
    case "$service_name" in
        "backend")
            if build_service "$service_name" backend_config; then
                build_results["$service_name"]=true
                if ! push_service "$service_name" backend_config && [[ "$PUSH" == "true" ]]; then
                    build_results["$service_name"]=false
                fi
            else
                build_results["$service_name"]=false
            fi
            ;;
        "frontend")
            if build_service "$service_name" frontend_config; then
                build_results["$service_name"]=true
                if ! push_service "$service_name" frontend_config && [[ "$PUSH" == "true" ]]; then
                    build_results["$service_name"]=false
                fi
            else
                build_results["$service_name"]=false
            fi
            ;;
        *)
            echo -e "\n${RED}❌ Unknown service: $service_name${NC}"
            build_results["$service_name"]=false
            ;;
    esac
done

# Cleanup
clean_images

# Summary
end_time=$(date +%s)
duration=$((end_time - start_time))
minutes=$((duration / 60))
seconds=$((duration % 60))

echo -e "\n${GREEN}🎉 BUILD SUMMARY${NC}"
echo -e "${YELLOW}================${NC}"

echo -e "  ${WHITE}⏱️ Total Duration: ${minutes}m ${seconds}s${NC}"
echo -e "  ${WHITE}🏷️ Tag: $TAG${NC}"

success_count=0
total_count=0
for service_name in "${services_to_build[@]}"; do
    total_count=$((total_count + 1))
    if [[ "${build_results[$service_name]}" == "true" ]]; then
        echo -e "  ${GREEN}✅ SUCCESS $service_name${NC}"
        success_count=$((success_count + 1))
    else
        echo -e "  ${RED}❌ FAILED $service_name${NC}"
    fi
done

# Final status
if [[ $success_count -eq $total_count ]]; then
    echo -e "\n${GREEN}🎊 All builds completed successfully!${NC}"
    
    echo -e "\n${CYAN}🚀 Next Steps:${NC}"
    echo -e "  ${WHITE}1. Test images: docker-compose up${NC}"
    echo -e "  ${WHITE}2. Load to Kind: kind load docker-image $REGISTRY/backend:$TAG${NC}"
    echo -e "  ${WHITE}3. Deploy to K8s: ./scripts/deploy-pipeline.sh${NC}"
    
elif [[ $success_count -gt 0 ]]; then
    echo -e "\n${YELLOW}⚠️ Partial success: $success_count/$total_count builds completed${NC}"
    echo -e "${WHITE}Check the errors above and retry failed builds${NC}"
else
    echo -e "\n${RED}❌ All builds failed!${NC}"
    echo -e "${WHITE}Check Docker setup and Dockerfiles${NC}"
    exit 1
fi

echo -e "\n${CYAN}🔍 Available Commands:${NC}"
echo -e "  ${WHITE}📋 List images: docker images | grep $REGISTRY${NC}"
echo -e "  ${WHITE}🧪 Test backend: docker run --rm -p 8000:8000 $REGISTRY/backend:$TAG${NC}"
echo -e "  ${WHITE}🌐 Test frontend: docker run --rm -p 3000:80 $REGISTRY/frontend:$TAG${NC}"
echo -e "  ${WHITE}🗑️ Remove images: docker rmi $REGISTRY/backend:$TAG $REGISTRY/frontend:$TAG${NC}"
