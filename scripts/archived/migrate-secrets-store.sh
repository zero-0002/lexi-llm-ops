#!/bin/bash
# 🔄 Secrets Store Migration Strategy
# ==================================

set -e

ENVIRONMENT=${1:-development}
PROVIDER=${2:-kubernetes}

echo "🔄 Secrets Store Migration for Environment: $ENVIRONMENT"
echo "Provider: $PROVIDER"
echo "==========================================================="

case $ENVIRONMENT in
  "development")
    echo "🔧 Development Environment Setup"
    echo "Using Kubernetes secrets in 'secrets-store' namespace"
    
    # Create secrets-store namespace
    kubectl create namespace secrets-store --dry-run=client -o yaml | kubectl apply -f -
    kubectl label namespace secrets-store purpose=secrets-storage environment=development --overwrite
    
    # Deploy with kubernetes provider
    cd helm
    helmfile -l app=setup-secrets -e development sync
    ;;
    
  "staging")
    echo "🏗️ Staging Environment Setup"
    
    if [ "$PROVIDER" = "aws" ]; then
      echo "Using AWS Secrets Manager"
      
      # Update Secret Store to use AWS
      kubectl patch secretstore legal-secret-store -n application --type='merge' -p='{"spec":{"provider":{"aws":{"service":"SecretsManager","region":"us-west-2"}}}}'
      
    elif [ "$PROVIDER" = "azure" ]; then
      echo "Using Azure Key Vault"
      # Azure configuration
      kubectl patch secretstore legal-secret-store -n application --type='merge' -p='{"spec":{"provider":{"azurekv":{"vaultUrl":"https://legal-staging-kv.vault.azure.net/"}}}}'
      
    fi
    ;;
    
  "production")
    echo "🚀 Production Environment Setup"
    echo "⚠️  WARNING: This will migrate from local secrets to cloud provider"
    echo "⚠️  Ensure cloud secrets are properly configured before proceeding"
    
    read -p "Are you sure you want to proceed with production migration? (y/N): " confirm
    if [ "$confirm" != "y" ]; then
      echo "Migration cancelled"
      exit 0
    fi
    
    if [ "$PROVIDER" = "aws" ]; then
      echo "🌩️ Migrating to AWS Secrets Manager"
      
      # Backup current secrets
      echo "📦 Backing up current secrets..."
      kubectl get secrets -n secrets-store -o yaml > secrets-backup-$(date +%Y%m%d-%H%M%S).yaml
      
      # Update to AWS provider
      cd helm
      helmfile -l app=setup-secrets -e production --set secretStore.provider=aws sync
      
    fi
    ;;
    
  *)
    echo "❌ Invalid environment. Use: development, staging, or production"
    exit 1
    ;;
esac

echo ""
echo "✅ Migration completed for $ENVIRONMENT environment"
echo ""
echo "🔍 Verification commands:"
echo "kubectl get secretstore -A"
echo "kubectl get externalsecrets -A"
echo "kubectl get secrets -A | grep legal-"
