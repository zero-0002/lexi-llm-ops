# 🚀 Legal-Retrieval Deployment Process
================================

## ⚡ **Deployment Architecture (Corrected)**

```
Bootstrap Phase (Manual - Outside GitOps):
├── 1. Create secrets from .env.secrets  
├── 2. Deploy ArgoCD manually
└── 3. Configure Helmfile Plugin

GitOps Phase (Automated via ArgoCD):  
├── 4. Deploy Root App-of-Apps
└── 5. ArgoCD auto-syncs all applications via Helmfile
```

> **🚨 Critical**: ArgoCD CANNOT manage itself! It must be bootstrapped manually first.

## 🎯 Quick Start (Recommended for Development)

```bash
cd scripts/
./quick-dev-deploy.sh
```

This script follows the **correct architecture**:
- ✅ **Bootstrap ArgoCD manually** (prevents self-destruction)
- ✅ **Applications managed by ArgoCD** (GitOps)
- ✅ Uses existing CMP plugin from `argocd-manifests/cmp-helmfile-plugin.yaml`
- ✅ No circular dependencies

## 📋 Manual Deployment Process

### Step 1: Create Base Secrets 🔐
```bash
cd scripts/
./create-dev-secrets.sh
```

### Step 2: Bootstrap ArgoCD (Outside GitOps) 🛠️
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n argocd
```

### Step 3: Configure Helmfile Plugin 🔧
```bash
kubectl apply -f argocd-manifests/cmp-helmfile-plugin.yaml
```

### Step 4: Deploy Root Application (GitOps) 📦
```bash
kubectl apply -f argocd-manifests/root-app.yaml
```

### Step 5: Monitor ArgoCD Sync Waves ⏱️
ArgoCD automatically deploys in this order:
```
Wave -2: setup-secrets (External Secrets Operator)
Wave -1: mongo, redis, qdrant (Databases)  
Wave  0: application-backend, application-frontend (Apps)
Wave  1: prometheus-stack, loki, promtail (Monitoring)
```

## 🔧 Complete Manual Alternative
```bash
cd scripts/
./deploy-complete.sh
```

## 🌐 Access ArgoCD UI

1. **Port Forward:**
   ```bash
   kubectl port-forward svc/argocd-server -n argocd 8080:443
   ```

2. **Access URL:** https://localhost:8080

3. **Get Admin Password:**
   ```bash
   kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath='{.data.password}' | base64 -d
   ```

## 📁 Architecture Decisions

### ✅ **What We Use:**
- **Manual ArgoCD Bootstrap**: Prevents circular dependency
- **Helmfile CMP Plugin**: For template generation (`argocd-manifests/cmp-helmfile-plugin.yaml`)
- **GitOps for Applications**: ArgoCD manages all apps via sync waves

### ❌ **What We Removed:**
- **`argocd-system.yaml`**: Removed (ArgoCD can't manage itself)
- **Helmfile ArgoCD deployment**: Removed (causes bootstrap issues)
- **helm/charts/argocd/**: Can be kept for reference but not used in GitOps

## 🚨 Important Notes
- **Never commit `.env.secrets`** - contains sensitive data
- **ArgoCD bootstrap is manual** - this is the correct approach
- **Applications use Helmfile** - via CMP plugin for template generation
- **No self-management** - ArgoCD doesn't manage its own deployment

## 🔍 Troubleshooting
- **ArgoCD UI:** `kubectl port-forward svc/argocd-server -n argocd 8080:443`
- **App status:** `kubectl get applications -n argocd -o wide`
- **External secrets:** `kubectl get externalsecrets -n secrets-management`
- **Pod logs:** `kubectl logs -n application deployment/legal-backend`

## 📊 Monitoring Deployment Progress

### Check ArgoCD Applications
```bash
kubectl get applications -n argocd -o wide
```

### Check All Pods
```bash
kubectl get pods -A | grep -E "(legal-|argocd|mongo|redis|qdrant)"
```

### Check Services
```bash
kubectl get svc -n application
```

### Check External Secrets
```bash
kubectl get externalsecrets -n secrets-management
kubectl describe externalsecret legal-app-secrets -n secrets-management
```
