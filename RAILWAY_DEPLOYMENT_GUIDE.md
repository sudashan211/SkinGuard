# Railway Deployment Guide - SkinGuard via GitHub

This guide walks you through deploying your SkinGuard application to Railway using GitHub integration.

---

## 📋 Prerequisites

Before starting, make sure you have:

✅ **GitHub Account** - Sign up at https://github.com if you don't have one
✅ **Railway Account** - Sign up at https://railway.app (can use GitHub login)
✅ **Git installed** - Check with `git --version` in terminal
✅ **Your code ready** - All code committed and working locally

---

## 🚀 STEP-BY-STEP DEPLOYMENT PROCESS

### **STEP 1: Prepare Your GitHub Repository**

#### 1.1 Create a GitHub Repository

1. Go to https://github.com
2. Click the **"+"** icon (top right) → **"New repository"**
3. Fill in:
   - **Repository name:** `SkinGuard` or `skinguard-app`
   - **Description:** "AI-Powered Skin Cancer Detection System"
   - **Visibility:** Choose **Private** (recommended) or Public
   - **DO NOT** initialize with README (we already have code)
4. Click **"Create repository"**

#### 1.2 Push Your Code to GitHub

Open terminal in your project root (`d:\SkinGuard`) and run:

```bash
# Initialize git (if not already initialized)
git init

# Add all files
git add .

# Commit your code
git commit -m "Initial commit - SkinGuard application ready for Railway deployment"

# Add your GitHub repository as remote (replace with YOUR repository URL)
git remote add origin https://github.com/YOUR_USERNAME/SkinGuard.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Important:** Replace `YOUR_USERNAME` with your actual GitHub username!

---

### **STEP 2: Create Railway Configuration Files**

Railway needs specific configuration files to know how to deploy your app. Let me check if you have them...

#### 2.1 Backend Configuration

Create `backend/railway.json`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

Create `backend/Procfile`:

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Create `backend/runtime.txt`:

```
python-3.11
```

#### 2.2 Frontend Configuration

Create `frontend/railway.json`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "npm run dev -- --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100
  }
}
```

---

### **STEP 3: Update Your Code for Railway**

#### 3.1 Backend Changes

**Update `backend/app/main.py`** - Add this near the top after imports:

```python
import os

# Get PORT from environment variable (Railway sets this)
PORT = int(os.getenv("PORT", 8001))

# Update CORS to allow Railway domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.railway.app",  # Allow Railway frontend
        "https://*.up.railway.app"  # Allow Railway custom domains
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 3.2 Frontend Changes

**Update `frontend/vite.config.ts`** - Add server configuration:

```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: parseInt(process.env.PORT || '3000'),
    strictPort: false,
  },
  preview: {
    host: '0.0.0.0',
    port: parseInt(process.env.PORT || '3000'),
  }
})
```

**Update `frontend/package.json`** - Add build script for production:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview --host 0.0.0.0 --port $PORT",
    "start": "vite preview --host 0.0.0.0 --port $PORT"
  }
}
```

#### 3.3 Update Environment Variables

Make sure your `.env` files don't contain sensitive data, as Railway will use its own environment variables.

**Backend:** Create `.env.example` with placeholder values
**Frontend:** Create `.env.example` with placeholder values

---

### **STEP 4: Deploy to Railway**

#### 4.1 Connect Railway to GitHub

1. Go to https://railway.app
2. Click **"Login"** → **"Login with GitHub"**
3. Authorize Railway to access your GitHub account

#### 4.2 Create a New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your **SkinGuard** repository
4. Railway will detect your project structure

#### 4.3 Deploy Backend Service

1. Railway will show your repository
2. Click **"Add Service"** → **"GitHub Repo"**
3. Select **SkinGuard** repository
4. Configure:
   - **Service Name:** `skinguard-backend`
   - **Root Directory:** `backend`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### 4.4 Add PostgreSQL Database

