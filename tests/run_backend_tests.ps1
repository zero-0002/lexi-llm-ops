#!/usr/bin/env pwsh
# COMPREHENSIVE BACKEND TEST LAUNCHER

param(
    [string]$BaseUrl = "http://localhost:8000",
    [string]$OutputDir = "tests/results",
    [int]$ConcurrentUsers = 3,
    [switch]$Verbose = $false
)

Write-Host "COMPREHENSIVE BACKEND TEST LAUNCHER" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Yellow

# Ensure we're in the right directory
if (!(Test-Path "src")) {
    Write-Host "Please run from project root directory (where 'src' folder exists)" -ForegroundColor Red
    exit 1
}

Write-Host "Project directory: $(Get-Location)" -ForegroundColor Green

# Check if server is running
Write-Host "Checking server availability..." -ForegroundColor Cyan
try {
    $healthCheck = Invoke-RestMethod -Uri "$BaseUrl/health" -TimeoutSec 5
    Write-Host "Server is running and accessible" -ForegroundColor Green
} catch {
    Write-Host "Server is not accessible at $BaseUrl" -ForegroundColor Red
    Write-Host "Please ensure the backend server is running:" -ForegroundColor Yellow
    Write-Host "  cd src && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Cyan
    exit 1
}

# Create necessary directories
New-Item -ItemType Directory -Path "tests" -Force | Out-Null
New-Item -ItemType Directory -Path "tests/api" -Force | Out-Null
New-Item -ItemType Directory -Path "tests/logs" -Force | Out-Null
New-Item -ItemType Directory -Path "tests/results" -Force | Out-Null

Write-Host "Test directories ready" -ForegroundColor Green

# Run comprehensive backend test
Write-Host "`nRunning Comprehensive Backend Test Suite..." -ForegroundColor Cyan
Write-Host "   Base URL: $BaseUrl" -ForegroundColor White
Write-Host "   Output Directory: $OutputDir" -ForegroundColor White
Write-Host "   Concurrent Users: $ConcurrentUsers" -ForegroundColor White

$arguments = @(
    "tests/api/comprehensive_backend_test.py",
    "--url", $BaseUrl,
    "--output", $OutputDir,
    "--concurrent", $ConcurrentUsers
)

if ($Verbose) {
    $arguments += "--verbose"
}

try {
    python @arguments
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        Write-Host "`nBACKEND TESTING COMPLETED SUCCESSFULLY!" -ForegroundColor Green
        Write-Host "Check results in: $OutputDir" -ForegroundColor Cyan
    } else {
        Write-Host "`nBackend testing completed with issues (exit code: $exitCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "`nFailed to run backend tests: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Show results summary
if (Test-Path "$OutputDir/test_summary_*.json") {
    Write-Host "`nQUICK SUMMARY:" -ForegroundColor Yellow
    $latestSummary = Get-ChildItem "$OutputDir/test_summary_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    $summary = Get-Content $latestSummary.FullName | ConvertFrom-Json
    
    Write-Host "   Success Rate: $($summary.api_testing.success_rate)%" -ForegroundColor $(if($summary.api_testing.success_rate -ge 90){"Green"}else{"Yellow"})
    Write-Host "   Total Tests: $($summary.api_testing.total_tests)" -ForegroundColor White
    Write-Host "   Avg Response: $($summary.api_testing.average_response_time_ms)ms" -ForegroundColor White
    Write-Host "   Duration: $($summary.execution_time.duration_minutes) minutes" -ForegroundColor White
}

Write-Host "`nResults Location: $OutputDir" -ForegroundColor Cyan
Write-Host "View detailed results in the CSV files generated" -ForegroundColor Cyan
