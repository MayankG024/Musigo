# Rebuild and Deploy Latest Musigo Version
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Rebuilding Musigo Docker Images" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Stop all services
Write-Host "1. Stopping all services..." -ForegroundColor Yellow
docker-compose down
Write-Host "   SUCCESS: Services stopped" -ForegroundColor Green
Write-Host ""

# Rebuild all images
Write-Host "2. Rebuilding all images (this may take 15-20 minutes)..." -ForegroundColor Yellow
docker-compose build --no-cache

if ($LASTEXITCODE -eq 0) {
    Write-Host "   SUCCESS: All images rebuilt" -ForegroundColor Green
} else {
    Write-Host "   FAILED: Build failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Start all services
Write-Host "3. Starting all services..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "   SUCCESS: All services started" -ForegroundColor Green
} else {
    Write-Host "   FAILED: Startup failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Wait for health checks
Write-Host "4. Waiting for services to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check status
Write-Host ""
Write-Host "5. Service Status:" -ForegroundColor Yellow
docker-compose ps
Write-Host ""

# Test backend
Write-Host "6. Testing backend health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
    Write-Host "   SUCCESS: Backend is healthy" -ForegroundColor Green
    Write-Host "   Status: $($health.status)" -ForegroundColor Gray
} catch {
    Write-Host "   WARNING: Backend not responding yet" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services running at:" -ForegroundColor White
Write-Host "  Frontend:  http://localhost:3000" -ForegroundColor Gray
Write-Host "  Backend:   http://localhost:8000" -ForegroundColor Gray
Write-Host "  API Docs:  http://localhost:8000/docs" -ForegroundColor Gray
Write-Host "  Redis:     localhost:6379" -ForegroundColor Gray
Write-Host "  Postgres:  localhost:5432" -ForegroundColor Gray
Write-Host "  ChromaDB:  http://localhost:8001" -ForegroundColor Gray
Write-Host ""
Write-Host "View logs: docker-compose logs -f [service-name]" -ForegroundColor Yellow
Write-Host "Stop all:  docker-compose down" -ForegroundColor Yellow
Write-Host ""
