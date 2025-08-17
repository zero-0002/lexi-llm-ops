#!/usr/bin/env pwsh
<#
.SYNOPSIS
🚀 START SERVICES AND RUN COMPREHENSIVE TESTS
.DESCRIPTION
Khởi động API server và Celery workers, sau đó chạy comprehensive tests
.PARAMETER Port
Port cho API server (default: 8001)
.PARAMETER SkipServerStart
Bỏ qua việc khởi động server (giả sử đã chạy)
.PARAMETER TestOnly
Chỉ chạy tests, không khởi động services
#>

param(
    [int]$Port = 8001,
    [switch]$SkipServerStart = $false,
    [switch]$TestOnly = $false,
    [switch]$Verbose = $true
)

$BaseUrl = "http://localhost:$Port"
$OutputPath = "tests/results"

function Write-StatusHeader {
    param([string]$Title, [string]$Color = "Cyan")
    
    Write-Host ""
    Write-Host "=" * 80 -ForegroundColor $Color
    Write-Host "🚀 $Title" -ForegroundColor $Color
    Write-Host "=" * 80 -ForegroundColor $Color
    Write-Host "🕐 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
}

function Test-ServerHealth {
    param([string]$Url, [int]$MaxRetries = 10)
    
    Write-Host "🔍 Checking server health at $Url..." -ForegroundColor Yellow
    
    for ($i = 1; $i -le $MaxRetries; $i++) {
        try {
            $response = Invoke-RestMethod -Uri "$Url/health" -Method GET -TimeoutSec 5
            Write-Host "✅ Server is healthy!" -ForegroundColor Green
            return $true
        } catch {
            Write-Host "  ⏳ Attempt $i/$MaxRetries - Server not ready..." -ForegroundColor Yellow
            Start-Sleep -Seconds 3
        }
    }
    
    Write-Host "❌ Server health check failed after $MaxRetries attempts" -ForegroundColor Red
    return $false
}

