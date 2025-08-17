# 🚀 Legal-Retrieval Deployment Scripts
=====================================

## 📋 Available Scripts

### 🎯 **Recommended for Development**
- **`quick-dev-deploy.sh`** - Fast deployment with all-in-one setup
- **`deploy-complete.sh`** - Complete deployment with detailed logging

### 🔧 **Utility Scripts**
- **`create-dev-secrets.sh`** - Create Kubernetes secrets from `.env.secrets`
- **`verify-helmfile-paths.sh`** - Verify Helmfile configuration and paths

### 📁 **Archived Scripts** (in `archived/` folder)
- **`deploy-manual-steps.sh`** - Old approach (kept for reference)
- **`deploy-manual-steps-helmfile.sh`** - Helmfile approach (incorrect architecture)

## ⚡ **Architecture (Corrected)**

```
Bootstrap Phase (Manual):
├── 1. Create secrets
├── 2. Deploy ArgoCD manually (bootstrap)
└── 3. Configure Helmfile Plugin

GitOps Phase (ArgoCD):
├── 4. Deploy Root App-of-Apps  
└── 5. Auto-sync applications via Helmfile CMP
```

## 🚨 **Why ArgoCD Can't Manage Itself**

ArgoCD managing itself creates a circular dependency:
1. ArgoCD App-of-Apps deploys ArgoCD System App
2. If you delete the App-of-Apps, it deletes ArgoCD itself
3. No ArgoCD left to manage applications = 💥 System failure

**Solution**: Bootstrap ArgoCD manually, let it manage only applications.

## 🎯 **Quick Usage**

```bash
# Development deployment (recommended)
cd scripts/
./quick-dev-deploy.sh

# Complete deployment with full logging
cd scripts/  
./deploy-complete.sh

# Verify configuration
cd scripts/
./verify-helmfile-paths.sh
```

## 📊 **Script Comparison**

| Script | ArgoCD Install | Plugin Config | App Deploy | Use Case |
|--------|----------------|---------------|------------|----------|
| `quick-dev-deploy.sh` | ✅ Bootstrap | ✅ Auto | ✅ GitOps | Development |
| `deploy-complete.sh` | ✅ Bootstrap | ✅ Manual | ✅ GitOps | Production |
| `create-dev-secrets.sh` | ❌ | ❌ | ❌ | Secrets only |

## 🔧 **Configuration Files Used**

- **`../argocd-manifests/cmp-helmfile-plugin.yaml`** - Helmfile CMP plugin
- **`../argocd-manifests/root-app.yaml`** - App-of-Apps root
- **`../helm/helmfile.yaml`** - Main Helmfile orchestration
- **`../.env.secrets`** - Development secrets (not committed)

## 🚀 **What Happens After Deployment**

1. **ArgoCD UI**: Access at https://localhost:8080
2. **Applications**: Auto-deploy via sync waves
3. **Monitoring**: All apps visible in ArgoCD UI
4. **Updates**: Change code → commit → ArgoCD syncs

## ⚠️ **Troubleshooting**

```bash
# Check ArgoCD status
kubectl get pods -n argocd

# Check applications
kubectl get applications -n argocd

# Access ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Get admin password
kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath='{.data.password}' | base64 -d
```
