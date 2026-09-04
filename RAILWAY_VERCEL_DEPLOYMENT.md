# 🚀 Musigo Deployment Guide - Railway + Vercel

## Overview
This guide will walk you through deploying Musigo's **backend** to Railway (with PostgreSQL and Redis) and the **frontend** to Vercel.

**Deployment Stack:**
- 🚂 **Railway**: Backend API + PostgreSQL + Redis
- ▲ **Vercel**: Next.js Frontend
- 🎵 **Spotify API**: Already configured

---

## Prerequisites Checklist

### ✅ Before You Start
- [ ] GitHub account (for both Railway and Vercel)
- [ ] Your code pushed to GitHub repository
- [ ] Spotify API credentials (already configured ✅)
- [ ] Credit card (optional, for Railway beyond free tier)

### ✅ What You Have Ready
- ✅ Backend optimized and tested (51/52 tests passing)
- ✅ Frontend built successfully
- ✅ Docker containers working
- ✅ Environment variables configured
- ✅ Spotify API credentials active

---

## Part 1: Deploy Backend to Railway 🚂

### Step 1: Push Code to GitHub

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Ready for deployment"

# Add your GitHub repository
git remote add origin https://github.com/YOUR_USERNAME/musigo.git

# Push to GitHub
git push -u origin main
```

### Step 2: Sign Up for Railway

1. Go to **https://railway.app/**
2. Click **"Start a New Project"**
3. Sign in with **GitHub**
4. Authorize Railway to access your repositories

### Step 3: Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your **Musigo repository**
4. Railway will detect your `docker-compose.yml`

### Step 4: Configure Services

Railway will detect multiple services. You need to deploy **3 services**:

#### Service 1: PostgreSQL Database
1. Click **"Add Service"** → **"Database"** → **"PostgreSQL"**
2. Railway automatically provisions PostgreSQL
3. Note: Connection details are auto-configured

#### Service 2: Redis Cache
1. Click **"Add Service"** → **"Database"** → **"Redis"**
2. Railway automatically provisions Redis
3. Note: Connection details are auto-configured

#### Service 3: Backend API
1. Railway should auto-detect your backend service
2. If not, click **"New"** → **"GitHub Repo"** → Select **backend**

### Step 5: Configure Backend Environment Variables

Click on your **Backend service** → **"Variables"** → Add these:

```bash
# Application
DEBUG=False
PORT=8000
ENVIRONMENT=production

# Database (Railway will provide this automatically)
# DATABASE_URL=${POSTGRES_URL}  # Railway auto-sets this

# Security - IMPORTANT: Generate a new secret!
SECRET_KEY=<GENERATE-STRONG-32-CHAR-SECRET>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Spotify API (your credentials)
SPOTIFY_CLIENT_ID=<your-spotify-client-id>
SPOTIFY_CLIENT_SECRET=<your-spotify-client-secret>

# Redis (Railway will provide this)
# REDIS_URL=${REDIS_URL}  # Railway auto-sets this

# Vector Database (disable for free tier)
REQUIRE_CHROMA=false
CHROMA_PERSIST_DIR=/app/chroma_db

# CORS - Update with your Vercel domain
CORS_ORIGINS=["https://your-app.vercel.app","https://musigo.vercel.app"]

# Rate Limiting (use Redis)
RATE_LIMIT_STORAGE=${REDIS_URL}/1

# File Storage
UPLOAD_DIR=/app/uploads
MAX_UPLOAD_SIZE=52428800
```

**🔐 Generate SECRET_KEY:**
```bash
# Run this in your terminal to generate a secure key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 6: Reference Database URLs

Railway automatically creates environment variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string

Make sure your backend service references them:
1. In Railway Backend → **Variables**
2. Click **"Reference"** → Select `DATABASE_URL` from PostgreSQL service
3. Click **"Reference"** → Select `REDIS_URL` from Redis service

### Step 7: Configure Dockerfile Path

1. In Backend service → **Settings**
2. Set **"Root Directory"**: `backend`
3. Set **"Dockerfile Path"**: `backend/Dockerfile`
4. Set **"Start Command"**: (Railway will use Dockerfile CMD automatically)

### Step 8: Deploy Backend

1. Railway automatically deploys on push
2. Wait for build to complete (~3-5 minutes)
3. Once deployed, click **"Deployments"** to see logs
4. Check for any errors

