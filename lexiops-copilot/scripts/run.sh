#!/bin/bash

#####
    echo "🚀 Starting LexiOps Copilot Agent..."

echo "🔍 Checking Kubernetes cluster..."
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Kubernetes cluster not accessible"
    exit 1
fi

echo "📦 Creating/checking namespace lexiops-copilot..."
kubectl create namespace lexiops-copilot --dry-run=client -o yaml | kubectl apply -f -

echo "🚀 Deploying MCP Kubernetes Server..."
kubectl apply -f k8s/mcp-k8s-deployment.yaml -n lexiops-copilot

echo "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=60s deployment/mcp-k8s-deployment -n lexiops-copilot

echo "✅ Deployment Status:"
kubectl get all -n lexiops-copilot

echo "📋 MCP Server Details:"
kubectl logs deployment/mcp-k8s-deployment -n lexiops-copilot --tail=10

echo "🌐 MCP Server is available at:"
echo "  - Internal: http://mcp-k8s-service.lexiops-copilot.svc.cluster.local:8000/mcp/"
echo "  - Port forward: kubectl port-forward service/mcp-k8s-service 9090:8000 -n lexiops-copilot"

echo ""
echo "🔧 To test MCP server:"
echo "  kubectl port-forward service/mcp-k8s-service 8002:8000 -n lexiops-copilot"
echo "  python test_mcp.py  # This will test full MCP workflow"
echo ""
echo "✅ MCP Server has 51 Kubernetes tools available!"

echo ""
echo "🚀 Starting AI Agent server on port 8001..."

# Start the server
echo "🌐 Starting server on http://localhost:8000"
uvicorn agent.main:app --host 0.0.0.0 --port 8000 --reload

echo "✅ Agent is ready! Try:"
echo "curl -X POST http://localhost:8000/chat -H 'Content-Type: application/json' -d '{\"message\": \"What time is it?\"}'"

