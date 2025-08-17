# Docker Test Management Script for Windows
# ========================================
# Comprehensive test execution and management for Legal Retrieval System

param(
    [string]$Command = "",
    [string]$TestType = "",
    [string]$Service = "",
    [switch]$Help
)

# Configuration
$ComposeFile = "docker-compose.test.yml"
$ProjectName = "legal-retrieval-test"
$ResultsDir = "./tests/results"
$LogsDir = "./tests/logs"

# Ensure directories exist
New-Item -ItemType Directory -Force -Path $ResultsDir | Out-Null
New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null

# Functions
function Write-Banner {
    Write-Host "========================================" -ForegroundColor Blue
    Write-Host "  Legal Retrieval System - Test Suite" -ForegroundColor Blue
    Write-Host "========================================" -ForegroundColor Blue
}

function Write-Step {
    param([string]$Message)
    Write-Host "==> $Message" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

# Check dependencies
function Test-Dependencies {
    Write-Step "Checking dependencies..."
    
    if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "Docker is not installed or not in PATH"
        exit 1
    }
    
    if (!(Get-Command docker-compose -ErrorAction SilentlyContinue)) {
        Write-Error "Docker Compose is not installed or not in PATH"
        exit 1
    }
    
    Write-Success "Dependencies checked"
}

# Environment setup
function Initialize-Environment {
    Write-Step "Setting up test environment..."
    
    # Check if .env file exists
    if (!(Test-Path ".env")) {
        Write-Error ".env file not found. Please copy from .env.example"
        exit 1
    }
    
    # Load environment variables
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^=]+)=(.*)$") {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
    
    # Validate required environment variables
    if (!(Test-Path env:OPENAI_API_KEY) -or [string]::IsNullOrEmpty($env:OPENAI_API_KEY)) {
        Write-Error "OPENAI_API_KEY not set in .env file"
        exit 1
    }
    
    Write-Success "Environment setup complete"
}

# Start test infrastructure
function Start-Infrastructure {
    Write-Step "Starting test infrastructure..."
    
    # Stop any existing test containers
    docker-compose -f $ComposeFile -p $ProjectName down --remove-orphans 2>$null
    
    # Start test infrastructure
    docker-compose -f $ComposeFile -p $ProjectName up -d --build
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to start test infrastructure"
        exit 1
    }
    
    Write-Info "Waiting for services to be ready..."
    
    # Wait for services to be healthy
    $maxAttempts = 60  # 5 minutes max
    $attempt = 0
    
    while ($attempt -lt $maxAttempts) {
        $status = docker-compose -f $ComposeFile -p $ProjectName ps
        if ($status -match "healthy") {
            Write-Success "Test infrastructure is ready"
            return
        }
        
        Start-Sleep -Seconds 5
        $attempt++
        Write-Host "." -NoNewline
    }
    
    Write-Host ""
    Write-Error "Test infrastructure failed to start within timeout"
    docker-compose -f $ComposeFile -p $ProjectName logs
    exit 1
}

# Health check
function Test-Health {
    Write-Step "Performing health checks..."
    
    $healthPassed = $true
    
    # Check API health
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8001/health" -TimeoutSec 10 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Success "Backend API is healthy"
        } else {
            Write-Error "Backend API health check failed"
            $healthPassed = $false
        }
    } catch {
        Write-Error "Backend API health check failed: $($_.Exception.Message)"
        $healthPassed = $false
    }
    
    # Check MongoDB
    $mongoCheck = docker-compose -f $ComposeFile -p $ProjectName exec -T mongodb-test mongosh --eval "db.adminCommand('ping')" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "MongoDB is healthy"
    } else {
        Write-Error "MongoDB health check failed"
        $healthPassed = $false
    }
    
    # Check Redis
    $redisCheck = docker-compose -f $ComposeFile -p $ProjectName exec -T redis-test redis-cli ping 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Redis is healthy"
    } else {
        Write-Error "Redis health check failed"
        $healthPassed = $false
    }
    
    # Check Qdrant
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:6335/health" -TimeoutSec 10 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Success "Qdrant is healthy"
        } else {
            Write-Error "Qdrant health check failed"
            $healthPassed = $false
        }
    } catch {
        Write-Error "Qdrant health check failed: $($_.Exception.Message)"
        $healthPassed = $false
    }
    
    if ($healthPassed) {
        Write-Success "All health checks passed"
    } else {
        Write-Error "Some health checks failed"
        return $false
    }
    
    return $true
}

