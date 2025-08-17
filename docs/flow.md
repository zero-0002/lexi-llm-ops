# 📂 Legal Chatbot RAG System - AWS Deployment

## 1. 🎯 Mục tiêu Project
Triển khai hệ thống **Legal Chatbot RAG System** trên AWS sử dụng:
- **EKS** để quản lý app backend, frontend, monitoring.
- **S3 + Qdrant + MongoDB** cho lưu trữ dữ liệu.
- **Airflow + SageMaker + MLflow** cho pipeline ML.
- **ArgoCD + Helmfile** để GitOps triển khai.

---

## 2. 📊 Kanban Board
*(Import file aws_project_plan_kanban.csv vào bảng Kanban của Notion, group theo Phase hoặc Status)*

---

## 3. 🗺 AWS Architecture Diagram
*(Upload diagram PNG/JPG tại đây)*

💡 **Ghi chú Flow:**
- Namespace `app`: API, Celery, Redis, MongoDB, Qdrant.
- Namespace `ml`: Airflow, MLflow, SageMaker jobs.
- Namespace `monitoring`: Loki, Grafana, Promtail.
- Data Flow: Crawl → Store (S3/Qdrant) → Retrieval → LLM → User.

---

## 4. ✅ Checklist lỗi hay gặp & fix nhanh
**Helmfile deploy lỗi chart không tìm thấy**
- Fix: `helm repo update` trước khi deploy.

**EKS pods CrashLoopBackOff**
- Fix: `kubectl logs -n <ns> <pod>` để xem log, thường do thiếu env hoặc config map.

**Ingress không vào được**
- Fix: Check ALB Ingress Controller logs, verify target group healthy.

**Airflow DAG không trigger**
- Fix: Check scheduler logs, verify DAG path mount đúng.

---

## 5. 🛠 Hướng dẫn triển khai P1 → P6

### P1 - Infra
```bash
eksctl create cluster --name legal-chatbot --region ap-southeast-1 --nodes 2 --node-type t3.medium


helm upgrade --install aws-load-balancer-controller eks/aws-load-balancer-controller -n kube-system ...
P2 - App

helm install mongo bitnami/mongodb -n app
helm install qdrant qdrant/qdrant -n app
helm install redis bitnami/redis -n app
P3 - Monitoring
helm install loki grafana/loki-stack -n monitoring
P4 - ML/Data
helm install airflow apache/airflow -n ml
P5 - Frontend
kubectl apply -f fe-deployment.yaml -n app
P6 - Optimize/Docs
HPA config:

kubectl autoscale deployment api --cpu-percent=50 --min=1 --max=3 -n app
6. 📂 Tài nguyên & Link
Helmfile repo: [GitHub link]

AWS Console: [link]

ArgoCD: [link]

Grafana Dashboard: [link]

---