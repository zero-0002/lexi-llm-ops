#!/bin/bash
# 🚀 Simple Deployment Steps
# =========================

set -e

echo "🔐 Step 1: Create Development Secrets from .env"
echo "==============================================="
./create-dev-secrets.sh

echo ""
echo "📦 Step 2: Deploy External Secrets System"
echo "========================================="
kubectl apply -f ../argocd-manifests/apps/setup-secrets.yaml

echo "⏳ Waiting for secrets to be ready..."
sleep 30

echo ""
echo "🗄️ Step 3: Deploy Databases"
echo "=========================="
kubectl apply -f ../argocd-manifests/apps/mongo.yaml
kubectl apply -f ../argocd-manifests/apps/redis.yaml
kubectl apply -f ../argocd-manifests/apps/qdrant.yaml

echo ""
echo "📊 Step 4: Deploy Monitoring"
echo "==========================="
kubectl apply -f ../argocd-manifests/apps/prometheus-stack.yaml
kubectl apply -f ../argocd-manifests/apps/loki.yaml

echo ""
echo "🚀 Step 5: Deploy Applications"
echo "============================="
kubectl apply -f ../argocd-manifests/apps/application-backend.yaml
kubectl apply -f ../argocd-manifests/apps/application-frontend.yaml

echo ""
echo "📋 Step 6: Deploy Promtail"
echo "=========================="
sleep 30
kubectl apply -f ../argocd-manifests/apps/promtail.yaml

echo ""
echo "✅ Deployment Complete!"
echo "======================="
kubectl get applications -n argocd
kubectl get pods -A | grep legal-
