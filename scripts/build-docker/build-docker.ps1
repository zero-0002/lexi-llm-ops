#!/usr/bin/env pwsh
# Legal Retrieval System - Docker Build Script
# ============================================

param(
    [Parameter(HelpMessage="Service to build: backend, frontend, all")]
    [ValidateSet("backend", "frontend", "all")]
    [string]$Service = "all",
    
    [Parameter(HelpMessage="Docker image tag")]
    [string]$Tag = "latest",
    
    [Parameter(HelpMessage="Docker registry prefix")]
    [string]$Registry = "legal-retrieval",
    
    [Parameter(HelpMessage="Skip image cleanup")]
    [switch]$SkipCleanup,
    
    [Parameter(HelpMessage="Push to registry after build")]
    [switch]$Push,
    
    [Parameter(HelpMessage="Show verbose output")]
    [switch]$ShowVerbose
)

Write-Host "🐳 LEGAL RETRIEVAL SYSTEM - DOCKER BUILD" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Yellow

$ErrorActionPreference = "Stop"

# Check if Docker is available
docker --version | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker is not available!" -ForegroundColor Red
    Write-Host "Please install Docker Desktop and make sure it's running" -ForegroundColor Yellow
    exit 1
}

# Check if docker daemon is running
docker ps | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker daemon is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Docker is available and running" -ForegroundColor Green

# Build configuration
$buildConfig = @{
    backend = @{
        name = "Backend API & Celery Worker"
        context = "./src/app"
        dockerfile = "Dockerfile"
        image = "$Registry/backend"
        platforms = "linux/amd64,linux/arm64"
    }
    frontend = @{
        name = "Frontend Web Application"
        context = "./src/legal-chatbot-fe"
        dockerfile = "Dockerfile"
        image = "$Registry/frontend"
        platforms = "linux/amd64,linux/arm64"
    }
}

