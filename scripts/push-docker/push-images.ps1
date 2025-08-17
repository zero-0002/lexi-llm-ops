#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Push Docker images to registry for Legal Retrieval System
.DESCRIPTION
    Pushes built Docker images to container registry with proper tagging
.PARAMETER Registry
    Container registry URL (default: docker.io)
.PARAMETER Tag
    Image tag to push (default: latest)
.PARAMETER Target
    Specific service to push (backend, frontend, celery-worker, or all)
.EXAMPLE
    .\push-images.ps1 -Target backend
    .\push-images.ps1 -Registry "your-registry.com" -Tag "v1.0.0"
#>

param(
    [string]$Registry = "docker.io",
    [string]$Tag = "latest", 
    [ValidateSet("backend", "frontend", "celery-worker", "all")]
    [string]$Target = "all"
)

# Color output functions
function Write-ColorOutput($ForegroundColor) {
    if ($args) {
        Write-Host $args -ForegroundColor $ForegroundColor
    }
}

function Write-Success($message) { Write-ColorOutput Green "✅ $message" }
function Write-Error($message) { Write-ColorOutput Red "❌ $message" }
function Write-Info($message) { Write-ColorOutput Cyan "ℹ️ $message" }
function Write-Warning($message) { Write-ColorOutput Yellow "⚠️ $message" }

# Configuration
$PROJECT_NAME = "legalretrieval"
$IMAGES = @{
    "backend" = @{
        "name" = "$PROJECT_NAME/backend"
        "path" = "src/app"
    }
    "frontend" = @{
        "name" = "$PROJECT_NAME/frontend" 
        "path" = "src/frontend"
    }
    "celery-worker" = @{
        "name" = "$PROJECT_NAME/celery-worker"
        "path" = "src/app"
    }
}

function Test-DockerConnection {
    Write-Info "Checking Docker connection..."
    try {
        $null = docker version --format json | ConvertFrom-Json
        Write-Success "Docker is running"
        return $true
    }
    catch {
        Write-Error "Docker is not running or not accessible"
        return $false
    }
}

function Test-ImageExists {
    param([string]$ImageName)
    
    $exists = docker images --format "table {{.Repository}}:{{.Tag}}" | Select-String "$ImageName:$Tag"
    return $null -ne $exists
}

function Push-DockerImage {
    param(
        [string]$ImageName,
        [string]$RegistryUrl = $Registry
    )
    
    $localImage = "$ImageName:$Tag"
    $remoteImage = "$RegistryUrl/$ImageName:$Tag"
    
    Write-Info "Pushing $localImage to $remoteImage..."
    
    # Tag for registry
    if ($RegistryUrl -ne "docker.io") {
        Write-Info "Tagging image for registry: $remoteImage"
        docker tag $localImage $remoteImage
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to tag image $localImage"
            return $false
        }
        $pushImage = $remoteImage
    } else {
        $pushImage = $localImage
    }
    
    # Push image
    docker push $pushImage
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to push image $pushImage"
        return $false
    }
    
    Write-Success "Successfully pushed $pushImage"
    return $true
}

function Push-AllImages {
    $success = $true
    $pushedImages = @()
    
    foreach ($service in $IMAGES.Keys) {
        if ($Target -eq "all" -or $Target -eq $service) {
            $imageName = $IMAGES[$service].name
            
            # Check if image exists locally
            if (-not (Test-ImageExists $imageName)) {
                Write-Warning "Image $imageName:$Tag not found locally. Skipping..."
                continue
            }
            
            if (Push-DockerImage $imageName) {
                $pushedImages += $imageName
            } else {
                $success = $false
                Write-Error "Failed to push $imageName"
            }
        }
    }
    
    return @{
        "success" = $success
        "pushed" = $pushedImages
    }
}

function Show-Summary {
    param($result)
    
    Write-Host "`n" -NoNewline
    Write-Info "=== PUSH SUMMARY ==="
    
    if ($result.pushed.Count -gt 0) {
        Write-Success "Successfully pushed images:"
        foreach ($image in $result.pushed) {
            Write-Host "  📦 $image:$Tag" -ForegroundColor Green
        }
    }
    
    if ($result.success) {
        Write-Success "All requested images pushed successfully!"
    } else {
        Write-Error "Some images failed to push"
        exit 1
    }
}

# Main execution
function Main {
    Write-Host "🚀 Legal Retrieval System - Docker Push Script" -ForegroundColor Magenta
    Write-Host "================================================================" -ForegroundColor Magenta
    
    # Check Docker
    if (-not (Test-DockerConnection)) {
        exit 1
    }
    
    # Show configuration
    Write-Info "Configuration:"
    Write-Host "  📝 Registry: $Registry" -ForegroundColor Cyan
    Write-Host "  🏷️  Tag: $Tag" -ForegroundColor Cyan
    Write-Host "  🎯 Target: $Target" -ForegroundColor Cyan
    Write-Host ""
    
    # Push images
    $result = Push-AllImages
    
    # Show summary
    Show-Summary $result
}

# Run main function
Main
