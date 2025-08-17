#!/bin/bash
# Docker Test Management Script
# ============================
# Comprehensive test execution and management for Legal Retrieval System

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.test.yml"
PROJECT_NAME="legal-retrieval-test"
RESULTS_DIR="./tests/results"
LOGS_DIR="./tests/logs"

# Ensure directories exist
mkdir -p "$RESULTS_DIR" "$LOGS_DIR"

# Functions
print_banner() {
    echo -e "${BLUE}"
    echo "========================================"
    echo "  Legal Retrieval System - Test Suite"
    echo "========================================"
    echo -e "${NC}"
}

print_step() {
    echo -e "${YELLOW}==> $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check dependencies
check_dependencies() {
    print_step "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    print_success "Dependencies checked"
}

# Environment setup
setup_environment() {
    print_step "Setting up test environment..."
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        print_error ".env file not found. Please copy from .env.example"
        exit 1
    fi
    
    # Validate required environment variables
    source .env
    
    if [ -z "$OPENAI_API_KEY" ]; then
        print_error "OPENAI_API_KEY not set in .env file"
        exit 1
    fi
    
    print_success "Environment setup complete"
}

# Start test infrastructure
start_infrastructure() {
    print_step "Starting test infrastructure..."
    
    # Stop any existing test containers
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down --remove-orphans 2>/dev/null || true
    
    # Start test infrastructure
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d --build
    
    print_info "Waiting for services to be ready..."
    
    # Wait for services to be healthy
    max_attempts=60  # 5 minutes max
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps | grep -q "healthy"; then
            print_success "Test infrastructure is ready"
            return 0
        fi
        
        sleep 5
        attempt=$((attempt + 1))
        echo -n "."
    done
    
    print_error "Test infrastructure failed to start within timeout"
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs
    exit 1
}

# Health check
health_check() {
    print_step "Performing health checks..."
    
    # Check API health
    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
        print_success "Backend API is healthy"
    else
        print_error "Backend API health check failed"
        return 1
    fi
    
    # Check database connections
    if docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" exec -T mongodb-test mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
        print_success "MongoDB is healthy"
    else
        print_error "MongoDB health check failed"
        return 1
    fi
    
    if docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" exec -T redis-test redis-cli ping > /dev/null 2>&1; then
        print_success "Redis is healthy"
    else
        print_error "Redis health check failed"
        return 1
    fi
    
    if curl -f http://localhost:6335/health > /dev/null 2>&1; then
        print_success "Qdrant is healthy"
    else
        print_error "Qdrant health check failed"
        return 1
    fi
    
    print_success "All health checks passed"
}

# Run tests
run_tests() {
    local test_type="$1"
    print_step "Running tests: $test_type"
    
    local test_args=""
    local output_file=""
    
    case "$test_type" in
        "smoke")
            test_args="-m smoke"
            output_file="smoke_test_results.xml"
            ;;
        "api")
            test_args="-m api"
            output_file="api_test_results.xml"
            ;;
        "database")
            test_args="-m database"
            output_file="database_test_results.xml"
            ;;
        "websocket")
            test_args="-m websocket"
            output_file="websocket_test_results.xml"
            ;;
        "integration")
            test_args="-m integration"
            output_file="integration_test_results.xml"
            ;;
        "performance")
            test_args="-m performance"
            output_file="performance_test_results.xml"
            ;;
        "all")
            test_args=""
            output_file="all_test_results.xml"
            ;;
        *)
            print_error "Unknown test type: $test_type"
            return 1
            ;;
    esac
    
    # Run tests in test runner container
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" exec -T test-runner \
        python -m pytest /app/tests \
        $test_args \
        --junitxml="/app/results/$output_file" \
        --html="/app/results/${test_type}_report.html" \
        --self-contained-html \
        --json-report \
        --json-report-file="/app/results/${test_type}_report.json" \
        --tb=short \
        --color=yes \
        -v
    
    local exit_code=$?
    
    # Copy results to host
    docker cp "$(docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps -q test-runner):/app/results/." "$RESULTS_DIR/"
    docker cp "$(docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps -q test-runner):/app/logs/." "$LOGS_DIR/"
    
    if [ $exit_code -eq 0 ]; then
        print_success "Tests passed: $test_type"
    else
        print_error "Tests failed: $test_type"
    fi
    
    return $exit_code
}

