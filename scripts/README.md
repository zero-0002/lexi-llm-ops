# Scripts Documentation
## Clean and Simple Setup

### 🚀 Main Scripts

#### **create-dev-secrets.sh**
- Creates Kubernetes secrets from `.env` file
- Simple and straightforward
- Usage: `./create-dev-secrets.sh`

#### **deploy-manual-steps.sh** 
- Simple step-by-step deployment
- Creates secrets → Deploys databases → Apps
- Usage: `./deploy-manual-steps.sh`

#### **test-helmfile-connection.sh**
- Tests helmfile selectors work correctly
- Verifies ArgoCD integration
- Usage: `./test-helmfile-connection.sh`

### 📦 Docker Scripts
- `build-docker.sh` - Build Docker images
- `docker-summary.sh` - Docker system summary

### 🧹 Maintenance Scripts
- `cleanup-project.sh` - Clean up project resources
- `system-check.sh` - System health check

### 📁 Archived Scripts
Complex scripts moved to `archived/` folder:
- `deploy-secrets-first.sh`
- `migrate-secrets-store.sh` 
- `setup-secrets-store.sh`
- `troubleshoot-secrets.sh`
- `verify-secrets.sh`

### 🔧 Setup Process

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

2. **Create secrets:**
   ```bash
   ./scripts/create-dev-secrets.sh
   ```

3. **Deploy everything:**
   ```bash
   ./scripts/deploy-manual-steps.sh
   ```

4. **Verify deployment:**
   ```bash
   kubectl get applications -n argocd
   kubectl get pods -A | grep legal-
   ```

### ⚠️ Important Notes
- Secrets are created from `.env` file (never commit real secrets)
- Uses `secrets-store` namespace for local development
- Simple Kubernetes-based External Secrets setup