# Run tests
function Invoke-Tests {
    param([string]$TestType)
    
    Write-Step "Running tests: $TestType"
    
    $testArgs = ""
    $outputFile = ""
    
    switch ($TestType) {
        "smoke" {
            $testArgs = "-m smoke"
            $outputFile = "smoke_test_results.xml"
        }
        "api" {
            $testArgs = "-m api"
            $outputFile = "api_test_results.xml"
        }
        "database" {
            $testArgs = "-m database"
            $outputFile = "database_test_results.xml"
        }
        "websocket" {
            $testArgs = "-m websocket"
            $outputFile = "websocket_test_results.xml"
        }
        "integration" {
            $testArgs = "-m integration"
            $outputFile = "integration_test_results.xml"
        }
        "performance" {
            $testArgs = "-m performance"
            $outputFile = "performance_test_results.xml"
        }
        "all" {
            $testArgs = ""
            $outputFile = "all_test_results.xml"
        }
        default {
            Write-Error "Unknown test type: $TestType"
            return $false
        }
    }
    
    # Run tests in test runner container
    $testCommand = @(
        "python", "-m", "pytest", "/app/tests"
        if ($testArgs) { $testArgs.Split(" ") }
        "--junitxml=/app/results/$outputFile"
        "--html=/app/results/${TestType}_report.html"
        "--self-contained-html"
        "--json-report"
        "--json-report-file=/app/results/${TestType}_report.json"
        "--tb=short"
        "--color=yes"
        "-v"
    ) -join " "
    
    docker-compose -f $ComposeFile -p $ProjectName exec -T test-runner $testCommand
    $exitCode = $LASTEXITCODE
    
    # Copy results to host
    $containerName = docker-compose -f $ComposeFile -p $ProjectName ps -q test-runner
    docker cp "${containerName}:/app/results/." $ResultsDir
    docker cp "${containerName}:/app/logs/." $LogsDir
    
    if ($exitCode -eq 0) {
        Write-Success "Tests passed: $TestType"
        return $true
    } else {
        Write-Error "Tests failed: $TestType"
        return $false
    }
}

# Generate test report
function New-TestReport {
    Write-Step "Generating test report..."
    
    $reportPath = Join-Path $ResultsDir "test_summary.md"
    
    $report = @"
# Legal Retrieval System - Test Results

**Test Execution Date:** $(Get-Date)
**Environment:** Docker Test Environment

## Test Results Summary

"@
    
    # Process each test result file
    Get-ChildItem -Path $ResultsDir -Filter "*.json" | ForEach-Object {
        $testName = $_.BaseName -replace "_report", ""
        $report += "`n### $testName Tests`n"
        
        try {
            $jsonContent = Get-Content $_.FullName | ConvertFrom-Json
            $report += "- Total: $($jsonContent.summary.total) tests`n"
            $report += "- Passed: $($jsonContent.summary.passed)`n"
            $report += "- Failed: $($jsonContent.summary.failed)`n"
            $report += "- Skipped: $($jsonContent.summary.skipped)`n"
            $report += "- Duration: $($jsonContent.duration)s`n`n"
        } catch {
            $report += "- Results available in $($_.Name)`n`n"
        }
    }
    
    $report += "`n## Service Status`n`n"
    
    # Add service status
    $serviceStatus = docker-compose -f $ComposeFile -p $ProjectName ps
    $report += "``````n$serviceStatus`n``````n"
    
    Set-Content -Path $reportPath -Value $report
    
    Write-Success "Test report generated: $reportPath"
}

