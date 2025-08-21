# 🏗️ KIẾN TRÚC MCP 3-SERVER ARCHITECTURE

## 📊 TỔNG QUAN KIẾN TRÚC:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   🌐 TIER 1:    │    │   🔄 TIER 2:    │    │   🛠️ TIER 3:    │
│  FASTAPI MAIN   │◄──►│   MCP CLIENT    │◄──►│   MCP TOOLS     │
│   (Port 8000)   │    │   (Adapter)     │    │   (Kubernetes)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 🏷️ **TIER 1: FASTAPI MAIN SERVER**

### **Vai trò:** Frontend API Gateway + AI Agent
### **Thành phần:** 
- `agent/main.py` - FastAPI application
- `agent/graph.py` - LangGraph workflow 
- `agent/nodes/` - AI processing nodes (GPT-4)
- **Port:** 8000

### **Chức năng:**
```python
✅ REST API endpoints (/chat, /health)
✅ AI Agent workflow (Planner → Executor → Synthesizer) 
✅ OpenAI GPT-4 integration
✅ User request processing
✅ Response formatting
```

### **Example Request:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "List all pods in lexiops-copilot namespace"}'
```

---

## 🔄 **TIER 2: MCP CLIENT (ADAPTER)**

### **Vai trò:** Protocol Bridge + Session Manager
### **Thành phần:**
- `langchain_mcp_adapters.client.MultiServerMCPClient`
- Session management
- Protocol translation
- **Internal communication**

### **Chức năng:**
```python
✅ Translate LangChain tools ↔ MCP protocol
✅ Session initialization & management
✅ JSON-RPC 2.0 communication
✅ Error handling & retries
✅ Multiple MCP server connections
```

### **Configuration:**
```python
mcp_client = MultiServerMCPClient({
    "kubernetes": {
        "url": "http://mcp-k8s-service.lexiops-copilot.svc.cluster.local:8000/mcp/",
        "transport": "streamable_http",
    },
    # Future: Add more MCP servers
    "filesystem": {...},
    "database": {...}
})
```

---

## 🛠️ **TIER 3: MCP TOOLS SERVER**

### **Vai trò:** Specialized Tool Provider
### **Thành phần:**
- Kubernetes MCP Server (Pod: `mcp-k8s-deployment`)
- Docker image: `ghcr.io/feiskyer/mcp-kubernetes-server:latest`
- **Port:** 8000 (ClusterIP service)

### **Chức năng:**
```python
✅ 51 Kubernetes tools (kubectl, helm)
✅ Resource management (get, create, delete, patch)
✅ Deployment operations (scale, rollout, expose)
✅ Node management (cordon, drain, taint)
✅ Exec, logs, port-forward commands
✅ RBAC-compliant operations
```

### **Available Tools:**
```yaml
Tools Categories:
- Resource Ops: k8s_get, k8s_describe, k8s_logs, k8s_create, k8s_delete
- Deployment: k8s_run, k8s_scale, k8s_rollout_*, k8s_expose  
- Node Mgmt: k8s_cordon, k8s_uncordon, k8s_drain, k8s_taint
- Utilities: k8s_exec_command, k8s_port_forward, k8s_cp
- Raw Access: kubectl, helm
```

---

## 🔗 **COMMUNICATION FLOW:**

### **Request Flow:**
```
1. User → FastAPI: "List pods in namespace X"
                  ↓
2. AI Agent (Planner): Analyze request → Plan: use k8s_get tool  
                  ↓
3. MCP Client: Translate to JSON-RPC → Initialize session
                  ↓
4. MCP K8s Server: Execute kubectl get pods -n X
                  ↓
5. MCP Client: Parse response → Convert to LangChain format
                  ↓  
6. AI Agent (Synthesizer): Format natural response
                  ↓
7. FastAPI → User: "Here are the pods in namespace X: ..."
```

### **Protocol Details:**
```json
# Tier 1 → Tier 2 (LangChain format)
{
  "tool_name": "k8s_get",
  "args": {"resource": "pods", "namespace": "lexiops-copilot"}
}

# Tier 2 → Tier 3 (MCP JSON-RPC)
{
  "jsonrpc": "2.0",
  "id": "call-1", 
  "method": "tools/call",
  "params": {
    "name": "k8s_get",
    "arguments": {"resource": "pods", "namespace": "lexiops-copilot"}
  }
}
```

---

## 🚀 **DEPLOYMENT ARCHITECTURE:**

### **Current Deployment:**
```yaml
# Tier 1: FastAPI Main
Location: Local development (D:/Data/Legal-Retrieval/lexiops-copilot)
Command: uvicorn agent.main:app --host 0.0.0.0 --port 8000 --reload
Access: http://localhost:8000

# Tier 2: MCP Client  
Location: Embedded in FastAPI process (langchain_mcp_adapters)
Type: Python library/adapter
Communication: Internal function calls

# Tier 3: MCP Tools
Location: Kubernetes cluster (lexiops-copilot namespace)
Service: mcp-k8s-service.lexiops-copilot.svc.cluster.local:8000
Pod: mcp-k8s-deployment-7b8cd99786-b66l8
```

### **Scaling Options:**
```yaml
# Single Node Development:
Tier 1: localhost:8000
Tier 2: embedded  
Tier 3: port-forward to localhost:8081

# Production Kubernetes:
Tier 1: Deployment + Service + Ingress
Tier 2: Sidecar container or embedded
Tier 3: Multiple MCP server deployments per domain
```

---

## 💡 **ADVANTAGES OF 3-TIER ARCHITECTURE:**

### ✅ **Separation of Concerns:**
- **Tier 1:** User interface & AI logic
- **Tier 2:** Protocol management & routing  
- **Tier 3:** Specialized domain tools

### ✅ **Scalability:**
- Independent scaling per tier
- Add new MCP servers without changing Tier 1
- Multiple tool domains (K8s, DB, Files, etc.)

### ✅ **Security:**
- Network isolation between tiers
- RBAC per MCP server
- Session-based authentication

### ✅ **Maintainability:**
- Clear boundaries
- Pluggable architecture
- Independent deployment cycles

---

## 🔮 **FUTURE EXTENSIONS:**

### **Additional MCP Servers (Tier 3):**
```yaml
Database MCP: PostgreSQL/MongoDB operations
Filesystem MCP: File system operations  
Cloud MCP: AWS/GCP/Azure operations
Monitoring MCP: Prometheus/Grafana operations
CI/CD MCP: Jenkins/ArgoCD operations
```

### **Enhanced Tier 2:**
```python
# Multi-server routing
# Load balancing
# Caching layer  
# Circuit breakers
# Metrics collection
```

---

## 🎯 **SUMMARY:**

**ĐÚng rồi!** Triển khai MCP cần **3 server tiers**:

1. **🌐 Tier 1 (Main):** FastAPI + AI Agent - User interface
2. **🔄 Tier 2 (Client):** MCP Adapter - Protocol bridge  
3. **🛠️ Tier 3 (Tools):** MCP K8s Server - Specialized tools

Architecture này cho phép:
- **Modular design** 
- **Independent scaling**
- **Domain-specific tools**
- **Protocol abstraction**
- **Security isolation**

Hiện tại bạn đã có đủ 3 tiers và architecture hoạt động tốt! 🎉