# Generate test report
generate_report() {
    print_step "Generating test report..."
    
    cat > "$RESULTS_DIR/test_summary.md" << EOF
# Legal Retrieval System - Test Results

**Test Execution Date:** $(date)
**Environment:** Docker Test Environment

## Test Results Summary

EOF
    
    # Process each test result file
    for result_file in "$RESULTS_DIR"/*.json; do
        if [ -f "$result_file" ]; then
            test_name=$(basename "$result_file" .json | sed 's/_report//')
            echo "### $test_name Tests" >> "$RESULTS_DIR/test_summary.md"
            
            # Extract summary from JSON (simplified)
            if command -v jq &> /dev/null; then
                jq -r '"- Total: \(.summary.total // "N/A") tests\n- Passed: \(.summary.passed // "N/A")\n- Failed: \(.summary.failed // "N/A")\n- Skipped: \(.summary.skipped // "N/A")\n- Duration: \(.duration // "N/A")s\n"' "$result_file" >> "$RESULTS_DIR/test_summary.md"
            else
                echo "- Results available in $result_file" >> "$RESULTS_DIR/test_summary.md"
            fi
            
            echo "" >> "$RESULTS_DIR/test_summary.md"
        fi
    done
    
    cat >> "$RESULTS_DIR/test_summary.md" << EOF

## Service Status

EOF
    
    # Add service status
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps >> "$RESULTS_DIR/test_summary.md"
    
    print_success "Test report generated: $RESULTS_DIR/test_summary.md"
}

# Cleanup
cleanup() {
    print_step "Cleaning up test environment..."
    
    # Stop and remove test containers
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down --remove-orphans
    
    print_success "Cleanup complete"
}

# Show logs
show_logs() {
    local service="$1"
    if [ -n "$service" ]; then
        docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs -f "$service"
    else
        docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs -f
    fi
}

# Show help
show_help() {
    cat << EOF
Docker Test Management Script for Legal Retrieval System

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    start           Start test infrastructure only
    test [TYPE]     Run specific test type
    full            Run complete test suite
    stop            Stop test infrastructure
    cleanup         Stop and cleanup test environment
    logs [SERVICE]  Show logs for service (or all if not specified)
    health          Run health checks
    report          Generate test report from existing results
    help            Show this help message

Test Types:
    smoke           Quick smoke tests
    api             API endpoint tests
    database        Database integration tests
    websocket       WebSocket functionality tests
    integration     Full integration tests
    performance     Performance tests
    all             All tests

Examples:
    $0 full                    # Run complete test suite
    $0 test api               # Run API tests only
    $0 test smoke             # Run smoke tests
    $0 logs backend-api-test  # Show backend API logs
    $0 health                 # Check service health

Environment:
    Requires .env file with OPENAI_API_KEY
    Uses docker-compose.test.yml for test infrastructure

Results:
    Test results: ./tests/results/
    Test logs: ./tests/logs/
EOF
}

# Main execution
main() {
    local command="$1"
    local arg="$2"
    
    case "$command" in
        "start")
            print_banner
            check_dependencies
            setup_environment
            start_infrastructure
            health_check
            print_success "Test infrastructure started successfully"
            ;;
        "test")
            if [ -z "$arg" ]; then
                print_error "Test type required. Use: smoke, api, database, websocket, integration, performance, or all"
                exit 1
            fi
            print_banner
            check_dependencies
            setup_environment
            start_infrastructure
            health_check
            run_tests "$arg"
            ;;
        "full")
            print_banner
            check_dependencies
            setup_environment
            start_infrastructure
            health_check
            
            # Run all test types
            local overall_result=0
            for test_type in smoke api database websocket integration; do
                if ! run_tests "$test_type"; then
                    overall_result=1
                fi
                echo ""
            done
            
            generate_report
            
            if [ $overall_result -eq 0 ]; then
                print_success "All tests completed successfully!"
            else
                print_error "Some tests failed. Check results for details."
            fi
            
            exit $overall_result
            ;;
        "stop")
            print_step "Stopping test infrastructure..."
            docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" stop
            print_success "Test infrastructure stopped"
            ;;
        "cleanup")
            cleanup
            ;;
        "logs")
            show_logs "$arg"
            ;;
        "health")
            health_check
            ;;
        "report")
            generate_report
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        "")
            print_error "Command required"
            show_help
            exit 1
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Execute main function with all arguments
main "$@"
