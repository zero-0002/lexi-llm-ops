#!/bin/bash
# Legal Retrieval System - Setup Script
# =====================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to make scripts executable
make_scripts_executable() {
    log_step "Making all scripts executable..."
    
    local scripts=(
        "build-images.sh"
        "push-images.sh"
        "update-helm-values.sh"
        "manage-secrets.sh"
        "deploy-pipeline.sh"
        "monitor-deployment.sh"
        "setup.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [ -f "$script" ]; then
            chmod +x "$script"
            log_success "Made executable: $script"
        else
            log_warning "Script not found: $script"
        fi
    done
}

# Function to check prerequisites
check_prerequisites() {
    log_step "Checking prerequisites..."
    
    local missing_tools=()
    
    # Check Docker
    if ! command_exists docker; then
        missing_tools+=("docker")
    else
        log_success "Docker found: $(docker --version | head -n1)"
    fi
    
    # Check kubectl
    if ! command_exists kubectl; then
        missing_tools+=("kubectl")
    else
        log_success "kubectl found: $(kubectl version --client --short 2>/dev/null || kubectl version --client)"
    fi
    
    # Check Helm
    if ! command_exists helm; then
        missing_tools+=("helm")
    else
        log_success "Helm found: $(helm version --short)"
    fi
    
    # Check optional tools
    if command_exists yq; then
        log_success "yq found: $(yq --version)"
    else
        log_warning "yq not found (optional - for advanced YAML processing)"
    fi
    
    if command_exists jq; then
        log_success "jq found: $(jq --version)"
    else
        log_warning "jq not found (recommended for JSON processing)"
    fi
    
    # Report missing tools
    if [ ${#missing_tools[@]} -gt 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        echo ""
        echo "Installation instructions:"
        echo "=========================="
        
        for tool in "${missing_tools[@]}"; do
            case "$tool" in
                "docker")
                    echo "Docker: https://docs.docker.com/get-docker/"
                    echo "  curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh"
                    ;;
                "kubectl")
                    echo "kubectl: https://kubernetes.io/docs/tasks/tools/"
                    echo "  curl -LO \"https://dl.k8s.io/release/\$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl\""
                    echo "  sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl"
                    ;;
                "helm")
                    echo "Helm: https://helm.sh/docs/intro/install/"
                    echo "  curl https://get.helm.sh/helm-v3.12.0-linux-amd64.tar.gz | tar xz"
                    echo "  sudo mv linux-amd64/helm /usr/local/bin/"
                    ;;
            esac
            echo ""
        done
        
        return 1
    fi
    
    return 0
}

# Function to setup environment file
setup_environment() {
    log_step "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            log "Creating .env from .env.example..."
            cp ".env.example" ".env"
            log_success ".env file created"
            echo ""
            log_warning "IMPORTANT: Please edit .env file with your actual values:"
            echo "  - DockerHub credentials"
            echo "  - OpenAI API key"
            echo "  - Database passwords"
            echo "  - JWT secret key"
            echo ""
            echo "Edit command: nano .env"
        else
            log_warning ".env.example not found, creating basic .env..."
            cat > .env << 'EOF'
# Basic configuration - Please update with your values
DOCKER_REGISTRY=docker.io
DOCKER_NAMESPACE=legalretrieval
IMAGE_TAG=latest
DOCKERHUB_USERNAME=your_username
DOCKERHUB_PASSWORD=your_password
OPENAI_API_KEY=your_openai_key
JWT_SECRET_KEY=your_jwt_secret_min_32_chars
EOF
            log_success "Basic .env file created"
        fi
    else
        log_success ".env file already exists"
    fi
}

