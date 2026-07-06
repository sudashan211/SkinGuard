# Railway Deployment Error - Quick Fix Guide

## Error You're Seeing

```
⚠ Script start.sh not found
✖ Railpack could not determine how to build the app.
```

## Why This Happened

Your project is a **monorepo** (has both `backend/` and `frontend/` folders), but Railway doesn't know which part to deploy. It's looking for language files at the root level but they're in subdirectories.

---

## ✅ Solution: Deploy Backend and Frontend Separately

You need **TWO Railway services** - one for backend, one for frontend.

### 📘 BACKEND SERVICE (Deploy First)

#### In Railway Dashboard:

1. Click on your existing **"SkinGuard"** service
2. Go to **Settings** → Scroll to **"Root Directory"**
3. Set Root Directory to: `backend`
4. Scroll down → Click **"Redeploy"**

#### Environment Variables to Add:

Go to **Variables** tab and add:

```
DATABASE_URL=postgresql://user:pass@host:port/dbname
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
JWT_SECRET=your-secret-key-here
OPENAI_API_KEY=your_openai_key (optional)
```

#### Expected Behavior:
- Railway will detect `requirements.txt` in `backend/`
- Install Python dependencies
- Use the `Procfile` to start with: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Backend will be available at: `https://your-backend.railway.app`

---

### 🎨 FRONTEND SERVICE (Deploy Second)

#### In Railway Dashboard:

1. In your Railway project, click **"+ New"** → **"GitHub Repo"**
2. Select the **same** SkinGuard repository
3. Go to **Settings** → Set Root Directory to: `frontend`
4. Deploy

#### Environment Variables to Add:

Go to **Variables** tab and add:

```
VITE_API_URL=https://your-backend.railway.app
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_GOOGLE_MAPS_API_KEY=your_google_maps_key
```

#### Build Settings:

Railway should auto-detect from `package.json`:
- **Build Command:** `npm install && npm run build`
- **Start Command:** `npm run preview` (or Railway will serve the `dist/` folder)

#### Expected Behavior:
- Railway detects `package.json` in `frontend/`
- Runs `npm install` and `npm run build`
- Serves the built React app
- Frontend will be available at: `https://your-frontend.railway.app`

---

## 🔄 After Both Services Are Deployed

### Update Frontend Environment Variable:

1. Go to **Frontend service** → **Variables**
2. Update `VITE_API_URL` with your actual backend URL from Railway
3. Redeploy frontend

### Update Backend CORS Settings:

Make sure your backend allows requests from the frontend domain. Check `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend.railway.app",  # Add this
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🗄️ Database Setup (PostgreSQL)

### Option 1: Railway PostgreSQL (Recommended)

1. In your Railway project, click **"+ New"** → **"Database"** → **"PostgreSQL"**
2. Railway will automatically create a database
3. Copy the `DATABASE_URL` from Variables
4. Add it to your **Backend service** environment variables

### Option 2: Supabase PostgreSQL

If you're already using Supabase:
1. Get your connection string from Supabase dashboard
2. Add as `DATABASE_URL` in backend variables

---

## 📝 Summary

Your deployment needs:

1. **Backend Service**
   - Root Directory: `backend`
   - Environment: DATABASE_URL, SUPABASE_URL, SUPABASE_KEY, JWT_SECRET

2. **Frontend Service**  
   - Root Directory: `frontend`
   - Environment: VITE_API_URL (pointing to backend), VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY

3. **Database Service**
   - Railway PostgreSQL or Supabase

---

## 🆘 Troubleshooting

### If Backend Still Fails:

Check build logs for:
- Missing dependencies in `requirements.txt`
- Python version issues (Railway uses Python 3.11 by default)
- Port binding (must use `$PORT` environment variable)

### If Frontend Build Fails:

Check:
- All environment variables are prefixed with `VITE_`
- `npm run build` works locally
- TypeScript errors (Railway fails on TS errors)

---

## Need the Deployment Guide?

See `RAILWAY_DEPLOYMENT_GUIDE.md` for full step-by-step instructions.
