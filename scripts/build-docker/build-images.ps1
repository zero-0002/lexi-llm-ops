# Legal Retrieval System - Docker Build Script (PowerShell)
# ==========================================================

param(
    [string]$Target = "all",
    [string]$Registry = "docker.io",
    [string]$Namespace = "legalretrieval", 
    [string]$Tag = "latest"
)

# Colors for output
$Green = "Green"
$Red = "Red" 
$Yellow = "Yellow"
$Cyan = "Cyan"
$Blue = "Blue"

# Functions
function Write-Log {
    param([string]$Message, [string]$Color = "White")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-Log "✅ $Message" $Green
}

function Write-Error {
    param([string]$Message)
    Write-Log "❌ $Message" $Red
}

function Write-Step {
    param([string]$Message)
    Write-Log "🚀 $Message" $Cyan
}

function Write-Warning {
    param([string]$Message)
    Write-Log "⚠️ $Message" $Yellow
}

# Check Docker environment
function Test-Docker {
    Write-Step "Checking Docker environment..."
    
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "Docker is not installed or not in PATH"
        exit 1
    }
    
    try {
        docker ps | Out-Null
        Write-Success "Docker environment is ready"
    }
    catch {
        Write-Error "Docker daemon is not running"
        exit 1
    }
}

# Build backend image
function Build-Backend {
    Write-Step "Building backend Docker image..."
    
    $imageName = "$Registry/$Namespace/backend:$Tag"
    
    Write-Log "Building image: $imageName" $Blue
    Write-Log "Build context: $(Get-Location)\src\app" $Blue
    
    # Check if Dockerfile exists
    if (-not (Test-Path "src\app\Dockerfile")) {
        Write-Error "Backend Dockerfile not found: src\app\Dockerfile"
        return $false
    }
    
    # Build the image
    try {
        $buildArgs = @(
            "--tag", $imageName,
            "--file", "src\app\Dockerfile",
            "--build-arg", "BUILD_DATE=$(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ')",
            "--build-arg", "VERSION=$Tag",
            "src\app"
        )
        
        & docker build @buildArgs
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Backend image built successfully"
            
            # Show image info
            $imageSize = docker images $imageName --format "{{.Size}}"
            Write-Log "Image size: $imageSize" $Blue
            
            return $true
        }
        else {
            Write-Error "Failed to build backend image"
            return $false
        }
    }
    catch {
        Write-Error "Error building backend image: $($_.Exception.Message)"
        return $false
    }
}

# Build frontend image
function Build-Frontend {
    Write-Step "Building frontend Docker image..."
    
    $imageName = "$Registry/$Namespace/frontend:$Tag"
    
    Write-Log "Building image: $imageName" $Blue
    Write-Log "Build context: $(Get-Location)\src\legal-chatbot-fe" $Blue
    
    # Check if Dockerfile exists
    if (-not (Test-Path "src\legal-chatbot-fe\Dockerfile")) {
        Write-Error "Frontend Dockerfile not found: src\legal-chatbot-fe\Dockerfile"
        return $false
    }
    
    # Build the image
    try {
        $buildArgs = @(
            "--tag", $imageName,
            "--file", "src\legal-chatbot-fe\Dockerfile",
            "--build-arg", "BUILD_DATE=$(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ')",
            "--build-arg", "VERSION=$Tag",
            "src\legal-chatbot-fe"
        )
        
        & docker build @buildArgs
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Frontend image built successfully"
            
            # Show image info
            $imageSize = docker images $imageName --format "{{.Size}}"
            Write-Log "Image size: $imageSize" $Blue
            
            return $true
        }
        else {
            Write-Error "Failed to build frontend image"
            return $false
        }
    }
    catch {
        Write-Error "Error building frontend image: $($_.Exception.Message)"
        return $false
    }
}

# Test images
function Test-Images {
    Write-Step "Testing built images..."
    
    $backendImage = "$Registry/$Namespace/backend:$Tag"
    $frontendImage = "$Registry/$Namespace/frontend:$Tag"
    
    # Test backend image
    Write-Log "Testing backend image..." $Blue
    try {
        & docker run --rm --entrypoint="" $backendImage python --version
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Backend image test passed"
        }
        else {
            Write-Error "Backend image test failed"
            return $false
        }
    }
    catch {
        Write-Error "Backend image test failed: $($_.Exception.Message)"
        return $false
    }
    
    # Test frontend image  
    Write-Log "Testing frontend image..." $Blue
    try {
        & docker run --rm --entrypoint="" $frontendImage nginx -v
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Frontend image test passed"
        }
        else {
            Write-Error "Frontend image test failed"
            return $false
        }
    }
    catch {
        Write-Error "Frontend image test failed: $($_.Exception.Message)"
        return $false
    }
    
    return $true
}

