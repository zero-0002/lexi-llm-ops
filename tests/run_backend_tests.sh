#!/bin/bash
# COMPREHENSIVE BACKEND TEST LAUNCHER

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Default parameters
BASE_URL="http://localhost:8000"
OUTPUT_DIR="tests/results"
CONCURRENT_USERS=3
VERBOSE=false

# Help function
show_help() {
    echo "COMPREHENSIVE BACKEND TEST LAUNCHER"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -u, --url URL            Backend URL to test (default: http://localhost:8000)"
    echo "  -o, --output DIR         Output directory for results (default: tests/results)"
    echo "  -c, --concurrent NUM     Number of concurrent users (default: 3)"
    echo "  -v, --verbose            Show verbose output"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                       # Test with default settings"
    echo "  $0 -u http://api:8000    # Test different URL"
    echo "  $0 -c 5 -v              # 5 concurrent users with verbose output"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--url)
            BASE_URL="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -c|--concurrent)
            CONCURRENT_USERS="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

echo -e "${GREEN}COMPREHENSIVE BACKEND TEST LAUNCHER${NC}"
echo -e "${YELLOW}=====================================${NC}"

# Ensure we're in the right directory
if [[ ! -d "src" ]]; then
    echo -e "${RED}Please run from project root directory (where 'src' folder exists)${NC}"
    exit 1
fi

echo -e "${GREEN}Project directory: $(pwd)${NC}"

# Check if server is running
echo -e "${CYAN}Checking server availability...${NC}"

if curl -s --connect-timeout 5 "$BASE_URL/health" >/dev/null 2>&1; then
    echo -e "${GREEN}Server is running and accessible${NC}"
else
    echo -e "${RED}Server is not accessible at $BASE_URL${NC}"
    echo -e "${YELLOW}Please ensure the backend server is running:${NC}"
    echo -e "${CYAN}  cd src && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000${NC}"
    exit 1
fi

# Create necessary directories
mkdir -p tests/api tests/logs tests/results

echo -e "${GREEN}Test directories ready${NC}"

# Run comprehensive backend test
echo -e "\n${CYAN}Running Comprehensive Backend Test Suite...${NC}"
echo -e "   ${WHITE}Base URL: $BASE_URL${NC}"
echo -e "   ${WHITE}Output Directory: $OUTPUT_DIR${NC}"
echo -e "   ${WHITE}Concurrent Users: $CONCURRENT_USERS${NC}"

# Build arguments array
arguments=(
    "tests/api/comprehensive_backend_test.py"
    "--url" "$BASE_URL"
    "--output" "$OUTPUT_DIR"
    "--concurrent" "$CONCURRENT_USERS"
)

if [[ "$VERBOSE" == "true" ]]; then
    arguments+=("--verbose")
fi

# Run the test
if python "${arguments[@]}"; then
    exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        echo -e "\n${GREEN}BACKEND TESTING COMPLETED SUCCESSFULLY!${NC}"
        echo -e "${CYAN}Check results in: $OUTPUT_DIR${NC}"
    else
        echo -e "\n${YELLOW}Backend testing completed with issues (exit code: $exit_code)${NC}"
    fi
else
    echo -e "\n${RED}Failed to run backend tests${NC}"
    exit 1
fi

# Show results summary
summary_files=($(find "$OUTPUT_DIR" -name "test_summary_*.json" -type f 2>/dev/null | sort -r))

if [[ ${#summary_files[@]} -gt 0 ]]; then
    latest_summary="${summary_files[0]}"
    
    echo -e "\n${YELLOW}QUICK SUMMARY:${NC}"
    
    # Extract values using jq if available, otherwise use grep/sed
    if command -v jq >/dev/null 2>&1; then
        success_rate=$(jq -r '.api_testing.success_rate // "N/A"' "$latest_summary" 2>/dev/null)
        total_tests=$(jq -r '.api_testing.total_tests // "N/A"' "$latest_summary" 2>/dev/null)
        avg_response=$(jq -r '.api_testing.average_response_time_ms // "N/A"' "$latest_summary" 2>/dev/null)
        duration=$(jq -r '.execution_time.duration_minutes // "N/A"' "$latest_summary" 2>/dev/null)
    else
        # Fallback parsing without jq
        success_rate=$(grep -o '"success_rate":[^,]*' "$latest_summary" 2>/dev/null | cut -d':' -f2 | tr -d ' "' || echo "N/A")
        total_tests=$(grep -o '"total_tests":[^,]*' "$latest_summary" 2>/dev/null | cut -d':' -f2 | tr -d ' "' || echo "N/A")
        avg_response=$(grep -o '"average_response_time_ms":[^,]*' "$latest_summary" 2>/dev/null | cut -d':' -f2 | tr -d ' "' || echo "N/A")
        duration=$(grep -o '"duration_minutes":[^,]*' "$latest_summary" 2>/dev/null | cut -d':' -f2 | tr -d ' "' || echo "N/A")
    fi
    
    # Color based on success rate
    if [[ "$success_rate" != "N/A" ]] && [[ $(echo "$success_rate >= 90" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then
        success_color="${GREEN}"
    else
        success_color="${YELLOW}"
    fi
    
    echo -e "   ${success_color}Success Rate: ${success_rate}%${NC}"
    echo -e "   ${WHITE}Total Tests: $total_tests${NC}"
    echo -e "   ${WHITE}Avg Response: ${avg_response}ms${NC}"
    echo -e "   ${WHITE}Duration: $duration minutes${NC}"
fi

echo -e "\n${CYAN}Results Location: $OUTPUT_DIR${NC}"
echo -e "${CYAN}View detailed results in the CSV files generated${NC}"
