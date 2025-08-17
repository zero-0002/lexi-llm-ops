# 🚀 Legal-Retrieval Deployment Process
================================

## 🎯 Quick Start (Recommended for Development)

```bash
cd scripts/
./quick-dev-deploy.sh
```

This script handles everything automatically via **Helmfile**:
- ✅ Pre-flight checks (kubectl, helm, **helmfile**, cluster connectivity)
- ✅ Creates secrets from `.env.secrets`
- ✅ **Deploys ArgoCD via Helmfile** (not manual installation)
- ✅ Deploys root App-of-Apps
- ✅ Provides access instructions

## 📋 Manual Deployment Process (Helmfile-based)

### Step 1: Create Base Secrets 🔐
```bash
cd scripts/
./create-dev-secrets.sh
```

### Step 2: Deploy ArgoCD via Helmfile 🛠️
```bash
cd helm/
helm repo add argocd https://argoproj.github.io/argo-helm
helm repo update
helmfile --selector app=argocd sync
```

### Step 3: Deploy Root Application 📦
```bash
kubectl apply -f argocd-manifests/root-app.yaml
```

### Step 4: Monitor ArgoCD Sync Waves ⏱️
ArgoCD automatically deploys in this order:
```
Wave -3: argocd-system (if using argocd-system.yaml)
Wave -2: setup-secrets (External Secrets Operator)
Wave -1: mongo, redis, qdrant (Databases)  
Wave  0: application-backend, application-frontend (Apps)
Wave  1: prometheus-stack, loki, promtail (Monitoring)
```

## 🔧 Complete Manual Alternative (Helmfile-based)
```bash
cd scripts/
./deploy-manual-steps-helmfile.sh
```

## 📁 Helmfile Structure
```
helm/
├── helmfile.yaml          # Main orchestration file
├── charts/
│   ├── argocd/
│   │   ├── helmfile.yaml  # ArgoCD-specific config  
│   │   └── argocd-values.yaml
│   ├── legal-backend/
│   ├── legal-frontend/
│   └── setup-secrets/
└── values/               # Environment-specific values
```

## � Verification Tools
```bash
# Verify helmfile paths and configuration
./scripts/verify-helmfile-paths.sh

# Check helmfile releases
cd helm/
helmfile list
helmfile --selector app=argocd list
```

## 🌐 Access ArgoCD UI

1. **Port Forward:**
   ```bash
   kubectl port-forward svc/argocd-server -n argocd 8080:80
   ```

2. **Access URL:** http://localhost:8080 (insecure mode for development)

3. **Get Admin Password:**
   ```bash
   kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath='{.data.password}' | base64 -d
   ```

## 🚨 Important Notes
- **Never commit `.env.secrets`** - contains sensitive data
- **ArgoCD is auto-installed** by deployment scripts if not present
- **External Secrets Operator** is deployed automatically via sync-wave -2
- **Databases deploy before applications** via sync-wave ordering

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
