#!/bin/bash
# Legal Retrieval System - Project Cleanup Script
# ================================================

echo "🧹 CLEANING UP PROJECT STRUCTURE"
echo "================================"

# Create directories if they don't exist
echo "📁 Creating organized directories..."
mkdir -p tests/api tests/integration tests/artifacts
mkdir -p reports docs/analysis

echo "📦 Removing redundant Docker Compose files..."
# Remove broken/backup compose files
rm -f docker-compose.backup.yml
rm -f docker-compose.broken.yml
rm -f docker-compose.corrupted.yml
echo "  ✅ Removed broken/backup compose files"

echo "🧪 Moving test files to tests directory..."
# Move test scripts to appropriate locations
[ -f test_analyze_api.py ] && mv test_analyze_api.py tests/api/
[ -f test_backend_api_comprehensive.py ] && mv test_backend_api_comprehensive.py tests/api/
[ -f test_comprehensive_system.py ] && mv test_comprehensive_system.py tests/integration/
[ -f test_final_system.py ] && mv test_final_system.py tests/integration/
[ -f test_streaming_responses.py ] && mv test_streaming_responses.py tests/api/

# Move test artifacts
[ -f test_analyze.json ] && mv test_analyze.json tests/artifacts/
[ -f test_message.json ] && mv test_message.json tests/artifacts/
[ -f test_query.json ] && mv test_query.json tests/artifacts/
[ -f test_query_simple.json ] && mv test_query_simple.json tests/artifacts/

echo "  ✅ Moved test files to tests/ directory"

echo "📚 Organizing reports and documentation..."
# Move reports
[ -f API_TEST_REPORT.md ] && mv API_TEST_REPORT.md reports/
[ -f DEPLOYMENT_SUCCESS_REPORT.md ] && mv DEPLOYMENT_SUCCESS_REPORT.md reports/
[ -f OPTIMIZATION_REPORT.md ] && mv OPTIMIZATION_REPORT.md reports/
[ -f ROOT_CAUSE_ANALYSIS.md ] && mv ROOT_CAUSE_ANALYSIS.md reports/

echo "  ✅ Organized documentation"

# Clean up Python cache
echo "🗑️ Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

echo ""
echo "🎉 CLEANUP COMPLETED!"
echo "📁 New structure:"
echo "  ├── docker-compose.yml (main)"
echo "  ├── docker-compose.test.yml (testing)" 
echo "  ├── docker-compose.optimized.yml (production)"
echo "  ├── tests/ (all test files)"
echo "  ├── docs/ (documentation)"
echo "  └── reports/ (analysis reports)"
echo ""
echo "📊 Next steps:"
echo "  1. Review docker-compose.yml"
echo "  2. Run: docker-compose up --build -d"
echo "  3. Test: python tests/api/test_comprehensive_api.py"