# Function to create necessary directories
create_directories() {
    log_step "Creating necessary directories..."
    
    local directories=(
        "helm/values/backups"
        "logs"
        "certs"
        "backup"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log_success "Created directory: $dir"
        else
            log "Directory exists: $dir"
        fi
    done
}

# Function to check Docker access
check_docker_access() {
    log_step "Checking Docker access..."
    
    if docker ps >/dev/null 2>&1; then
        log_success "Docker daemon is accessible"
    else
        log_warning "Cannot access Docker daemon"
        echo "You may need to:"
        echo "  1. Start Docker daemon: sudo systemctl start docker"
        echo "  2. Add user to docker group: sudo usermod -aG docker \$USER"
        echo "  3. Log out and log back in"
        return 1
    fi
}

# Function to check Kubernetes access
check_kubernetes_access() {
    log_step "Checking Kubernetes access..."
    
    if kubectl cluster-info >/dev/null 2>&1; then
        local context=$(kubectl config current-context)
        log_success "Connected to Kubernetes cluster: $context"
    else
        log_warning "Cannot access Kubernetes cluster"
        echo "Please ensure:"
        echo "  1. Kubernetes cluster is running"
        echo "  2. kubectl is configured correctly"
        echo "  3. kubeconfig file exists and is valid"
        return 1
    fi
}

# Function to validate Helm charts
validate_helm_charts() {
    log_step "Validating Helm charts..."
    
    local chart_dirs=(
        "helm/charts/legal-backend"
        "helm/charts/legal-celery-worker"
        "helm/charts/legal-frontend"
    )
    
    local validation_errors=0
    
    for chart_dir in "${chart_dirs[@]}"; do
        if [ -d "$chart_dir" ]; then
            if helm lint "$chart_dir" >/dev/null 2>&1; then
                log_success "Chart valid: $chart_dir"
            else
                log_error "Chart validation failed: $chart_dir"
                validation_errors=$((validation_errors + 1))
            fi
        else
            log_warning "Chart directory not found: $chart_dir"
            validation_errors=$((validation_errors + 1))
        fi
    done
    
    return $validation_errors
}

# Function to show setup summary
show_setup_summary() {
    echo ""
    echo -e "${CYAN}Setup Summary${NC}"
    echo "============="
    echo ""
    
    echo -e "${GREEN}✅ Available Scripts:${NC}"
    echo "  ./build-images.sh       - Build Docker images"
    echo "  ./push-images.sh        - Push images to registry"
    echo "  ./update-helm-values.sh - Update Helm values"
    echo "  ./manage-secrets.sh     - Manage Kubernetes secrets"
    echo "  ./deploy-pipeline.sh    - Complete deployment pipeline"
    echo "  ./monitor-deployment.sh - Monitor deployments"
    echo ""
    
    echo -e "${YELLOW}📝 Next Steps:${NC}"
    echo "  1. Edit .env file with your configuration"
    echo "  2. Ensure Docker and Kubernetes are running"
    echo "  3. Run: ./deploy-pipeline.sh"
    echo ""
    
    echo -e "${BLUE}📚 Documentation:${NC}"
    echo "  See: docs/LINUX_DEPLOYMENT_GUIDE.md"
    echo ""
    
    echo -e "${CYAN}🚀 Quick Start:${NC}"
    echo "  # Full deployment"
    echo "  ./deploy-pipeline.sh"
    echo ""
    echo "  # Step by step"
    echo "  ./build-images.sh"
    echo "  ./push-images.sh"
    echo "  ./manage-secrets.sh"
    echo "  ./deploy-pipeline.sh"
}

# Main function
main() {
    echo -e "${GREEN}"
    echo "🛠️  Legal Retrieval System - Setup"
    echo "=================================="
    echo -e "${NC}"
    
    local setup_errors=0
    
    # Make scripts executable
    make_scripts_executable
    
    # Check prerequisites
    if ! check_prerequisites; then
        setup_errors=$((setup_errors + 1))
    fi
    
    # Setup environment
    setup_environment
    
    # Create directories
    create_directories
    
    # Check Docker access
    if ! check_docker_access; then
        setup_errors=$((setup_errors + 1))
    fi
    
    # Check Kubernetes access (optional)
    if ! check_kubernetes_access; then
        log_warning "Kubernetes not accessible (you can set this up later)"
    fi
    
    # Validate Helm charts
    if ! validate_helm_charts; then
        log_warning "Some Helm chart validation issues found"
    fi
    
    # Show summary
    show_setup_summary
    
    # Final result
    if [ $setup_errors -eq 0 ]; then
        echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
        echo -e "${CYAN}Ready to deploy!${NC}"
    else
        echo -e "${YELLOW}⚠️  Setup completed with some warnings${NC}"
        echo -e "${CYAN}Please address the issues above before deploying${NC}"
    fi
}

# Handle arguments
case "${1:-setup}" in
    "check")
        check_prerequisites
        ;;
    "scripts")
        make_scripts_executable
        ;;
    "env")
        setup_environment
        ;;
    "dirs")
        create_directories
        ;;
    "docker")
        check_docker_access
        ;;
    "k8s")
        check_kubernetes_access
        ;;
    "helm")
        validate_helm_charts
        ;;
    "setup"|"all")
        main
        ;;
    *)
        echo "Usage: $0 {setup|check|scripts|env|dirs|docker|k8s|helm|all}"
        echo ""
        echo "Commands:"
        echo "  setup   - Complete setup (default)"
        echo "  check   - Check prerequisites only"
        echo "  scripts - Make scripts executable only"
        echo "  env     - Setup environment file only"
        echo "  dirs    - Create directories only"
        echo "  docker  - Check Docker access only"
        echo "  k8s     - Check Kubernetes access only"
        echo "  helm    - Validate Helm charts only"
        echo "  all     - Same as setup"
        exit 1
        ;;
esac