function Build-Service {
    param(
        [string]$ServiceName,
        [hashtable]$Config
    )
    
    Write-Host "`n🔨 Building: $($Config.name)" -ForegroundColor Cyan
    Write-Host "===============================================" -ForegroundColor White
    
    $imageFullName = "$($Config.image):$Tag"
    
    Write-Host "  📦 Image: $imageFullName" -ForegroundColor White
    Write-Host "  📂 Context: $($Config.context)" -ForegroundColor White
    Write-Host "  📄 Dockerfile: $($Config.dockerfile)" -ForegroundColor White
    
    # Check if context directory exists
    if (-not (Test-Path $Config.context)) {
        Write-Host "  ❌ Context directory not found: $($Config.context)" -ForegroundColor Red
        return $false
    }
    
    # Check if Dockerfile exists
    $dockerfilePath = Join-Path $Config.context $Config.dockerfile
    if (-not (Test-Path $dockerfilePath)) {
        Write-Host "  ❌ Dockerfile not found: $dockerfilePath" -ForegroundColor Red
        return $false
    }
    
    Write-Host "  🚀 Starting build..." -ForegroundColor White
    
    # Build command
    $buildArgs = @(
        "build",
        "--tag", $imageFullName,
        "--file", (Join-Path $Config.context $Config.dockerfile),
        $Config.context
    )
    
    if ($ShowVerbose) {
        $buildArgs += "--progress=plain"
    }
    
    # Add build arguments for different services
    switch ($ServiceName) {
        "backend" {
            $buildArgs += @(
                "--build-arg", "BUILDKIT_INLINE_CACHE=1",
                "--build-arg", "PYTHON_VERSION=3.11"
            )
        }
        "frontend" {
            $buildArgs += @(
                "--build-arg", "NODE_VERSION=18",
                "--build-arg", "NGINX_VERSION=1.25"
            )
        }
    }
    
    try {
        if ($ShowVerbose) {
            Write-Host "  🔍 Build command: docker $($buildArgs -join ' ')" -ForegroundColor Gray
        }
        
        $buildOutput = docker @buildArgs
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ Build successful!" -ForegroundColor Green
            
            # Show image info
            $imageInfo = docker images $imageFullName --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
            Write-Host "  📊 Image Info:" -ForegroundColor Blue
            Write-Host "     $imageInfo" -ForegroundColor Gray
            
            return $true
        } else {
            Write-Host "  ❌ Build failed!" -ForegroundColor Red
            if ($ShowVerbose -and $buildOutput) {
                Write-Host "     Build output:" -ForegroundColor Gray
                $buildOutput | ForEach-Object { Write-Host "     $_" -ForegroundColor Gray }
            }
            return $false
        }
    } catch {
        Write-Host "  ❌ Build error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Push-Service {
    param(
        [string]$ServiceName,
        [hashtable]$Config
    )
    
    if (-not $Push) {
        return $true
    }
    
    $imageFullName = "$($Config.image):$Tag"
    
    Write-Host "`n📤 Pushing: $($Config.name)" -ForegroundColor Cyan
    Write-Host "  📦 Image: $imageFullName" -ForegroundColor White
    
    try {
        docker push $imageFullName
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ Push successful!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "  ❌ Push failed!" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "  ❌ Push error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Clean-Images {
    if ($SkipCleanup) {
        return
    }
    
    Write-Host "`n🧹 Cleaning up dangling images..." -ForegroundColor Cyan
    
    try {
        $danglingImages = docker images -f "dangling=true" -q
        if ($danglingImages) {
            docker rmi $danglingImages
            Write-Host "  ✅ Cleanup completed" -ForegroundColor Green
        } else {
            Write-Host "  ℹ️ No dangling images to clean" -ForegroundColor Blue
        }
    } catch {
        Write-Host "  ⚠️ Cleanup warning: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Main build process
$startTime = Get-Date
$buildResults = @{}

if ($Service -eq "all") {
    $servicesToBuild = $buildConfig.Keys
} else {
    $servicesToBuild = @($Service)
}

Write-Host "`n🎯 Building services: $($servicesToBuild -join ', ')" -ForegroundColor Cyan
Write-Host "🏷️ Tag: $Tag" -ForegroundColor White
Write-Host "🏪 Registry: $Registry" -ForegroundColor White

foreach ($serviceName in $servicesToBuild) {
    if (-not $buildConfig.ContainsKey($serviceName)) {
        Write-Host "`n❌ Unknown service: $serviceName" -ForegroundColor Red
        continue
    }
    
    $config = $buildConfig[$serviceName]
    $buildSuccess = Build-Service -ServiceName $serviceName -Config $config
    $buildResults[$serviceName] = $buildSuccess
    
    if ($buildSuccess) {
        $pushSuccess = Push-Service -ServiceName $serviceName -Config $config
        if (-not $pushSuccess -and $Push) {
            $buildResults[$serviceName] = $false
        }
    }
}

# Cleanup
Clean-Images

# Summary
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host "`n🎉 BUILD SUMMARY" -ForegroundColor Green
Write-Host "================" -ForegroundColor Yellow

Write-Host "  ⏱️ Total Duration: $($duration.Minutes)m $($duration.Seconds)s" -ForegroundColor White
Write-Host "  🏷️ Tag: $Tag" -ForegroundColor White

foreach ($serviceName in $servicesToBuild) {
    $success = $buildResults[$serviceName]
    $status = if ($success) { "✅ SUCCESS" } else { "❌ FAILED" }
    $color = if ($success) { "Green" } else { "Red" }
    
    Write-Host "  $status $serviceName" -ForegroundColor $color
}

# Final status
$successCount = ($buildResults.Values | Where-Object { $_ }).Count
$totalCount = $buildResults.Count

if ($successCount -eq $totalCount) {
    Write-Host "`n🎊 All builds completed successfully!" -ForegroundColor Green
    
    Write-Host "`n🚀 Next Steps:" -ForegroundColor Cyan
    Write-Host "  1. Test images: docker-compose up" -ForegroundColor White
    Write-Host "  2. Load to Kind: kind load docker-image $Registry/backend:$Tag" -ForegroundColor White
    Write-Host "  3. Deploy to K8s: ./helm/deploy-kind.ps1" -ForegroundColor White
    
} elseif ($successCount -gt 0) {
    Write-Host "`n⚠️ Partial success: $successCount/$totalCount builds completed" -ForegroundColor Yellow
    Write-Host "Check the errors above and retry failed builds" -ForegroundColor White
} else {
    Write-Host "`n❌ All builds failed!" -ForegroundColor Red
    Write-Host "Check Docker setup and Dockerfiles" -ForegroundColor White
    exit 1
}

Write-Host "`n🔍 Available Commands:" -ForegroundColor Cyan
Write-Host "  📋 List images: docker images | grep $Registry" -ForegroundColor White
Write-Host "  🧪 Test backend: docker run --rm -p 8000:8000 $Registry/backend:$Tag" -ForegroundColor White
Write-Host "  🌐 Test frontend: docker run --rm -p 3000:80 $Registry/frontend:$Tag" -ForegroundColor White
Write-Host "  🗑️ Remove images: docker rmi $Registry/backend:$Tag $Registry/frontend:$Tag" -ForegroundColor White
