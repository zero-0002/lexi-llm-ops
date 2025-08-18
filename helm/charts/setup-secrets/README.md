# Setup-Secrets Chart

Helm chart đơn giản để tạo và quản lý secrets cho Legal Retrieval System.

## 📋 Tính năng

- ✅ Tạo secrets trực tiếp từ values.yaml
- ✅ Hỗ trợ load values từ .env file
- ✅ Tạo secrets riêng biệt cho backend, frontend, celery worker
- ✅ Sử dụng `envFrom` để load environment variables
- ✅ Không cần External Secrets Operator

## 🏗️ Cấu trúc

```
setup-secrets/
├── Chart.yaml                 # Chart metadata
├── values.yaml                # Configuration values
├── templates/
│   ├── base-secrets.yaml      # Secret templates
│   └── _helpers.tpl           # Helper templates
└── README.md                  # Tài liệu này
```

## 📦 Secrets được tạo

1. **legal-backend-secret** - Environment variables cho backend
   - `MONGO_USERNAME`, `MONGO_PASSWORD`
   - `REDIS_PASSWORD`
   - `OPENAI_API_KEY`
   - `JWT_SECRET`, `SECRET_KEY`, `ENCRYPTION_KEY`

2. **legal-frontend-secret** - Environment variables cho frontend
   - `REACT_APP_API_BASE_URL`
   - `REACT_APP_GOOGLE_ANALYTICS_ID`
   - `REACT_APP_ENABLE_ANALYTICS`

3. **legal-celery-worker-secret** - Environment variables cho celery worker
   - Tất cả từ backend secret
   - `CELERY_BROKER_PASSWORD`, `CELERY_RESULT_BACKEND_PASSWORD`

## 🚀 Cách sử dụng

### 1. Cập nhật values từ .env file

```bash
cd scripts/
./update-values-from-env.sh
```

### 2. Deploy chart

```bash
# Sử dụng helmfile
helmfile -f helm/helmfile.yaml apply --selector name=setup-secrets

# Hoặc sử dụng helm trực tiếp
helm install setup-secrets helm/charts/setup-secrets -n secrets-management --create-namespace
```

### 3. Sử dụng trong deployment

```yaml
spec:
  template:
    spec:
      containers:
      - name: your-app
        image: your-image
        # 🔑 Load tất cả environment variables
        envFrom:
        - secretRef:
            name: legal-backend-secret        # Cho backend
            # legal-frontend-secret           # Cho frontend  
            # legal-celery-worker-secret      # Cho celery worker
```

## 🔧 Scripts hỗ trợ

- `scripts/create-dev-secrets.sh` - Tạo base secrets từ .env
- `scripts/update-values-from-env.sh` - Cập nhật values.yaml từ .env

## 📝 Examples

Xem file `docs/envfrom-deployment-examples.yaml` để có ví dụ deployment hoàn chỉnh.

## ⚠️ Lưu ý bảo mật

- ❌ Không commit file `.env` vào git
- ✅ Sử dụng file `.env.example` cho template
- ✅ Trong production, sử dụng External Secrets hoặc cloud secret managers
- ✅ Định kỳ rotate secrets và API keys