1. In your Railway project, click **"New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway will automatically create a PostgreSQL database
3. Railway provides these environment variables automatically:
   - `DATABASE_URL`
   - `PGHOST`
   - `PGPORT`
   - `PGUSER`
   - `PGPASSWORD`
   - `PGDATABASE`

#### 4.5 Configure Backend Environment Variables

1. Click on your **backend service**
2. Go to **"Variables"** tab
3. Add these environment variables:

```
DATABASE_URL=${{Postgres.DATABASE_URL}}
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
HUGGINGFACE_API_KEY=your-huggingface-api-key
ENVIRONMENT=production
```

**Important:** Replace placeholder values with your actual credentials!

#### 4.6 Deploy Frontend Service

1. Click **"New"** → **"GitHub Repo"**
2. Select **SkinGuard** repository again
3. Configure:
   - **Service Name:** `skinguard-frontend`
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Start Command:** `npm run preview -- --host 0.0.0.0 --port $PORT`

#### 4.7 Configure Frontend Environment Variables

1. Click on your **frontend service**
2. Go to **"Variables"** tab
3. Add this variable:

```
VITE_API_URL=${{skinguard-backend.RAILWAY_PUBLIC_DOMAIN}}
```

This automatically connects your frontend to the backend!

---

### **STEP 5: Run Database Migrations**

After backend deployment, you need to set up your database:

#### Option 1: Use Railway CLI (Recommended)

1. Install Railway CLI:
```bash
npm i -g @railway/cli
```

2. Login to Railway:
```bash
railway login
```

3. Link to your project:
```bash
railway link
```

4. Run database setup:
```bash
railway run --service backend python -c "from app.database import init_db; init_db()"
```

Or run your SQL setup:
```bash
railway run --service backend psql $DATABASE_URL -f database_setup.sql
```

#### Option 2: Use Railway Dashboard

1. Go to your **PostgreSQL service** in Railway
2. Click **"Data"** tab
3. Click **"Query"** and paste your `database_setup.sql` content
4. Click **"Run"**

---

### **STEP 6: Configure Custom Domains (Optional)**

#### 6.1 Get Railway URLs

Railway provides automatic URLs like:
- Backend: `https://skinguard-backend-production-abc123.up.railway.app`
- Frontend: `https://skinguard-frontend-production-xyz789.up.railway.app`

#### 6.2 Update CORS Settings

Update your backend CORS to include the Railway frontend URL:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://skinguard-frontend-production-xyz789.up.railway.app",  # Your Railway frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 6.3 Add Custom Domain (Optional - Requires Paid Plan)

1. Click on your service → **"Settings"**
2. Scroll to **"Domains"**
3. Click **"Generate Domain"** for a Railway subdomain
4. Or **"Custom Domain"** to add your own domain

---

### **STEP 7: Verify Deployment**

#### 7.1 Check Backend Health

Visit: `https://your-backend-url.railway.app/health`

Should return:
```json
{"status": "healthy"}
```

#### 7.2 Check Frontend

Visit: `https://your-frontend-url.railway.app`

The SkinGuard homepage should load!

#### 7.3 Test Full Workflow

1. Register a new account
2. Upload an image
3. Complete symptom questionnaire
4. View AI analysis results
5. Search for hospitals
6. Book an appointment

---

## 🔧 TROUBLESHOOTING

### Backend Issues

**Problem:** Backend won't start
- **Solution:** Check logs in Railway dashboard → Backend service → **"Deployments"** → Click latest deployment → **"View Logs"**
- Common issue: Missing environment variables

**Problem:** Database connection failed
- **Solution:** Verify `DATABASE_URL` is set correctly in backend environment variables
- Use Railway's built-in PostgreSQL reference: `${{Postgres.DATABASE_URL}}`

**Problem:** CORS errors
- **Solution:** Add your Railway frontend URL to CORS allowed origins in `main.py`

### Frontend Issues

