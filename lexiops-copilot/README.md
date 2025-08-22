# 🚀 DevOps Copilot System (Kubernetes Namespace Deployment)

## 📌 Overview
This project implements an **agentic workflow system** designed to assist **DevOps engineers (Operators)** in managing and automating operations on **Kubernetes clusters**.  
The system is deployed **inside a single Kubernetes namespace** and acts as an **internal copilot** — planning, validating, and executing tasks securely and reliably.  

⚠️ **Note:** End-users do **not** interact with this system. Only **Dev/Operators** can submit requests.



<img src="./docs/agentic.svg" alt="Lexiops copilot"/>


## 🏗 Architecture & Flow

### 🔹 1. Request Handling
- **Dev (Operator)** submits a request (task, prompt, or operation).  
- The request is received by the **Responder**.

### 🔹 2. Planning
- The **Planner** generates an execution plan.  
- May query **DB-RAG** for background knowledge or historical results.  

### 🔹 3. Review & Validation
- The **Reviewer** checks the plan:  
  - ✅ **Pass** → forwarded to the **Router**.  
  - ❌ **Fail** → sent back to the **Planner** for adjustment.  
  - 🔄 **Repeated failures** → escalated to **Dev** for manual fix.

### 🔹 4. Execution
- **Router** selects the appropriate **Tool** (e.g., `kubectl MCP`, `Helm`, `ArgoCD`, `Prometheus`).  
- The tool executes the operation on the Kubernetes cluster.  
- Results are stored in **DB-RAG** for later reuse.

### 🔹 5. Response
- **Responder** composes the final output.  
- Returns the result back to the **Dev (Operator)**.

### 🔹 6. Monitoring & Improvement
- **Agent Supervisor** monitors logs, errors, and workflow performance.  
- Detects recurring error patterns.  
- Suggests improvements or updates rule-based logic/configuration.

---

## ⚙️ Features
- 🛡 **Safe Execution Flow**: Plans are always reviewed before execution.  
- 🔄 **Fallback & Error Handling**: Automatic retries, fallback agents, and escalation to human if needed.  
- 📚 **DB-RAG Integration**: Knowledge base for contextual responses and plan refinement.  
- 👀 **Agent Supervisor**: Continuous monitoring and self-improvement.  
- ☸️ **Kubernetes Native**: Deployed and isolated in a single namespace.  

---

## 🔐 Security & Access Control
- Only **Dev/Operators** can access and interact with the system.  
- **End-users** cannot see or interact with internal agents.  
- All executions run under controlled **namespace-scoped RBAC permissions**.  

---

## 📊 Example Workflow (Text Version)

1. **Dev** submits a request.  
2. **Responder** receives and forwards the request to **Planner**.  
3. **Planner** creates an execution plan.  
4. **Reviewer** checks the plan:  
   - If valid → send to **Router**.  
   - If invalid → return to **Planner**.  
   - If repeated errors → escalate to **Dev**.  
5. **Router** chooses the correct **Tool**.  
6. **Tool** executes the task and updates **DB-RAG**.  
7. **Planner** may reuse results from **DB-RAG**.  
8. **Responder** sends the final answer back to **Dev**.  
9. **Agent Supervisor** monitors everything, detects patterns, and proposes improvements.  

---

## 📌 Future Improvements
- 🤖 **Meta-Agent Supervisor** with adaptive learning for recurring error patterns.  
- 📈 **Extended observability** (Grafana/Loki dashboards).  
- 📝 **Audit logging** for compliance and traceability.  
- 🗂 **Versioned DB-RAG** to track evolving infrastructure knowledge.  

---

✅ With this design, the system provides a **robust, fault-tolerant, and secure DevOps assistant** inside Kubernetes.  
