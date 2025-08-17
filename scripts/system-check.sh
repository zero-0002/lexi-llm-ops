#!/bin/bash
# Legal Retrieval System - Complete System Check
# ==============================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔍 LEGAL RETRIEVAL SYSTEM - COMPLETE SYSTEM CHECK${NC}"
echo -e "${YELLOW}===================================================${NC}"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check file exists and show size
check_file() {
    local file_path="$1"
    local description="$2"
    
    if [[ -f "$file_path" ]]; then
        local size=$(du -h "$file_path" 2>/dev/null | cut -f1)
        echo -e "   ${GREEN}✅ $description: $file_path ($size)${NC}"
        return 0
    else
        echo -e "   ${RED}❌ $description: Not found${NC}"
        return 1
    fi
}

# Function to check directory exists
check_directory() {
    local dir_path="$1"
    local description="$2"
    
    if [[ -d "$dir_path" ]]; then
        local count=$(find "$dir_path" -type f 2>/dev/null | wc -l)
        echo -e "   ${GREEN}✅ $description: $dir_path ($count files)${NC}"
        return 0
    else
        echo -e "   ${RED}❌ $description: Not found${NC}"
        return 1
    fi
}

echo -e "\n${CYAN}🛠️ SYSTEM REQUIREMENTS CHECK:${NC}"
echo -e "${WHITE}==============================${NC}"

# Check Docker
if command_exists docker; then
    docker_version=$(docker --version 2>/dev/null)
    echo -e "${GREEN}✅ Docker: $docker_version${NC}"
    
    # Check Docker daemon
    if docker ps >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Docker Daemon: Running${NC}"
    else
        echo -e "${RED}❌ Docker Daemon: Not running${NC}"
    fi
else
    echo -e "${RED}❌ Docker: Not installed${NC}"
fi

# Check Docker Compose
if command_exists docker-compose; then
    compose_version=$(docker-compose --version 2>/dev/null)
    echo -e "${GREEN}✅ Docker Compose: $compose_version${NC}"
elif command_exists docker && docker compose version >/dev/null 2>&1; then
    compose_version=$(docker compose version 2>/dev/null)
    echo -e "${GREEN}✅ Docker Compose: $compose_version${NC}"
else
    echo -e "${RED}❌ Docker Compose: Not available${NC}"
fi

# Check other tools
tools=("kubectl" "kind" "helm" "make" "git" "curl" "jq")
for tool in "${tools[@]}"; do
    if command_exists "$tool"; then
        tool_version=$(eval "$tool --version 2>/dev/null | head -1" || echo "Available")
        echo -e "${GREEN}✅ $tool: Available${NC}"
    else
        echo -e "${YELLOW}⚠️ $tool: Not installed (optional)${NC}"
    fi
done

echo -e "\n${CYAN}📁 PROJECT STRUCTURE CHECK:${NC}"
echo -e "${WHITE}=============================${NC}"

# Check main directories
directories=(
    "src:Source Code"
    "src/app:Backend Application"
    "src/legal-chatbot-fe:Frontend Application"
    "helm:Kubernetes Helm Charts"
    "scripts:Deployment Scripts"
    "tests:Test Suite"
    "docs:Documentation"
)

for dir_info in "${directories[@]}"; do
    IFS=':' read -r dir_path description <<< "$dir_info"
    check_directory "$dir_path" "$description"
done

echo -e "\n${CYAN}🐳 DOCKER CONFIGURATION CHECK:${NC}"
echo -e "${WHITE}================================${NC}"

# Check Docker files
check_file "docker-compose.yml" "Main Docker Compose"
check_file "docker-compose.test.yml" "Test Docker Compose"
check_file "src/app/Dockerfile" "Backend Dockerfile"
check_file "src/legal-chatbot-fe/Dockerfile" "Frontend Dockerfile"
check_file "src/app/docker-entrypoint.sh" "Backend Entrypoint"

echo -e "\n${CYAN}📋 BASH SCRIPTS CHECK:${NC}"
echo -e "${WHITE}========================${NC}"

# Check bash scripts
bash_scripts=(
    "scripts/docker-summary.sh:Docker Summary Script"
    "scripts/build-docker.sh:Docker Build Script"
    "scripts/update-helm-values.sh:Helm Values Update Script"
    "tests/run_docker_tests.sh:Docker Test Runner"
    "tests/run_backend_tests.sh:Backend Test Runner"
    "scripts/deploy-pipeline.sh:Deploy Pipeline Script"
    "scripts/setup.sh:Setup Script"
    "scripts/monitor-deployment.sh:Monitor Deployment Script"
)

