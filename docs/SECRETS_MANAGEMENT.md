# 🔐 Secrets vs Configuration Management
## Clean Architecture for Security and Configuration

### 📁 **File Structure**

```
📄 .env.secrets           # 🔐 SECRETS ONLY (never commit)
📄 .env.config            # ⚙️ System configuration  
📄 .env.example           # 📝 Template with dummy values
📄 helm/values/*.yaml     # ⚙️ Kubernetes configuration
```

### 🔐 **Secrets (.env.secrets)**

Contains ONLY sensitive data:
- Database passwords
- API keys (OpenAI, SERPER)
- JWT secrets
- Encryption keys

```bash
# Database Secrets
MONGODB_PASSWORD=secure-password
REDIS_PASSWORD=redis-password

# API Keys
OPENAI_API_KEY=sk-...
SERPER_API_KEY=...

# Security Secrets
SECRET_KEY=...
JWT_SECRET=...
ENCRYPTION_KEY=...
```

### ⚙️ **System Configuration (.env.config)**

Contains NON-sensitive system settings:
- Database URLs (without passwords)
- Service hostnames
- Port numbers
- Feature flags
- Performance settings

```bash
# Database Configuration
MONGODB_DATABASE=legaldb
MONGODB_USER=legal_user
REDIS_URL=redis://localhost:6379

# Application Configuration
APP_NAME=Legal Retrieval System
DEBUG=true
LOG_LEVEL=INFO
```

### 🎯 **Helm Values (helm/values/*.yaml)**

Kubernetes-specific configuration:
- Service names
- Resource limits
- Networking settings
- Environment-specific config

```yaml
# System Environment Variables (non-secret)
env:
  APP_NAME: "Legal Retrieval System"
  DEBUG: "true"
  MONGO_HOST: "legal-mongodb.data-service.svc.cluster.local"
  REDIS_HOST: "legal-redis-master.data-service.svc.cluster.local"

# Secrets injected via External Secrets
# No secrets in values files!
```

### 🔄 **How It Works**

1. **Development**:
   ```bash
   # 1. Create secrets from .env.secrets
   ./scripts/create-dev-secrets.sh
   
   # 2. System config from Helm values
   helm template -f values/backend-api.yaml
   ```

2. **Kubernetes Pods**:
   - **System config** → Environment variables from values
   - **Secrets** → Environment variables from External Secrets
   - **Combined** → Complete configuration in pod

3. **Security Benefits**:
   - ✅ Secrets never in git repository
   - ✅ Secrets managed separately from config
   - ✅ Easy to rotate secrets without changing config
   - ✅ Different secrets per environment

### 🛡️ **Security Best Practices**

- **Never commit** `.env.secrets` to git
- **Always use** External Secrets in Kubernetes
- **Separate** secrets from configuration
- **Use different** secrets per environment
- **Rotate secrets** regularly
- **Audit** secret access

### 📝 **Usage Examples**

#### Creating Secrets:
```bash
# Copy and edit secrets
cp .env.example .env.secrets
vim .env.secrets  # Add real secrets

# Create K8s secrets
./scripts/create-dev-secrets.sh
```

#### Checking Configuration:
```bash
# System config only
cat .env.config

# Helm values (no secrets)
cat helm/values/backend-api.yaml

# Secrets in K8s (encrypted)
kubectl get secret legal-backend-secret -n application -o yaml
```

This architecture ensures **security** while maintaining **flexibility** for configuration management! 🔐✅