**Problem:** Frontend can't connect to backend
- **Solution:** Check `VITE_API_URL` environment variable points to correct backend URL
- Format: `https://your-backend-url.railway.app`

**Problem:** Build fails
- **Solution:** Check Node version matches your local setup
- Update `package.json` engines field:
```json
"engines": {
  "node": ">=18.0.0",
  "npm": ">=9.0.0"
}
```

### Database Issues

**Problem:** Tables don't exist
- **Solution:** Run database migrations using Railway CLI or dashboard query

**Problem:** Connection pooling errors
- **Solution:** Add connection pool settings to database config

---

## 💰 RAILWAY PRICING (as of 2024)

### Free Tier (Hobby Plan)
- ✅ $5 monthly credit (with GitHub Student Pack: $10)
- ✅ 500 execution hours/month
- ✅ Shared CPU
- ✅ 512 MB RAM per service
- ✅ 1 GB disk
- ✅ Automatic HTTPS
- ✅ Community support

### Pro Plan - $20/month
- ✅ Included $20 credit + pay-as-you-go
- ✅ Priority builds
- ✅ More resources
- ✅ Custom domains
- ✅ Team collaboration
- ✅ Priority support

**Estimated Cost for SkinGuard:**
- Backend: ~$3-5/month (512MB RAM, shared CPU)
- Frontend: ~$2-3/month (static hosting)
- PostgreSQL: ~$5-7/month (256MB RAM)
- **Total: ~$10-15/month** (fits in Hobby plan with GitHub Student Pack!)

---

## 📚 USEFUL RAILWAY COMMANDS

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# View logs
railway logs

# Run commands in Railway environment
railway run <command>

# Open Railway dashboard
railway open

# Deploy manually (if auto-deploy disabled)
railway up
```

---

## ✅ POST-DEPLOYMENT CHECKLIST

After successful deployment:

- [ ] Backend health check returns 200
- [ ] Frontend loads without errors
- [ ] Database tables created
- [ ] User registration works
- [ ] Image upload works
- [ ] AI analysis works
- [ ] Hospital search works (Google Maps API key set)
- [ ] Appointment booking works
- [ ] Email notifications work (SMTP configured)
- [ ] All environment variables set correctly
- [ ] CORS configured for Railway domains
- [ ] SSL/HTTPS working (automatic with Railway)

---

## 🎓 GitHub Student Pack Bonus

If you're a student, get free Railway credits!

1. Go to https://education.github.com/pack
2. Verify your student status
3. Get $10/month Railway credit (double the free tier!)
4. Also get free domains, hosting, and more!

---

## 📖 Additional Resources

- **Railway Docs:** https://docs.railway.app
- **Railway Templates:** https://railway.app/templates
- **Railway Discord:** https://discord.gg/railway (for support)
- **Railway Status:** https://railway.statuspage.io

---

## 🚨 SECURITY REMINDERS

**NEVER commit these to GitHub:**
- ❌ `.env` files with real credentials
- ❌ `DATABASE_URL` with passwords
- ❌ API keys (Google Maps, Hugging Face, SMTP passwords)
- ❌ JWT secrets

**Always use:**
- ✅ `.env.example` with placeholder values
- ✅ Railway environment variables for secrets
- ✅ `.gitignore` to exclude sensitive files

---

## 🎉 CONGRATULATIONS!

Your SkinGuard application is now live on Railway!

**Next Steps:**
1. Share your Railway URL with users
2. Monitor logs for errors
3. Set up custom domain (optional)
4. Configure backups for database
5. Set up monitoring/alerts

---

## 📞 Need Help?

If you encounter issues:
1. Check Railway logs (most informative!)
2. Review this guide's troubleshooting section
3. Ask on Railway Discord: https://discord.gg/railway
4. Check Railway docs: https://docs.railway.app

---

**Created:** 2026-07-06
**Last Updated:** 2026-07-06
**Guide Version:** 1.0