# Cleanup
function Remove-Infrastructure {
    Write-Step "Cleaning up test environment..."
    
    # Stop and remove test containers
    docker-compose -f $ComposeFile -p $ProjectName down --remove-orphans
    
    Write-Success "Cleanup complete"
}

# Show logs
function Show-Logs {
    param([string]$Service = "")
    
    if ($Service) {
        docker-compose -f $ComposeFile -p $ProjectName logs -f $Service
    } else {
        docker-compose -f $ComposeFile -p $ProjectName logs -f
    }
}

# Show help
function Show-Help {
    Write-Host @"
Docker Test Management Script for Legal Retrieval System

Usage: .\run_docker_tests.ps1 -Command <COMMAND> [OPTIONS]

Commands:
    start           Start test infrastructure only
    test            Run specific test type (requires -TestType)
    full            Run complete test suite
    stop            Stop test infrastructure
    cleanup         Stop and cleanup test environment
    logs            Show logs for service (use -Service parameter)
    health          Run health checks
    report          Generate test report from existing results
    help            Show this help message

Parameters:
    -TestType       Test type: smoke, api, database, websocket, integration, performance, all
    -Service        Service name for logs
    -Help           Show this help message

Examples:
    .\run_docker_tests.ps1 -Command full
    .\run_docker_tests.ps1 -Command test -TestType api
    .\run_docker_tests.ps1 -Command test -TestType smoke
    .\run_docker_tests.ps1 -Command logs -Service backend-api-test
    .\run_docker_tests.ps1 -Command health

Environment:
    Requires .env file with OPENAI_API_KEY
    Uses docker-compose.test.yml for test infrastructure

Results:
    Test results: ./tests/results/
    Test logs: ./tests/logs/
"@
}

# Main execution
function Main {
    if ($Help) {
        Show-Help
        return
    }
    
    switch ($Command.ToLower()) {
        "start" {
            Write-Banner
            Test-Dependencies
            Initialize-Environment
            Start-Infrastructure
            Test-Health
            Write-Success "Test infrastructure started successfully"
        }
        "test" {
            if ([string]::IsNullOrEmpty($TestType)) {
                Write-Error "Test type required. Use: smoke, api, database, websocket, integration, performance, or all"
                exit 1
            }
            Write-Banner
            Test-Dependencies
            Initialize-Environment
            Start-Infrastructure
            if (Test-Health) {
                Invoke-Tests $TestType
            }
        }
        "full" {
            Write-Banner
            Test-Dependencies
            Initialize-Environment
            Start-Infrastructure
            
            if (Test-Health) {
                # Run all test types
                $overallResult = $true
                $testTypes = @("smoke", "api", "database", "websocket", "integration")
                
                foreach ($testType in $testTypes) {
                    if (!(Invoke-Tests $testType)) {
                        $overallResult = $false
                    }
                    Write-Host ""
                }
                
                New-TestReport
                
                if ($overallResult) {
                    Write-Success "All tests completed successfully!"
                } else {
                    Write-Error "Some tests failed. Check results for details."
                    exit 1
                }
            }
        }
        "stop" {
            Write-Step "Stopping test infrastructure..."
            docker-compose -f $ComposeFile -p $ProjectName stop
            Write-Success "Test infrastructure stopped"
        }
        "cleanup" {
            Remove-Infrastructure
        }
        "logs" {
            Show-Logs $Service
        }
        "health" {
            Test-Health
        }
        "report" {
            New-TestReport
        }
        "help" {
            Show-Help
        }
        "" {
            Write-Error "Command required"
            Show-Help
            exit 1
        }
        default {
            Write-Error "Unknown command: $Command"
            Show-Help
            exit 1
        }
    }
}

# Execute main function
Main