for script_info in "${bash_scripts[@]}"; do
    IFS=':' read -r script_path description <<< "$script_info"
    if check_file "$script_path" "$description"; then
        # Check if script is executable
        if [[ -x "$script_path" ]]; then
            echo -e "     ${GREEN}✅ Executable${NC}"
        else
            echo -e "     ${YELLOW}⚠️ Not executable (run: chmod +x $script_path)${NC}"
        fi
    fi
done

echo -e "\n${CYAN}🧪 TEST INFRASTRUCTURE CHECK:${NC}"
echo -e "${WHITE}==============================${NC}"

# Check test files
test_files=(
    "tests/test_api_comprehensive.py:Comprehensive API Tests"
    "tests/test_database.py:Database Tests"
    "tests/test_websocket.py:WebSocket Tests"
    "tests/conftest.py:PyTest Configuration"
    "tests/pytest.ini:PyTest Settings"
    "tests/requirements.test.txt:Test Dependencies"
    "tests/Dockerfile.test:Test Container"
)

for file_info in "${test_files[@]}"; do
    IFS=':' read -r file_path description <<< "$file_info"
    check_file "$file_path" "$description"
done

echo -e "\n${CYAN}⚙️ CONFIGURATION FILES CHECK:${NC}"
echo -e "${WHITE}==============================${NC}"

# Check configuration files
config_files=(
    "Makefile:Make Commands"
    ".env.docker.example:Environment Template"
    "scripts/mongo-init.js:MongoDB Initialization"
    "scripts/mongo-init-test.js:MongoDB Test Initialization"
)

for file_info in "${config_files[@]}"; do
    IFS=':' read -r file_path description <<< "$file_info"
    check_file "$file_path" "$description"
done

echo -e "\n${CYAN}📚 DOCUMENTATION CHECK:${NC}"
echo -e "${WHITE}========================${NC}"

# Check documentation files
doc_files=(
    "README.md:Main README"
    "docs/TESTING_GUIDE.md:Testing Guide"
    "docs/API_TESTING_GUIDE.md:API Testing Guide"
    "tests/DOCKER_TESTING_GUIDE.md:Docker Testing Guide"
    "DOCKER_DEPLOYMENT_GUIDE.md:Docker Deployment Guide"
    "scripts/DOCKER_README.md:Docker Scripts README"
)

for file_info in "${doc_files[@]}"; do
    IFS=':' read -r file_path description <<< "$file_info"
    check_file "$file_path" "$description"
done

echo -e "\n${CYAN}🚀 QUICK COMMANDS CHECK:${NC}"
echo -e "${WHITE}==========================${NC}"

echo -e "${BLUE}🔨 Build Commands:${NC}"
echo -e "  ${WHITE}./scripts/build-docker.sh                    # Build all services${NC}"
echo -e "  ${WHITE}./scripts/build-docker.sh -s backend         # Build backend only${NC}"
echo -e "  ${WHITE}./scripts/build-docker.sh -s frontend        # Build frontend only${NC}"

echo -e "\n${BLUE}🧪 Test Commands:${NC}"
echo -e "  ${WHITE}make test                                     # Run all tests${NC}"
echo -e "  ${WHITE}make test-smoke                               # Run smoke tests${NC}"
echo -e "  ${WHITE}./tests/run_docker_tests.sh --command full   # Direct test runner${NC}"

echo -e "\n${BLUE}🚀 Deploy Commands:${NC}"
echo -e "  ${WHITE}make up                                       # Start all services${NC}"
echo -e "  ${WHITE}make dev-up                                   # Start with build${NC}"
echo -e "  ${WHITE}docker-compose up -d                         # Direct compose${NC}"

echo -e "\n${BLUE}📊 Monitor Commands:${NC}"
echo -e "  ${WHITE}make logs                                     # View all logs${NC}"
echo -e "  ${WHITE}make status                                   # Check service status${NC}"
echo -e "  ${WHITE}./scripts/docker-summary.sh                  # System summary${NC}"

echo -e "\n${GREEN}🎯 SYSTEM CHECK COMPLETE!${NC}"
echo -e "${CYAN}Your Legal Retrieval System is ready for Linux deployment!${NC}"

# Final recommendations
echo -e "\n${YELLOW}💡 NEXT STEPS:${NC}"
echo -e "  ${WHITE}1. Make scripts executable: find scripts tests -name '*.sh' -exec chmod +x {} \;${NC}"
echo -e "  ${WHITE}2. Build services: ./scripts/build-docker.sh${NC}"
echo -e "  ${WHITE}3. Start services: make dev-up${NC}"
echo -e "  ${WHITE}4. Run tests: make test-smoke${NC}"
echo -e "  ${WHITE}5. Check status: ./scripts/docker-summary.sh${NC}"

echo -e "\n${GREEN}🐧 Welcome to Linux-based deployment! 🐧${NC}"
