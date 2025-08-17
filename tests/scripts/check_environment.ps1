#!/usr/bin/env pwsh
<#
.SYNOPSIS
🔍 ENVIRONMENT CHECK BEFORE TESTING
.DESCRIPTION
Kiểm tra môi trường, dependencies và configuration trước khi chạy tests
#>

param(
    [switch]$Fix = $false,
    [switch]$Verbose = $true
)

function Write-CheckHeader {
    param([string]$Title, [string]$Color = "Cyan")
    
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor $Color
    Write-Host "🔍 $Title" -ForegroundColor $Color
    Write-Host "=" * 60 -ForegroundColor $Color
}

function Test-CondaEnvironment {
    Write-CheckHeader "CONDA ENVIRONMENT CHECK"
    
    try {
        # Check if conda is available
        $condaVersion = & conda --version 2>$null
        Write-Host "✅ Conda: $condaVersion" -ForegroundColor Green
        
        # Check crypto_agent environment
        $envList = & conda env list 2>$null | Where-Object { $_ -match "crypto_agent" }
        if ($envList) {
            Write-Host "✅ Environment 'crypto_agent': EXISTS" -ForegroundColor Green
        } else {
            Write-Host "❌ Environment 'crypto_agent': NOT FOUND" -ForegroundColor Red
            return $false
        }
        
        # Check Python version in environment
        $pythonVersion = & conda run --name crypto_agent python --version 2>$null
        Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
        
        return $true
        
    } catch {
        Write-Host "❌ Conda environment check failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Test-PythonPackages {
    Write-CheckHeader "PYTHON PACKAGES CHECK"
    
    $requiredPackages = @{
        "fastapi" = "Web framework"
        "uvicorn" = "ASGI server"
        "celery" = "Task queue"
        "aiohttp" = "Async HTTP client"
        "psutil" = "System monitoring"
        "asyncio" = "Async support"
    }
    
    $allGood = $true
    
    foreach ($package in $requiredPackages.Keys) {
        try {
            $null = & conda run --name crypto_agent python -c "import $package; print('OK')" 2>$null
            Write-Host "✅ $package - $($requiredPackages[$package])" -ForegroundColor Green
        } catch {
            Write-Host "❌ $package - MISSING ($($requiredPackages[$package]))" -ForegroundColor Red
            $allGood = $false
        }
    }
    
    return $allGood
}

function Test-ProjectStructure {
    Write-CheckHeader "PROJECT STRUCTURE CHECK"
    
    $requiredPaths = @{
        "src/app/main.py" = "FastAPI main application"
        "src/app/celery_config.py" = "Celery configuration"
        "src/app/utils/logging_config.py" = "Logging configuration"
        "tests/scripts" = "Test scripts directory"
        "tests/results" = "Test results directory"
        "requirements.txt" = "Python dependencies"
        ".env" = "Environment variables"
    }
    
    $allGood = $true
    
    foreach ($path in $requiredPaths.Keys) {
        if (Test-Path $path) {
            Write-Host "✅ $path - $($requiredPaths[$path])" -ForegroundColor Green
        } else {
            Write-Host "❌ $path - MISSING ($($requiredPaths[$path]))" -ForegroundColor Red
            $allGood = $false
        }
    }
    
    # Check if we're in the right directory
    if (!(Test-Path "src/app/main.py")) {
        Write-Host "⚠️ Make sure you're in the Legal-Retrieval root directory" -ForegroundColor Yellow
        Write-Host "   Current directory: $(Get-Location)" -ForegroundColor Gray
    }
    
    return $allGood
}

function Test-PortAvailability {
    Write-CheckHeader "PORT AVAILABILITY CHECK"
    
    $portsToCheck = @(8000, 8001, 5672, 6379)  # API, API alt, RabbitMQ, Redis
    
    $allGood = $true
    
    foreach ($port in $portsToCheck) {
        try {
            $connection = New-Object System.Net.Sockets.TcpClient
            $connection.ConnectAsync("localhost", $port).Wait(1000)
            
            if ($connection.Connected) {
                Write-Host "⚠️ Port ${port}: IN USE" -ForegroundColor Yellow
                $connection.Close()
            } else {
                Write-Host "✅ Port ${port}: AVAILABLE" -ForegroundColor Green
            }
        } catch {
            Write-Host "✅ Port ${port}: AVAILABLE" -ForegroundColor Green
        }
    }
    
    return $allGood
}

function Test-LoggingConfiguration {
    Write-CheckHeader "LOGGING CONFIGURATION CHECK"
    
    try {
        # Test logging imports
        $testScript = @"
import sys
sys.path.insert(0, 'src')
from app.utils.logging_config import get_application_logger, get_performance_logger
logger = get_application_logger('test')
print('Logging configuration OK')
"@
        
        $testFile = "temp_logging_test.py"
        $testScript | Out-File -FilePath $testFile -Encoding UTF8
        
        $result = & conda run --name crypto_agent python $testFile 2>$null
        Remove-Item $testFile -ErrorAction SilentlyContinue
        
        if ($result -contains "Logging configuration OK") {
            Write-Host "✅ Logging configuration: OK" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Logging configuration: FAILED" -ForegroundColor Red
            return $false
        }
        
    } catch {
        Write-Host "❌ Logging configuration test failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Test-CeleryConfiguration {
    Write-CheckHeader "CELERY CONFIGURATION CHECK"
    
    try {
        # Test Celery imports
        $testScript = @"
import sys
sys.path.insert(0, 'src')
from app.celery_config import celery_app
print('Celery configuration OK')
"@
        
        $testFile = "temp_celery_test.py"
        $testScript | Out-File -FilePath $testFile -Encoding UTF8
        
        $result = & conda run --name crypto_agent python $testFile 2>$null
        Remove-Item $testFile -ErrorAction SilentlyContinue
        
        if ($result -contains "Celery configuration OK") {
            Write-Host "✅ Celery configuration: OK" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Celery configuration: FAILED" -ForegroundColor Red
            return $false
        }
        
    } catch {
        Write-Host "❌ Celery configuration test failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Show-FixSuggestions {
    param([hashtable]$Issues)
    
    Write-CheckHeader "FIX SUGGESTIONS" "Yellow"
    
    if ($Issues.ContainsKey("conda")) {
        Write-Host "🔧 CONDA ENVIRONMENT ISSUES:" -ForegroundColor Yellow
        Write-Host "   1. Install Miniconda/Anaconda if not installed" -ForegroundColor White
        Write-Host "   2. Create crypto_agent environment:" -ForegroundColor White
        Write-Host "      conda create -n crypto_agent python=3.9" -ForegroundColor Gray
        Write-Host "   3. Activate environment:" -ForegroundColor White
        Write-Host "      conda activate crypto_agent" -ForegroundColor Gray
    }
    
    if ($Issues.ContainsKey("packages")) {
        Write-Host "🔧 PYTHON PACKAGES ISSUES:" -ForegroundColor Yellow
        Write-Host "   1. Install required packages:" -ForegroundColor White
        Write-Host "      conda run --name crypto_agent pip install -r requirements.txt" -ForegroundColor Gray
        Write-Host "   2. Or install packages individually:" -ForegroundColor White
        Write-Host "      conda run --name crypto_agent pip install fastapi uvicorn celery aiohttp psutil" -ForegroundColor Gray
    }
    
    if ($Issues.ContainsKey("structure")) {
        Write-Host "🔧 PROJECT STRUCTURE ISSUES:" -ForegroundColor Yellow
        Write-Host "   1. Make sure you're in the Legal-Retrieval root directory" -ForegroundColor White
        Write-Host "   2. Check if files were moved during cleanup" -ForegroundColor White
        Write-Host "   3. Restore missing files from backup or git" -ForegroundColor White
    }
    
    if ($Issues.ContainsKey("config")) {
        Write-Host "🔧 CONFIGURATION ISSUES:" -ForegroundColor Yellow
        Write-Host "   1. Check import paths in Python files" -ForegroundColor White
        Write-Host "   2. Verify PYTHONPATH includes src directory" -ForegroundColor White
        Write-Host "   3. Check for syntax errors in configuration files" -ForegroundColor White
    }
}

function Auto-FixIssues {
    Write-CheckHeader "ATTEMPTING AUTO-FIX" "Blue"
    
    # Create missing directories
    $dirsToCreate = @("tests/results", "logs")
    foreach ($dir in $dirsToCreate) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "✅ Created directory: $dir" -ForegroundColor Green
        }
    }
    
    # Install missing packages
    try {
        Write-Host "🔄 Installing/updating packages..." -ForegroundColor Yellow
        $installResult = & conda run --name crypto_agent pip install -r requirements.txt 2>&1
        Write-Host "✅ Package installation completed" -ForegroundColor Green
    } catch {
        Write-Host "❌ Package installation failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Set environment variables
    if (!(Test-Path ".env")) {
        $envContent = @"
LOG_LEVEL=INFO
LOG_FORMAT=json
ENABLE_STRUCTURED_LOGS=true
ENABLE_PERFORMANCE_LOGGING=true
"@
        $envContent | Out-File -FilePath ".env" -Encoding UTF8
        Write-Host "✅ Created basic .env file" -ForegroundColor Green
    }
}

# ================================
# MAIN EXECUTION
# ================================

Write-CheckHeader "🔍 ENVIRONMENT VERIFICATION FOR COMPREHENSIVE TESTING" "Blue"

$issues = @{}
$allChecksPass = $true

# Run all checks
if (!(Test-CondaEnvironment)) {
    $issues["conda"] = $true
    $allChecksPass = $false
}

if (!(Test-PythonPackages)) {
    $issues["packages"] = $true
    $allChecksPass = $false
}

if (!(Test-ProjectStructure)) {
    $issues["structure"] = $true
    $allChecksPass = $false
}

Test-PortAvailability | Out-Null

if (!(Test-LoggingConfiguration)) {
    $issues["config"] = $true
    $allChecksPass = $false
}

if (!(Test-CeleryConfiguration)) {
    $issues["config"] = $true
    $allChecksPass = $false
}

# Show results
Write-CheckHeader "VERIFICATION RESULTS" "Green"

if ($allChecksPass) {
    Write-Host "🎉 ALL CHECKS PASSED!" -ForegroundColor Green
    Write-Host "✅ Environment is ready for comprehensive testing" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 You can now run:" -ForegroundColor Cyan
    Write-Host "   .\tests\scripts\run_comprehensive_tests.ps1" -ForegroundColor White
} else {
    Write-Host "⚠️ SOME CHECKS FAILED" -ForegroundColor Yellow
    Write-Host "❌ Environment needs attention before testing" -ForegroundColor Red
    
    if ($Fix) {
        Auto-FixIssues
        Write-Host ""
        Write-Host "🔄 Re-run this script to verify fixes" -ForegroundColor Cyan
    } else {
        Show-FixSuggestions -Issues $issues
        Write-Host ""
        Write-Host "💡 Run with -Fix flag to attempt automatic fixes:" -ForegroundColor Cyan
        Write-Host "   .\tests\scripts\check_environment.ps1 -Fix" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "🔚 Environment check completed at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
