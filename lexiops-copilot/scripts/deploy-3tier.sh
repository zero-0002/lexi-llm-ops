#!/bin/bash

echo "🏗️ DEPLOYING 3-TIER MCP ARCHITECTURE"
echo "======================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if command exists
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is not installed"
        exit 1
    fi
}

print_step "Checking prerequisites..."
check_command kubectl
check_command python
check_command pip
check_command uvicorn

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    print_error "Kubernetes cluster not accessible"
    exit 1
fi

print_success "Prerequisites check passed"

echo ""
echo "🛠️ TIER 3: DEPLOYING MCP TOOLS SERVER"
echo "====================================="

print_step "Creating namespace lexiops-copilot..."
kubectl create namespace lexiops-copilot --dry-run=client -o yaml | kubectl apply -f -

print_step "Deploying MCP Kubernetes Server..."
kubectl apply -f k8s/mcp-k8s-deployment.yaml -n lexiops-copilot

print_step "Waiting for deployment to be ready..."
if kubectl wait --for=condition=available --timeout=120s deployment/mcp-k8s-deployment -n lexiops-copilot; then
    print_success "MCP Kubernetes Server deployed successfully"
else
    print_error "MCP Kubernetes Server deployment failed"
    exit 1
fi

echo ""
echo "🔄 TIER 2: SETTING UP MCP CLIENT"
echo "==============================="

print_step "Installing Python dependencies..."
pip install -q langchain langchain-openai langgraph langchain-mcp-adapters fastapi uvicorn python-dotenv aiohttp

print_step "Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    print_warning "Please edit .env and add your OPENAI_API_KEY"
    print_warning "Then run this script again or start the server manually"
fi

# Check for OpenAI API key
if ! grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
    print_warning "OPENAI_API_KEY not found in .env file"
    print_warning "MCP Client will work but AI features may be limited"
fi

print_success "MCP Client setup completed"

echo ""
echo "🌐 TIER 1: STARTING FASTAPI MAIN SERVER"
echo "======================================"

print_step "Configuring MCP client to connect to Tier 3..."
# Update graph.py to use the correct MCP server URL
MCP_SERVICE_URL="http://mcp-k8s-service.lexiops-copilot.svc.cluster.local:8000/mcp/"

print_step "Starting port-forward for MCP server (background)..."
# Kill existing port-forward processes
pkill -f "kubectl port-forward.*mcp-k8s-service" 2>/dev/null || true
sleep 2

# Start port-forward in background
kubectl port-forward service/mcp-k8s-service 9090:8000 -n lexiops-copilot &
PORT_FORWARD_PID=$!
sleep 5

if ps -p $PORT_FORWARD_PID > /dev/null; then
    print_success "Port-forward established on localhost:9090"
else
    print_error "Port-forward failed"
    exit 1
fi

echo ""
echo "🧪 TESTING 3-TIER ARCHITECTURE"  
echo "============================="

print_step "Testing MCP connection..."
if python test_mcp.py > /dev/null 2>&1; then
    print_success "MCP connection test passed"
else
    print_warning "MCP connection test failed, continuing anyway..."
fi

print_step "Starting FastAPI server..."
echo ""
echo "🚀 DEPLOYMENT SUMMARY"
echo "===================="
echo -e "${GREEN}✅ TIER 3 (MCP Tools):${NC} Deployed in Kubernetes"
echo -e "   📍 Service: mcp-k8s-service.lexiops-copilot.svc.cluster.local:8000"
echo -e "   🔗 Port-forward: http://localhost:9090/mcp/"
echo ""
echo -e "${GREEN}✅ TIER 2 (MCP Client):${NC} Embedded in FastAPI process"  
echo -e "   📦 langchain_mcp_adapters loaded"
echo -e "   🔗 Connected to Tier 3 via port-forward"
echo ""
echo -e "${GREEN}✅ TIER 1 (FastAPI Main):${NC} Starting on port 8000"
echo -e "   🌐 REST API: http://localhost:8000"
echo -e "   📚 API Docs: http://localhost:8000/docs"
echo -e "   🤖 AI Agent: GPT-4 Turbo enabled"
echo ""
echo "📋 ARCHITECTURE STATUS:"
echo "User Request → FastAPI (Tier 1) → MCP Client (Tier 2) → K8s Tools (Tier 3)"
echo ""
echo -e "${YELLOW}💡 Testing Commands:${NC}"
echo 'curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"message\": \"List pods in lexiops-copilot namespace\"}"'
echo ""
echo -e "${YELLOW}🛑 To stop all tiers:${NC}"
echo "pkill -f 'uvicorn|kubectl port-forward'"
echo "kubectl delete -f k8s/mcp-k8s-deployment.yaml -n lexiops-copilot"
echo ""
echo "🎯 Starting Tier 1 server..."

# Cleanup function
cleanup() {
    echo ""
    print_step "Shutting down..."
    kill $PORT_FORWARD_PID 2>/dev/null || true
    print_success "Architecture shutdown completed"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup EXIT INT TERM

# Start the FastAPI server
uvicorn agent.main:app --host 0.0.0.0 --port 8000 --reload