# Cleanup dangling images
function Remove-DanglingImages {
    Write-Step "Cleaning up dangling images..."
    
    try {
        $danglingImages = docker images -f "dangling=true" -q
        if ($danglingImages) {
            & docker rmi $danglingImages
            Write-Success "Dangling images cleaned up"
        }
        else {
            Write-Log "No dangling images to clean up" $Blue
        }
    }
    catch {
        Write-Warning "Failed to cleanup dangling images: $($_.Exception.Message)"
    }
}

# Show built images
function Show-Images {
    Write-Step "Built images summary..."
    
    Write-Host "`nBuilt Images:" -ForegroundColor $Cyan
    docker images | Select-String $Namespace | Select-String $Tag
    
    Write-Host "`nUsage Examples:" -ForegroundColor $Cyan
    $backendImage = "$Registry/$Namespace/backend:$Tag"
    $frontendImage = "$Registry/$Namespace/frontend:$Tag"
    
    Write-Host "  Backend:  docker run --rm -p 8000:8000 $backendImage" -ForegroundColor $Blue
    Write-Host "  Frontend: docker run --rm -p 3000:80 $frontendImage" -ForegroundColor $Blue
}

# Main function
function Main {
    Write-Host "`n🐳 Legal Retrieval System - Docker Build" -ForegroundColor $Green
    Write-Host "=========================================" -ForegroundColor $Green
    Write-Host ""
    
    # Load environment if available
    if (Test-Path ".env") {
        Write-Log "Loading environment variables..." $Blue
        Get-Content ".env" | ForEach-Object {
            if ($_ -match "^([^#][^=]+)=(.*)$") {
                [Environment]::SetEnvironmentVariable($matches[1], $matches[2])
            }
        }
        
        # Override with environment variables if they exist
        if ($env:DOCKER_REGISTRY) { $Registry = $env:DOCKER_REGISTRY }
        if ($env:DOCKER_NAMESPACE) { $Namespace = $env:DOCKER_NAMESPACE }
        if ($env:IMAGE_TAG) { $Tag = $env:IMAGE_TAG }
    }
    
    # Show configuration
    Write-Host "Build Configuration:" -ForegroundColor $Cyan
    Write-Host "  Registry: $Registry" -ForegroundColor $Blue
    Write-Host "  Namespace: $Namespace" -ForegroundColor $Blue  
    Write-Host "  Tag: $Tag" -ForegroundColor $Blue
    Write-Host "  Context: $(Get-Location)" -ForegroundColor $Blue
    Write-Host ""
    
    # Execute build steps
    Test-Docker
    
    $buildErrors = 0
    
    # Build backend
    if (-not (Build-Backend)) {
        $buildErrors++
    }
    
    # Build frontend
    if (-not (Build-Frontend)) {
        $buildErrors++
    }
    
    # Test images if builds succeeded
    if ($buildErrors -eq 0) {
        if (-not (Test-Images)) {
            $buildErrors++
        }
    }
    
    # Cleanup
    Remove-DanglingImages
    
    # Show results
    Show-Images
    
    # Summary
    if ($buildErrors -eq 0) {
        Write-Host "`n🎉 All images built successfully!" -ForegroundColor $Green
        Write-Host "Next steps:" -ForegroundColor $Cyan
        Write-Host "  1. Push to registry: .\push-images.ps1" -ForegroundColor $Blue
        Write-Host "  2. Update Helm values: .\update-helm-values.ps1" -ForegroundColor $Blue
        Write-Host "  3. Deploy to Kubernetes: .\deploy-pipeline.ps1" -ForegroundColor $Blue
    }
    else {
        Write-Host "`n❌ Build completed with $buildErrors error(s)" -ForegroundColor $Red
        exit 1
    }
}

# Handle parameters
switch ($Target.ToLower()) {
    "backend" {
        Test-Docker
        Build-Backend
    }
    "frontend" {
        Test-Docker
        Build-Frontend
    }
    "test" {
        Test-Images
    }
    "clean" {
        Remove-DanglingImages
    }
    "all" {
        Main
    }
    default {
        Write-Host "Usage: .\build-images.ps1 [-Target <backend|frontend|test|clean|all>] [-Registry <registry>] [-Namespace <namespace>] [-Tag <tag>]"
        Write-Host ""
        Write-Host "Commands:"
        Write-Host "  backend  - Build backend image only"
        Write-Host "  frontend - Build frontend image only"
        Write-Host "  test     - Test built images"
        Write-Host "  clean    - Clean up dangling images"
        Write-Host "  all      - Build all images (default)"
        exit 1
    }
}
