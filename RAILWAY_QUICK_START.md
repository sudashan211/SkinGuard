# 🚀 Railway Deployment - Quick Start Guide

## Steps to Deploy SkinGuard to Railway

### ✅ Prerequisites
- GitHub account
- Railway account (sign up at https://railway.app)
- Git installed on your computer

---

## 📝 STEP-BY-STEP (5 Minutes)

### 1️⃣ Push Code to GitHub

```bash
# In d:\SkinGuard directory, run:
git init
git add .
git commit -m "Ready for Railway deployment"
git remote add origin https://github.com/YOUR_USERNAME/SkinGuard.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username!

---

### 2️⃣ Connect Railway to GitHub

1. Go to https://railway.app
2. Click **"Login with GitHub"**
3. Authorize Railway

---

### 3️⃣ Create Railway Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your **SkinGuard** repository

---

### 4️⃣ Deploy Backend

1. Railway detects your repo
2. Click **"Add Service"**
3. Configure:
   - **Root Directory:** `backend`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

### 5️⃣ Add PostgreSQL Database

1. Click **"New"** → **"Database"** → **"PostgreSQL"**
2. Railway creates it automatically!

---

### 6️⃣ Set Backend Environment Variables

Click backend service → **"Variables"** → Add these:

```
DATABASE_URL=${{Postgres.DATABASE_URL}}
JWT_SECRET=your-secret-key-here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
GOOGLE_MAPS_API_KEY=your-key-here
HUGGINGFACE_API_KEY=your-key-here
ENVIRONMENT=production
```

---

### 7️⃣ Deploy Frontend

1. Click **"New"** → **"GitHub Repo"**
2. Select **SkinGuard** again
3. Configure:
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Start Command:** `npm run preview -- --host 0.0.0.0 --port $PORT`

---

### 8️⃣ Set Frontend Environment Variable

Click frontend service → **"Variables"** → Add:

```
VITE_API_URL=https://<your-backend-url>.up.railway.app
```

Replace `<your-backend-url>` with your actual backend URL from Railway!

---

### 9️⃣ Setup Database

Install Railway CLI:
```bash
npm i -g @railway/cli
railway login
railway link
```

Run database setup:
```bash
railway run --service backend psql $DATABASE_URL -f database_setup.sql
```

---

### 🎉 DONE! Your App is Live!

Visit your frontend URL: `https://<your-frontend>.up.railway.app`

---

## 🔍 Quick Checks

✅ Backend health: `https://<backend-url>/health`  
✅ Frontend loads without errors  
✅ Can register new account  
✅ Can upload image and get AI analysis  

---

## 💰 Cost Estimate

**Free Tier (with GitHub Student Pack):**
- $10/month credit
- Enough for SkinGuard (~$10-15/month estimated usage)

**Get GitHub Student Pack:** https://education.github.com/pack

---

## 🆘 Problems?

**Backend won't start?**
→ Check logs in Railway dashboard → Backend service → Deployments → View Logs

**Frontend can't connect?**
→ Verify `VITE_API_URL` points to correct backend URL

**Database errors?**
→ Make sure you ran the database setup SQL script

---

## 📚 Full Guide

For detailed instructions, see: `RAILWAY_DEPLOYMENT_GUIDE.md`

---

**Time to deploy:** ~5-10 minutes  
**Difficulty:** Easy  
**Cost:** Free (with student pack) or ~$10-15/month

