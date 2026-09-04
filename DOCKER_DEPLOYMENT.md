# 🐳 Docker Deployment Guide for Musigo

## Current Status

### Docker Images Built
- ✅ **Backend**: 17.4 GB (includes PyTorch, ChromaDB v0.5.23, ML models)
- ⏳ **Frontend**: Building (estimated 200-300 MB)
- ⏳ **Worker**: Building (estimated 17.5 GB, same as backend)

### Build in Progress
The frontend and worker images are currently being rebuilt with the latest code.

---

## Option 1: Local Docker Deployment (Current)

### What's Happening
```bash
docker-compose build --no-cache frontend worker
```
This rebuilds the frontend and worker containers with your latest code changes.

### After Build Completes
```bash
# Restart all services with new images
docker-compose down
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### Quick Deploy Script
I've created: **`rebuild-and-deploy.ps1`**
```powershell
.\rebuild-and-deploy.ps1
```
This will:
1. Stop all services
2. Rebuild all images
3. Start services
4. Check health
5. Show status

---

## Option 2: Push to Docker Hub (Public Registry)

### Why Push to Docker Hub?
- Share images across machines
- Deploy to cloud platforms (Railway, AWS, etc.)
- Pull pre-built images instead of building
- Version control for images

### Step 1: Login to Docker Hub
```powershell
docker login
# Enter your Docker Hub username and password
```

### Step 2: Use the Push Script
I've created: **`push-to-dockerhub.ps1`**
```powershell
.\push-to-dockerhub.ps1 YOUR_DOCKERHUB_USERNAME
```

This will:
1. Tag images with your username
2. Push to Docker Hub
3. Make them publicly available

### Step 3: Update docker-compose.yml
Replace build context with images:
```yaml
services:
  backend:
    image: your-username/musigo-backend:latest
    # Remove: build: ...
  
  frontend:
    image: your-username/musigo-frontend:latest
    # Remove: build: ...
  
  worker:
    image: your-username/musigo-worker:latest
    # Remove: build: ...
```

---

## Option 3: Push to GitHub Container Registry (GHCR)

### Advantages
- Free and unlimited for public repos
- Integrated with GitHub
- Better for CI/CD

### Step 1: Create Personal Access Token
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token with `write:packages` permission

### Step 2: Login to GHCR
```powershell
$env:CR_PAT = "YOUR_GITHUB_TOKEN"
echo $env:CR_PAT | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

### Step 3: Tag and Push
```powershell
# Tag images
docker tag musigo-backend:latest ghcr.io/YOUR_USERNAME/musigo-backend:latest
docker tag musigo-frontend:latest ghcr.io/YOUR_USERNAME/musigo-frontend:latest
docker tag musigo-worker:latest ghcr.io/YOUR_USERNAME/musigo-worker:latest

# Push to GHCR
docker push ghcr.io/YOUR_USERNAME/musigo-backend:latest
docker push ghcr.io/YOUR_USERNAME/musigo-frontend:latest
docker push ghcr.io/YOUR_USERNAME/musigo-worker:latest
```

---

## Current Build Progress

### Monitor Build
```powershell
# Check running build
docker-compose build --progress=plain

# Check images after build
docker images | Select-String "musigo"
```

### Build Times (Estimated)
- **Frontend**: 5-10 minutes (npm install, Next.js build)
- **Worker**: 20-25 minutes (Python deps, ML models - LARGE)
- **Total**: ~25-30 minutes for fresh build

### Large Context Transfer
The build is copying ~500 MB of context. This includes:
- `node_modules/` (frontend)
- `.venv/` or `venv/` (backend)
- `.next/` build cache
- Python `__pycache__`

**Optimization**: Add to `.dockerignore`:
```
node_modules
.next
__pycache__
*.pyc
.venv
venv
.git
.env
*.log
```

---

## After Images Are Built

### 1. Restart Services
```powershell
docker-compose down
docker-compose up -d
```

### 2. Verify All Services
```powershell
docker-compose ps
# All should show "healthy" or "Up"
```

### 3. Test Application
```powershell
# Backend health
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000

# ChromaDB
curl http://localhost:8001/api/v1/heartbeat
```

### 4. Check Logs
```powershell
# All services
docker-compose logs

# Specific service
docker-compose logs -f backend

# Last 50 lines
docker-compose logs --tail=50 backend
```

---

## Image Sizes

### Current Images
```
Backend:  17.4 GB (PyTorch 2.4.1 + ChromaDB + ML models)
Frontend: ~200 MB (Node.js + Next.js)
Worker:   17.5 GB (Same as backend + worker code)
```

### Why So Large?
**Backend/Worker**: Include machine learning libraries
- PyTorch: ~2 GB
- Sentence Transformers: ~500 MB
- ChromaDB: ~200 MB
- Models: ~500 MB
- Python deps: ~1 GB

### Optimization Options
1. **Multi-stage builds** (already using for frontend)
2. **Smaller base images** (already using alpine where possible)
3. **Optional ChromaDB** (can disable with `REQUIRE_CHROMA=false`)
4. **Layer caching** (docker-compose does this automatically)

---

## Deployment Platforms

### Railway (Recommended for Backend)
```yaml
# Use pre-built images
docker pull your-username/musigo-backend:latest
docker pull your-username/musigo-worker:latest
```

### Vercel (Recommended for Frontend)
- Deploys directly from GitHub
- No Docker needed
- Uses `frontend/` directory

### AWS ECS / GCP Cloud Run
```bash
# Push to respective container registries
# AWS ECR, GCP Artifact Registry
```

---

## Quick Reference Commands

### Rebuild Everything
```powershell
docker-compose build --no-cache
```

### Rebuild Specific Service
```powershell
docker-compose build --no-cache backend
```

### Pull from Registry
```powershell
docker-compose pull
```

### Start All Services
```powershell
docker-compose up -d
```

### Stop All Services
```powershell
docker-compose down
```

### Remove All (including volumes)
```powershell
docker-compose down -v
```

### View All Logs
```powershell
docker-compose logs -f
```

### Restart Single Service
```powershell
docker-compose restart backend
```

---

## Next Steps

1. ⏳ **Wait for current build to complete** (~20 more minutes)
2. ✅ **Restart services** with new images
3. ✅ **Test application** locally
4. 🚀 **Choose deployment option**:
   - Local only: You're done!
   - Docker Hub: Run `push-to-dockerhub.ps1`
   - Railway/Vercel: Follow deployment guides

---

## Support

### Check Build Progress
The build is currently running. You can see progress in the terminal.

### When Build Completes
You'll see:
```
[+] Building X.Xs (30/30) FINISHED
✔ Container musigo_frontend  Built
✔ Container musigo_worker    Built
```

### If Build Fails
Check logs:
```powershell
docker-compose build frontend 2>&1 | Select-String "error"
```

---

*Docker images being built with latest Musigo code including ChromaDB v0.5.23*
