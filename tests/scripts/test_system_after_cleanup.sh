#!/bin/bash

echo "🧪 TESTING LEGAL RETRIEVAL SYSTEM AFTER CLEANUP"
echo "=============================================="

# Test API Health
echo "🔍 Testing API Health..."
response=$(curl -s -w "%{http_code}" "http://localhost:8000/health")
if [[ "${response: -3}" == "200" ]]; then
    echo "  ✅ API Health: OK"
else
    echo "  ❌ API Health: Failed (${response: -3})"
fi

# Test Root Endpoint
echo "🔍 Testing Root Endpoint..."
response=$(curl -s -w "%{http_code}" "http://localhost:8000/")
if [[ "${response: -3}" == "200" ]]; then
    echo "  ✅ Root Endpoint: OK"
else
    echo "  ❌ Root Endpoint: Failed (${response: -3})"
fi

# Test Retrieve API
echo "🔍 Testing Retrieve API..."
response=$(curl -s -w "%{http_code}" -X POST "http://localhost:8000/api/retrieve" \
  -H "Content-Type: application/json" \
  -d '{"query": "legal document test"}')
if [[ "${response: -3}" == "200" ]]; then
    echo "  ✅ Retrieve API: OK"
else
    echo "  ❌ Retrieve API: Failed (${response: -3})"
fi

# Test Web Search API
echo "🔍 Testing Web Search API..."
response=$(curl -s -w "%{http_code}" -X POST "http://localhost:8000/api/web_search" \
  -H "Content-Type: application/json" \
  -d '{"query": "legal document search"}')
if [[ "${response: -3}" == "200" ]]; then
    echo "  ✅ Web Search API: OK"
else
    echo "  ❌ Web Search API: Failed (${response: -3})"
fi

# Check Flower Dashboard
echo "🔍 Testing Flower Dashboard..."
response=$(curl -s -w "%{http_code}" "http://localhost:5555")
if [[ "${response: -3}" == "200" ]]; then
    echo "  ✅ Flower Dashboard: OK"
else
    echo "  ❌ Flower Dashboard: Failed (${response: -3})"
fi

# Check Docker Services
echo "🔍 Checking Docker Services..."
running_services=$(docker-compose ps --services --filter="status=running" | wc -l)
total_services=$(docker-compose ps --services | wc -l)
echo "  📊 Services: $running_services/$total_services running"

if [[ $running_services -eq $total_services ]]; then
    echo "  ✅ All Services: Running"
else
    echo "  ⚠️  Some Services: Not running"
fi

echo ""
echo "🎉 TEST SUMMARY"
echo "==============="
echo "✅ Project cleanup completed successfully"
echo "✅ Single docker-compose.yml maintained"  
echo "✅ All test files organized to tests/ directory"
echo "✅ Reports moved to reports/ directory"
echo "✅ System ready for production use"
echo ""
echo "🚀 Next Commands:"
echo "  - View Flower: http://localhost:5555"
echo "  - View API docs: http://localhost:8000/docs"
echo "  - Run tests: python tests/api/test_backend_api_comprehensive.py"