### Step 9: Get Backend URL

1. In Backend service → **Settings** → **Networking**
2. Click **"Generate Domain"**
3. Railway will generate a URL like: `musigo-backend.up.railway.app`
4. **Copy this URL** - you'll need it for Vercel!

### Step 10: Test Backend

```bash
# Test health endpoint
curl https://your-backend.up.railway.app/api/health

# Test Spotify integration
curl "https://your-backend.up.railway.app/api/songs/search?q=test&limit=1"
```

---

## Part 2: Deploy Frontend to Vercel ▲

### Step 1: Sign Up for Vercel

1. Go to **https://vercel.com/**
2. Click **"Sign Up"**
3. Sign in with **GitHub**
4. Authorize Vercel to access your repositories

### Step 2: Import Project

1. Click **"Add New..."** → **"Project"**
2. Select **"Import Git Repository"**
3. Find and select your **Musigo repository**
4. Click **"Import"**

### Step 3: Configure Build Settings

Vercel should auto-detect Next.js. Verify these settings:

```
Framework Preset: Next.js
Root Directory: frontend
Build Command: npm run build
Output Directory: .next
Install Command: npm install
```

### Step 4: Configure Environment Variables

Click **"Environment Variables"** and add:

```bash
# Backend API URL (from Railway Step 9)
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app

# App Configuration
NEXT_PUBLIC_APP_NAME=Musigo
NEXT_PUBLIC_APP_DESCRIPTION=Discover music through AI-powered recommendations
```

**Important:** Replace `your-backend.up.railway.app` with your actual Railway backend URL!

### Step 5: Deploy Frontend

1. Click **"Deploy"**
2. Wait for build (~2-3 minutes)
3. Vercel will provide a preview URL

### Step 6: Get Frontend URL

After deployment completes:
1. Vercel provides a URL like: `musigo-frontend.vercel.app`
2. **Copy this URL**

### Step 7: Update Backend CORS

Go back to **Railway** → **Backend service** → **Variables**:

Update `CORS_ORIGINS`:
```json
["https://musigo-frontend.vercel.app","https://musigo-frontend-git-main-yourname.vercel.app"]
```

**Redeploy backend** after updating CORS!

### Step 8: Set Up Custom Domain (Optional)

1. In Vercel → **Settings** → **Domains**
2. Add your custom domain (e.g., `musigo.com`)
3. Follow Vercel's DNS configuration instructions
4. Update Railway CORS to include your custom domain

---

## Part 3: Final Verification ✅

### Test Complete Flow

1. **Open your Vercel URL** in browser
2. **Test homepage** - Should load with animations
3. **Test search** - Try: "upbeat songs for workout"
4. **Test navigation** - Click Discover, Library, Trending
5. **Test Spotify** - Search should return real songs
6. **Check console** - No CORS errors
7. **Test music player** - Click a song to play preview

### Verification Checklist

- [ ] Frontend loads successfully
- [ ] No console errors
- [ ] Search returns results from Spotify
- [ ] Navigation works across all pages
- [ ] Music player plays previews
- [ ] Backend API responding correctly
- [ ] No CORS errors in browser console
- [ ] PostgreSQL connected (check Railway logs)
- [ ] Redis connected (check Railway logs)

---

## Part 4: Monitoring & Maintenance 📊

### Railway Monitoring

1. **Logs**: Backend service → **Deployments** → View logs
2. **Metrics**: Monitor CPU, memory, network usage
3. **Database**: PostgreSQL service → Check connections, queries
4. **Redis**: Redis service → Monitor cache hits/misses

### Vercel Monitoring

1. **Analytics**: Built-in analytics dashboard
2. **Logs**: View deployment and function logs
3. **Performance**: Core Web Vitals tracking

### Set Up Alerts

**Railway:**
- Enable deployment notifications in settings
- Set up Slack/Discord webhooks for errors

**Vercel:**
- Enable deployment notifications
- Set up email alerts for failed deployments

---

## Troubleshooting Guide 🔧

### Common Issues

#### 1. Backend Won't Start
**Error:** `500 Internal Server Error`

**Solution:**
```bash
# Check Railway logs
1. Go to Backend service → Deployments
2. Click latest deployment → View logs
3. Look for database connection errors
4. Verify DATABASE_URL is referenced correctly
```

