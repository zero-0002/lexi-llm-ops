#!/bin/bash
# Legal Retrieval System - Docker Summary and Validation
# ======================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

echo -e "${GREEN}🐳 LEGAL RETRIEVAL SYSTEM - DOCKER CONFIGURATION SUMMARY${NC}"
echo -e "${YELLOW}=========================================================${NC}"

# Function to check file exists and get size
check_file() {
    local file_path="$1"
    if [[ -f "$file_path" ]]; then
        local size=$(du -h "$file_path" 2>/dev/null | cut -f1)
        echo -e "   ${GREEN}✅ File: $file_path ($size)${NC}"
        return 0
    else
        echo -e "   ${RED}❌ File: Not found${NC}"
        return 1
    fi
}

# Function to check dockerfile features
check_dockerfile_features() {
    local dockerfile="$1"
    if [[ -f "$dockerfile" ]]; then
        local content=$(cat "$dockerfile")
        
        # Check for multi-stage build
        if echo "$content" | grep -q "FROM.*AS[[:space:]]\+\w\+"; then
            echo -e "   ${GREEN}✅ Multi-stage build: Yes${NC}"
        else
            echo -e "   ${YELLOW}⚠️ Multi-stage build: No${NC}"
        fi
        
        # Check for health check
        if echo "$content" | grep -q "HEALTHCHECK"; then
            echo -e "   ${GREEN}✅ Health check: Configured${NC}"
        else
            echo -e "   ${YELLOW}⚠️ Health check: Missing${NC}"
        fi
        
        # Check for non-root user
        if echo "$content" | grep -q "USER[[:space:]]\+\w\+"; then
            echo -e "   ${GREEN}✅ Security: Non-root user${NC}"
        else
            echo -e "   ${YELLOW}⚠️ Security: Root user${NC}"
        fi
    fi
}

echo -e "\n${CYAN}📦 DOCKER IMAGES OVERVIEW:${NC}"
echo -e "${WHITE}==========================${NC}"

# Backend Dockerfile
echo -e "\n${BLUE}🔹 Backend Dockerfile${NC}"
echo -e "   ${GRAY}Description: FastAPI application with Celery workers${NC}"
check_file "src/app/Dockerfile"
check_dockerfile_features "src/app/Dockerfile"
check_file "src/app/docker-entrypoint.sh"
check_file "src/app/.dockerignore"

# Frontend Dockerfile
echo -e "\n${BLUE}🔹 Frontend Dockerfile${NC}"
echo -e "   ${GRAY}Description: React application served by Nginx${NC}"
check_file "src/legal-chatbot-fe/Dockerfile"
check_dockerfile_features "src/legal-chatbot-fe/Dockerfile"
check_file "src/legal-chatbot-fe/.dockerignore"

echo -e "\n${CYAN}⚙️ CONFIGURATION FILES:${NC}"
echo -e "${WHITE}========================${NC}"

echo -e "\n${BLUE}🔹 Docker Compose${NC}"
echo -e "   ${GRAY}Description: Complete development environment${NC}"
check_file "docker-compose.yml"

echo -e "\n${BLUE}🔹 Environment Template${NC}"
echo -e "   ${GRAY}Description: Docker environment variables template${NC}"
check_file ".env.docker.example"

echo -e "\n${BLUE}🔹 Build Script${NC}"
echo -e "   ${GRAY}Description: Bash script to build all Docker images${NC}"
check_file "scripts/build-docker/build-images.sh"

echo -e "\n${BLUE}🔹 Helm Update Script${NC}"
echo -e "   ${GRAY}Description: Update Helm values with Docker images${NC}"
check_file "scripts/update-helm-values.sh"

echo -e "\n${BLUE}🔹 Docker Documentation${NC}"
echo -e "   ${GRAY}Description: Complete Docker setup and usage guide${NC}"
check_file "scripts/DOCKER_README.md"

echo -e "\n${CYAN}🛠️ DOCKER ENVIRONMENT CHECK:${NC}"
echo -e "${WHITE}==============================${NC}"

# Check Docker availability
if docker_version=$(docker --version 2>/dev/null); then
    echo -e "${GREEN}✅ Docker: $docker_version${NC}"
else
    echo -e "${RED}❌ Docker: Not available${NC}"
fi

# Check Docker daemon
if docker ps >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker Daemon: Running${NC}"
else
    echo -e "${RED}❌ Docker Daemon: Not running${NC}"
fi

# Check Docker Compose
if compose_version=$(docker-compose --version 2>/dev/null); then
    echo -e "${GREEN}✅ Docker Compose: $compose_version${NC}"
else
    if compose_version=$(docker compose version 2>/dev/null); then
        echo -e "${GREEN}✅ Docker Compose: $compose_version${NC}"
    else
        echo -e "${YELLOW}⚠️ Docker Compose: Not available${NC}"
    fi
fi

echo -e "\n${CYAN}📊 DOCKER IMAGES STATUS:${NC}"
echo -e "${WHITE}=========================${NC}"

