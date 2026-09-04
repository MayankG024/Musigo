# Push Musigo Docker Images to Docker Hub
# Usage: .\push-to-dockerhub.ps1 <your-dockerhub-username>

param(
    [Parameter(Mandatory=$true)]
    [string]$DockerHubUsername
)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Pushing Musigo to Docker Hub" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if logged in
Write-Host "1. Checking Docker Hub login..." -ForegroundColor Yellow
$loginCheck = docker info 2>&1 | Select-String "Username"
if (-not $loginCheck) {
    Write-Host "   Not logged in. Logging in..." -ForegroundColor Yellow
    docker login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   FAILED: Login unsuccessful" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "   SUCCESS: Already logged in" -ForegroundColor Green
}
Write-Host ""

# Tag images
Write-Host "2. Tagging images for Docker Hub..." -ForegroundColor Yellow

# Backend
Write-Host "   Tagging backend..." -ForegroundColor Gray
docker tag musigo-backend:latest "$DockerHubUsername/musigo-backend:latest"
docker tag musigo-backend:latest "$DockerHubUsername/musigo-backend:v1.0.0"

# Frontend
Write-Host "   Tagging frontend..." -ForegroundColor Gray
docker tag musigo-frontend:latest "$DockerHubUsername/musigo-frontend:latest"
docker tag musigo-frontend:latest "$DockerHubUsername/musigo-frontend:v1.0.0"

# Worker
Write-Host "   Tagging worker..." -ForegroundColor Gray
docker tag musigo-worker:latest "$DockerHubUsername/musigo-worker:latest"
docker tag musigo-worker:latest "$DockerHubUsername/musigo-worker:v1.0.0"

Write-Host "   SUCCESS: Images tagged" -ForegroundColor Green
Write-Host ""

# Push images
Write-Host "3. Pushing images to Docker Hub..." -ForegroundColor Yellow

# Push backend
Write-Host "   Pushing backend (17.4 GB - this will take a while)..." -ForegroundColor Gray
docker push "$DockerHubUsername/musigo-backend:latest"
docker push "$DockerHubUsername/musigo-backend:v1.0.0"

# Push frontend
Write-Host "   Pushing frontend (212 MB)..." -ForegroundColor Gray
docker push "$DockerHubUsername/musigo-frontend:latest"
docker push "$DockerHubUsername/musigo-frontend:v1.0.0"

# Push worker
Write-Host "   Pushing worker (17.5 GB - this will take a while)..." -ForegroundColor Gray
docker push "$DockerHubUsername/musigo-worker:latest"
docker push "$DockerHubUsername/musigo-worker:v1.0.0"

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "SUCCESS: Images pushed to Docker Hub" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your images are now available at:" -ForegroundColor White
Write-Host "  - $DockerHubUsername/musigo-backend:latest" -ForegroundColor Gray
Write-Host "  - $DockerHubUsername/musigo-frontend:latest" -ForegroundColor Gray
Write-Host "  - $DockerHubUsername/musigo-worker:latest" -ForegroundColor Gray
Write-Host ""
Write-Host "To use in docker-compose.yml:" -ForegroundColor Yellow
Write-Host "  Replace 'build: ...' with 'image: $DockerHubUsername/musigo-backend:latest'" -ForegroundColor Gray
Write-Host ""