function Start-APIServer {
    param([int]$Port)
    
    Write-StatusHeader "STARTING API SERVER" "Blue"
    
    # Check if server is already running
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/health" -Method GET -TimeoutSec 2
        Write-Host "✅ API Server already running at $BaseUrl" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "📡 Starting new API server on port $Port..." -ForegroundColor Yellow
    }
    
    # Start server in background
    try {
        $serverJob = Start-Job -ScriptBlock {
            param($Port)
            Set-Location "D:\Data\Legal-Retrieval"
            & conda run --name crypto_agent python -m uvicorn src.app.main:app --host 0.0.0.0 --port $Port --reload
        } -ArgumentList $Port
        
        Write-Host "🔄 Server job started (ID: $($serverJob.Id))" -ForegroundColor Cyan
        
        # Wait for server to be ready
        Start-Sleep -Seconds 5
        
        if (Test-ServerHealth -Url $BaseUrl -MaxRetries 15) {
            Write-Host "✅ API Server started successfully!" -ForegroundColor Green
            return $serverJob
        } else {
            Write-Host "❌ Failed to start API server" -ForegroundColor Red
            Stop-Job $serverJob -PassThru | Remove-Job
            return $null
        }
        
    } catch {
        Write-Host "❌ Error starting server: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

function Start-CeleryWorkers {
    Write-StatusHeader "STARTING CELERY WORKERS" "Blue"
    
    # Check if Celery workers are already running
    $celeryProcesses = Get-Process | Where-Object { $_.ProcessName -like "*celery*" -or $_.CommandLine -like "*celery*" } -ErrorAction SilentlyContinue
    
    if ($celeryProcesses -and $celeryProcesses.Count -gt 0) {
        Write-Host "✅ Celery workers already running ($($celeryProcesses.Count) processes)" -ForegroundColor Green
        return $true
    }
    
    Write-Host "🔄 Starting Celery workers..." -ForegroundColor Yellow
    
    try {
        # Start Celery worker
        $celeryJob = Start-Job -ScriptBlock {
            Set-Location "D:\Data\Legal-Retrieval"
            & conda run --name crypto_agent celery -A src.app.celery_config worker --loglevel=info --pool=solo
        }
        
        Write-Host "🔄 Celery worker job started (ID: $($celeryJob.Id))" -ForegroundColor Cyan
        
        # Wait a bit for workers to initialize
        Start-Sleep -Seconds 10
        
        # Check if workers are running
        $celeryProcesses = Get-Process | Where-Object { $_.ProcessName -like "*celery*" -or $_.CommandLine -like "*celery*" } -ErrorAction SilentlyContinue
        
        if ($celeryProcesses -and $celeryProcesses.Count -gt 0) {
            Write-Host "✅ Celery workers started successfully!" -ForegroundColor Green
            return $celeryJob
        } else {
            Write-Host "⚠️ Celery workers may not be running properly" -ForegroundColor Yellow
            return $celeryJob
        }
        
    } catch {
        Write-Host "❌ Error starting Celery workers: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

function Run-ComprehensiveTests {
    Write-StatusHeader "RUNNING COMPREHENSIVE TESTS" "Green"
    
    # Ensure output directory exists
    if (!(Test-Path $OutputPath)) {
        New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
    }
    
    Write-Host "📋 Test Configuration:" -ForegroundColor Cyan
    Write-Host "  🌐 Base URL: $BaseUrl" -ForegroundColor White
    Write-Host "  📁 Output Path: $OutputPath" -ForegroundColor White
    Write-Host "  🧪 Test Suite: Comprehensive API + Celery + Logging" -ForegroundColor White
    
    # Run PowerShell comprehensive test
    Write-Host "`n🔍 Running PowerShell Comprehensive Test..." -ForegroundColor Yellow
    
    try {
        $psTestResult = & "$PSScriptRoot/comprehensive_api_celery_test.ps1" -BaseUrl $BaseUrl -OutputPath $OutputPath -WithPerformance -ConcurrentUsers 5 -Verbose
        Write-Host "✅ PowerShell test completed" -ForegroundColor Green
    } catch {
        Write-Host "❌ PowerShell test failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Run Python advanced test
    Write-Host "`n🔍 Running Python Advanced Test..." -ForegroundColor Yellow
    
    try {
        $pyTestResult = & conda run --name crypto_agent python "$PSScriptRoot/advanced_comprehensive_test.py" --url $BaseUrl --output $OutputPath --concurrent 5 --verbose
        Write-Host "✅ Python test completed" -ForegroundColor Green
    } catch {
        Write-Host "❌ Python test failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Show results summary
    Write-Host "`n📊 Test Results Summary:" -ForegroundColor Cyan
    $resultFiles = Get-ChildItem -Path $OutputPath -Filter "*$(Get-Date -Format 'yyyyMMdd')*" | Sort-Object CreationTime -Descending
    
    foreach ($file in $resultFiles | Select-Object -First 10) {
        Write-Host "  📄 $($file.Name) ($('{0:N0}' -f $file.Length) bytes)" -ForegroundColor White
    }
    
    Write-Host "`n🎉 COMPREHENSIVE TESTING COMPLETED!" -ForegroundColor Green
}

function Show-SystemStatus {
    Write-StatusHeader "SYSTEM STATUS CHECK" "Cyan"
    
    # Check API Server
    try {
        $healthResponse = Invoke-RestMethod -Uri "$BaseUrl/health" -Method GET -TimeoutSec 5
        Write-Host "✅ API Server: RUNNING" -ForegroundColor Green
    } catch {
        Write-Host "❌ API Server: NOT RUNNING" -ForegroundColor Red
    }
    
    # Check Celery Workers
    $celeryProcesses = Get-Process | Where-Object { $_.ProcessName -like "*celery*" -or $_.CommandLine -like "*celery*" } -ErrorAction SilentlyContinue
    if ($celeryProcesses -and $celeryProcesses.Count -gt 0) {
        Write-Host "✅ Celery Workers: RUNNING ($($celeryProcesses.Count) processes)" -ForegroundColor Green
    } else {
        Write-Host "❌ Celery Workers: NOT RUNNING" -ForegroundColor Red
    }
    
    # Check Python Environment
    try {
        $pythonVersion = & conda run --name crypto_agent python --version
        Write-Host "✅ Python Environment: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Python Environment: NOT AVAILABLE" -ForegroundColor Red
    }
    
    # Check required packages
    $requiredPackages = @("fastapi", "uvicorn", "celery", "aiohttp")
    foreach ($package in $requiredPackages) {
        try {
            $null = & conda run --name crypto_agent python -c "import $package"
            Write-Host "✅ Package ${package}: AVAILABLE" -ForegroundColor Green
        } catch {
            Write-Host "❌ Package ${package}: NOT AVAILABLE" -ForegroundColor Red
        }
    }
}

# ================================
# MAIN EXECUTION
# ================================

Write-StatusHeader "🚀 COMPREHENSIVE TEST RUNNER" "Blue"

# Variables to track started jobs
$serverJob = $null
$celeryJob = $null

try {
    # Show initial system status
    Show-SystemStatus
    
    if (!$TestOnly) {
        # Start services if needed
        if (!$SkipServerStart) {
            $serverJob = Start-APIServer -Port $Port
            if (!$serverJob) {
                Write-Host "❌ Failed to start API server. Exiting." -ForegroundColor Red
                exit 1
            }
        }
        
        # Start Celery workers
        $celeryJob = Start-CeleryWorkers
    }
    
    # Run comprehensive tests
    Run-ComprehensiveTests
    
    Write-StatusHeader "✅ ALL OPERATIONS COMPLETED SUCCESSFULLY" "Green"
    
} catch {
    Write-Host "❌ CRITICAL ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Stack Trace: $($_.ScriptStackTrace)" -ForegroundColor Red
} finally {
    # Cleanup prompt
    if (!$TestOnly -and ($serverJob -or $celeryJob)) {
        Write-Host "`n🤔 Do you want to stop the started services? (y/N): " -ForegroundColor Yellow -NoNewline
        $cleanup = Read-Host
        
        if ($cleanup -eq 'y' -or $cleanup -eq 'Y') {
            Write-Host "🧹 Stopping services..." -ForegroundColor Yellow
            
            if ($serverJob) {
                Stop-Job $serverJob -PassThru | Remove-Job
                Write-Host "✅ API Server stopped" -ForegroundColor Green
            }
            
            if ($celeryJob) {
                Stop-Job $celeryJob -PassThru | Remove-Job
                Write-Host "✅ Celery workers stopped" -ForegroundColor Green
            }
        } else {
            Write-Host "ℹ️ Services left running for manual testing" -ForegroundColor Cyan
            Write-Host "  🌐 API Server: $BaseUrl" -ForegroundColor White
            if ($serverJob) {
                Write-Host "  🔄 Server Job ID: $($serverJob.Id)" -ForegroundColor White
            }
            if ($celeryJob) {
                Write-Host "  🔄 Celery Job ID: $($celeryJob.Id)" -ForegroundColor White
            }
        }
    }
    
    Write-Host "`n🔚 Test runner completed at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
}