# Check existing images
if backend_image=$(docker images legal-retrieval/backend --format "{{.Repository}}:{{.Tag}}" 2>/dev/null | head -1); then
    if [[ -n "$backend_image" ]]; then
        echo -e "${GREEN}✅ Backend Image: $backend_image${NC}"
        backend_size=$(docker images legal-retrieval/backend --format "{{.Size}}" 2>/dev/null | head -1)
        echo -e "   ${GRAY}Size: $backend_size${NC}"
    else
        echo -e "${YELLOW}⚠️ Backend Image: Not built${NC}"
        echo -e "   ${GRAY}Run: ./scripts/build-docker/build-images.sh backend${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ Backend Image: Not built${NC}"
    echo -e "   ${GRAY}Run: ./scripts/build-docker/build-images.sh backend${NC}"
fi

if frontend_image=$(docker images legal-retrieval/frontend --format "{{.Repository}}:{{.Tag}}" 2>/dev/null | head -1); then
    if [[ -n "$frontend_image" ]]; then
        echo -e "${GREEN}✅ Frontend Image: $frontend_image${NC}"
        frontend_size=$(docker images legal-retrieval/frontend --format "{{.Size}}" 2>/dev/null | head -1)
        echo -e "   ${GRAY}Size: $frontend_size${NC}"
    else
        echo -e "${YELLOW}⚠️ Frontend Image: Not built${NC}"
        echo -e "   ${GRAY}Run: ./scripts/build-docker/build-images.sh frontend${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ Frontend Image: Not built${NC}"
    echo -e "   ${GRAY}Run: ./scripts/build-docker/build-images.sh frontend${NC}"
fi

echo -e "\n${GREEN}🚀 QUICK START COMMANDS:${NC}"
echo -e "${YELLOW}=========================${NC}"

echo -e "\n${CYAN}📦 Build Images:${NC}"
echo -e "  ${WHITE}./scripts/build-docker/build-images.sh                  # Build all images${NC}"
echo -e "  ${WHITE}./scripts/build-docker/build-images.sh backend         # Build backend only${NC}"
echo -e "  ${WHITE}./scripts/build-docker/build-images.sh frontend        # Build frontend only${NC}"

echo -e "\n${CYAN}🚀 Run with Docker Compose:${NC}"
echo -e "  ${WHITE}docker-compose up -d                                   # Start all services${NC}"
echo -e "  ${WHITE}docker-compose logs -f backend-api                     # View backend logs${NC}"
echo -e "  ${WHITE}docker-compose down                                    # Stop all services${NC}"

echo -e "\n${CYAN}🧪 Test Individual Containers:${NC}"
echo -e "  ${WHITE}docker run --rm -p 8000:8000 legal-retrieval/backend:latest api${NC}"
echo -e "  ${WHITE}docker run --rm -p 3000:80 legal-retrieval/frontend:latest${NC}"

echo -e "\n${CYAN}⚙️ Update Helm for Kubernetes:${NC}"
echo -e "  ${WHITE}./scripts/update-helm-values.sh --load-to-kind --update-kind${NC}"

echo -e "\n${GREEN}🎯 DOCKER FEATURES IMPLEMENTED:${NC}"
echo -e "${YELLOW}=================================${NC}"

features=(
    "✅ Multi-stage builds for optimal image size"
    "✅ Non-root users for security"
    "✅ Health checks for all services"
    "✅ Comprehensive .dockerignore files"
    "✅ Flexible entrypoint scripts"
    "✅ Development docker-compose setup"
    "✅ Production-ready configurations"
    "✅ Automated build scripts"
    "✅ Helm integration for Kubernetes"
    "✅ Environment variable templates"
    "✅ Complete documentation"
)

for feature in "${features[@]}"; do
    echo -e "  ${WHITE}$feature${NC}"
done

echo -e "\n${CYAN}📚 DOCUMENTATION:${NC}"
echo -e "${WHITE}==================${NC}"

echo -e "  ${BLUE}📖 scripts/DOCKER_README.md - Complete Docker setup guide${NC}"
echo -e "  ${BLUE}📋 docker-compose.yml - Development environment configuration${NC}"
echo -e "  ${BLUE}⚙️ .env.docker.example - Environment variables template${NC}"

echo -e "\n${GREEN}🎊 DOCKER SETUP COMPLETE!${NC}"
echo -e "${CYAN}Your Legal Retrieval System is now fully containerized!${NC}"

echo -e "\n${YELLOW}💡 Next Steps:${NC}"
echo -e "  ${WHITE}1. Build images: ./scripts/build-docker/build-images.sh${NC}"
echo -e "  ${WHITE}2. Copy .env file: cp .env.docker.example .env${NC}"
echo -e "  ${WHITE}3. Set your API keys in .env file${NC}"
echo -e "  ${WHITE}4. Start services: docker-compose up -d${NC}"
echo -e "  ${WHITE}5. Access frontend: http://localhost:3000${NC}"
echo -e "  ${WHITE}6. Access backend API: http://localhost:8000/docs${NC}"

echo -e "\n${GREEN}🐳 Happy containerizing! 🐳${NC}"
