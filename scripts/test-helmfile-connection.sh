#!/bin/bash

# Script để test kết nối helmfile với ArgoCD
echo "🔍 Testing Helmfile ArgoCD Integration..."

cd helm/

echo "📋 Testing individual app selectors:"
echo ""

# Test backend app
echo "🚀 Testing legal-backend..."
helmfile -l app=legal-backend template --include-crds > /tmp/backend-test.yaml
if [ $? -eq 0 ]; then
    echo "✅ Backend selector works"
    echo "   Generated $(cat /tmp/backend-test.yaml | wc -l) lines"
else
    echo "❌ Backend selector failed"
fi

# Test frontend app
echo "🖥️  Testing legal-frontend..."
helmfile -l app=legal-frontend template --include-crds > /tmp/frontend-test.yaml
if [ $? -eq 0 ]; then
    echo "✅ Frontend selector works"
    echo "   Generated $(cat /tmp/frontend-test.yaml | wc -l) lines"
else
    echo "❌ Frontend selector failed"
fi

# Test monitoring
echo "📊 Testing prometheus-stack..."
helmfile -l app=prometheus-stack template --include-crds > /tmp/prometheus-test.yaml
if [ $? -eq 0 ]; then
    echo "✅ Prometheus selector works"
    echo "   Generated $(cat /tmp/prometheus-test.yaml | wc -l) lines"
else
    echo "❌ Prometheus selector failed"
fi

# Test database
echo "🗄️  Testing legal-mongodb..."
helmfile -l app=legal-mongodb template --include-crds > /tmp/mongodb-test.yaml
if [ $? -eq 0 ]; then
    echo "✅ MongoDB selector works"
    echo "   Generated $(cat /tmp/mongodb-test.yaml | wc -l) lines"
else
    echo "❌ MongoDB selector failed"
fi

echo ""
echo "📈 Summary of all releases in helmfile:"
helmfile list

echo ""
echo "🔧 Available labels:"
helmfile list -o json | jq -r '.[].labels'

echo ""
echo "✅ Test completed!"