#### 2. CORS Errors
**Error:** `Access to fetch blocked by CORS policy`

**Solution:**
```bash
# Update CORS_ORIGINS in Railway backend
CORS_ORIGINS=["https://your-vercel-app.vercel.app"]
# Redeploy backend
```

#### 3. Spotify API Not Working
**Error:** `Missing SPOTIFY_CLIENT_ID`

**Solution:**
```bash
# Verify in Railway Backend → Variables
SPOTIFY_CLIENT_ID=<your-spotify-client-id>
SPOTIFY_CLIENT_SECRET=<your-spotify-client-secret>
```

#### 4. Frontend Can't Connect to Backend
**Error:** `Network Error` or `ERR_CONNECTION_REFUSED`

**Solution:**
```bash
# Check Vercel environment variable
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
# Should NOT have trailing slash
# Redeploy frontend after fixing
```

#### 5. Database Connection Issues
**Error:** `Could not connect to database`

**Solution:**
```bash
# In Railway Backend service
1. Go to Variables
2. Ensure DATABASE_URL is referenced from PostgreSQL service
3. Check PostgreSQL service is running
4. View PostgreSQL logs for issues
```

---

## Cost Estimation 💰

### Railway Free Tier
- **$5/month free credit**
- Covers small applications
- Includes: PostgreSQL + Redis + Backend
- Estimated usage: ~$3-5/month for low traffic

### Vercel Free Tier
- **Completely free** for hobby projects
- 100 GB bandwidth/month
- Unlimited deployments
- Perfect for Musigo frontend

### Total Cost
- **Free**: If staying under Railway's $5 credit
- **~$5-10/month**: For moderate traffic
- **Scale up**: As needed with usage

---

## Production Checklist ✅

Before going live:

### Security
- [ ] Changed SECRET_KEY to strong random value
- [ ] Set DEBUG=False in production
- [ ] Updated CORS to production domains only
- [ ] Enabled HTTPS (Railway & Vercel do this automatically)
- [ ] Reviewed rate limiting settings

### Performance
- [ ] Tested with production database (PostgreSQL)
- [ ] Verified Redis caching works
- [ ] Checked API response times
- [ ] Optimized images (using Next.js Image)
- [ ] Enabled CDN (Vercel does this automatically)

### Monitoring
- [ ] Set up error tracking (consider Sentry)
- [ ] Enabled deployment notifications
- [ ] Configured database backups (Railway automatic)
- [ ] Set up uptime monitoring (UptimeRobot, BetterStack)

### Documentation
- [ ] Updated README with deployment URLs
- [ ] Documented environment variables
- [ ] Created user guide
- [ ] Set up status page

---

## Quick Command Reference

### Railway CLI (Optional)
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# View logs
railway logs

# Run migrations
railway run python manage.py migrate
```

### Vercel CLI (Optional)
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod

# View logs
vercel logs
```

---

## Next Steps After Deployment 🎯

1. **Test thoroughly** on production URLs
2. **Set up custom domain** (optional)
3. **Configure monitoring** and alerts
4. **Add analytics** (Google Analytics, Plausible)
5. **Create backup strategy** for database
6. **Document API** for future developers
7. **Set up CI/CD** for automatic deployments
8. **Add error tracking** (Sentry, Rollbar)
9. **Optimize performance** based on metrics
10. **Scale resources** as traffic grows

---

## Support Resources 📚

### Railway
- Documentation: https://docs.railway.app/
- Discord: https://discord.gg/railway
- Status: https://railway.app/status

### Vercel
- Documentation: https://vercel.com/docs
- Discord: https://vercel.com/discord
- Status: https://vercel-status.com/

### Musigo
- GitHub Issues: Your repository issues page
- Documentation: README.md in your repo

---

## Congratulations! 🎉

You've successfully deployed Musigo to production using Railway and Vercel!

Your app is now:
- ✅ Running on reliable infrastructure
- ✅ Using production-grade PostgreSQL
- ✅ Cached with Redis
- ✅ Deployed on CDN (Vercel)
- ✅ Auto-scaling as needed
- ✅ Monitored and logged

**Your Live URLs:**
- Frontend: `https://your-app.vercel.app`
- Backend: `https://your-backend.up.railway.app`

**Share your music discovery app with the world!** 🎵🌍
