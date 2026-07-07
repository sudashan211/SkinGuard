# Railway Deployment Fix Guide

## 🚨 CRITICAL ISSUE: DATABASE_URL Malformed

### Problem
The Railway backend is returning 500 errors because the `DATABASE_URL` environment variable contains the literal string "port" instead of the numeric port `5432`.

**Error from logs:**
```
psycopg2.OperationalError: invalid integer value "port" for connection option "port"
```

### Solution: Fix DATABASE_URL in Railway

1. **Go to Railway Dashboard**
   - Open: https://railway.app/dashboard
   - Navigate to your `skinguard-production` project
   - Click on the backend service

2. **Find the Correct Database URL from Supabase**
   - Go to Supabase Dashboard: https://supabase.com/dashboard
   - Select your project: `fqvxrlltwymecsuqfzcg`
   - Navigate to: Settings → Database → Connection String
   - Copy the **URI** format connection string (NOT the Transaction pooler)
   - It should look like:
     ```
     postgresql://postgres:[YOUR-PASSWORD]@db.fqvxrlltwymecsuqfzcg.supabase.co:5432/postgres
     ```

3. **Update DATABASE_URL in Railway**
   - In Railway backend service, go to **Variables** tab
   - Find `DATABASE_URL` variable
   - **Delete** the current malformed value
   - **Add new** `DATABASE_URL` with the correct connection string from Supabase
   - Make sure to replace `[YOUR-PASSWORD]` with your actual Supabase database password

4. **Railway Will Auto-Redeploy**
   - Railway automatically redeploys when environment variables change
   - Wait for the deployment to complete (watch the Deployments tab)
   - Check logs to confirm no more "invalid integer value 'port'" errors

---

## Issue 2: CORS Configuration

### Problem
Backend is returning `https://railway.com` as CORS origin instead of allowing the frontend domain.

### Solution: Update CORS_ORIGINS in Railway

1. **In Railway Variables tab**, update `CORS_ORIGINS`:
   ```
   http://localhost:3000,http://localhost:5173,https://skin-guard-4kxr.vercel.app
   ```

2. **Important Notes:**
   - NO spaces after commas
   - Include all necessary origins
   - Wildcard `["*"]` should only be used for testing, not production

---

## Issue 3: Vercel Frontend Using Old Railway URL

### Problem
Vercel is caching the old Railway URL in builds, causing 404 errors.

### Solution: Force Vercel to Use New Railway URL

1. **Delete Old Environment Variable** (This clears cache):
   - Go to Vercel Dashboard: https://vercel.com/dashboard
   - Select `skin-guard-4kxr` project
   - Go to Settings → Environment Variables
   - Find `VITE_API_URL`
   - Click the **three dots** → **Delete**
   - Confirm deletion

2. **Add Fresh Environment Variable**:
   - Click **Add New** button
   - Key: `VITE_API_URL`
   - Value: `https://skinguard-production-b846.up.railway.app`
   - Environments: **Check "Production"** (uncheck Development and Preview)
   - Click **Save**

3. **Trigger Manual Redeploy**:
   - Go to Deployments tab
   - Click the **three dots** on the latest deployment
   - Click **Redeploy**
   - Select **Use existing Build Cache: OFF** (important!)
   - Click **Redeploy**

4. **Alternative: Make a Git Commit to Force Fresh Build**:
   ```bash
   # Update the trigger file
   echo Updated: 2026-07-07 > VERCEL_REBUILD_TRIGGER.txt
   git add VERCEL_REBUILD_TRIGGER.txt
   git commit -m "Force Vercel rebuild with new Railway URL"
   git push origin main
   ```

---

## Verification Steps

### 1. Test Railway Backend Health
```bash
# Open in browser or use curl:
https://skinguard-production-b846.up.railway.app/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-07-07T...",
  "version": "1.0.0"
}
```

### 2. Check Railway Logs
- Go to Railway Dashboard → Backend Service → Logs
- Should NOT see any "invalid integer value 'port'" errors
- Should see successful startup messages

### 3. Test Frontend Login
- Open: https://skin-guard-4kxr.vercel.app
- Try to login or signup
- Open Browser DevTools (F12) → Console
- Should NOT see CORS errors
- Should NOT see 404 errors to old Railway URL

### 4. Check API Calls in Network Tab
- Browser DevTools → Network tab
- Try login
- Look for `/api/auth/login` request
- URL should be: `https://skinguard-production-b846.up.railway.app/api/auth/login`
- Response should be 200 (success) or proper error, NOT 500

---

## Environment Variables Reference

### Railway Backend Required Variables
```
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.fqvxrlltwymecsuqfzcg.supabase.co:5432/postgres
SUPABASE_URL=https://fqvxrlltwymecsuqfzcg.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=[Your service role key]
JWT_SECRET_KEY=[Your JWT secret]
USE_REAL_AI=true
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://skin-guard-4kxr.vercel.app
```

### Vercel Frontend Required Variables
```
VITE_API_URL=https://skinguard-production-b846.up.railway.app
VITE_SUPABASE_URL=https://fqvxrlltwymecsuqfzcg.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
VITE_GOOGLE_MAPS_API_KEY=AIzaSyCQolRXIHc3HZZA59TcAOPyzJ_qeAjJBYA
```

---

## Secondary Issues (Fix After Database URL)

### Scheduler Errors
```
AttributeError: 'TableQuery' object has no attribute 'lt'
AttributeError: 'TableQuery' object has no attribute 'not_'
```

**These are from the custom PostgreSQL wrapper** (`postgres_db.py`) missing Supabase methods. These errors are non-critical for login/signup but should be fixed for full functionality.

**To Fix:** Add missing methods to `TableQuery` class:
- `.lt()` - Less than comparison
- `.not_()` - NOT condition builder
- `.is_()` - NULL check

But **FIRST fix the DATABASE_URL** - that's blocking all database operations!

---

## Deployment URLs

- **Backend (Railway)**: https://skinguard-production-b846.up.railway.app
- **Frontend (Vercel)**: https://skin-guard-4kxr.vercel.app
- **GitHub Repo**: https://github.com/sudashan211/SkinGuard

---

## Next Steps After Fixing

1. ✅ Fix DATABASE_URL in Railway (CRITICAL - do this first!)
2. ✅ Update CORS_ORIGINS in Railway
3. ✅ Delete and re-add VITE_API_URL in Vercel
4. ✅ Redeploy Vercel without build cache
5. ✅ Test login at https://skin-guard-4kxr.vercel.app
6. Fix missing PostgreSQL wrapper methods (`lt`, `not_`, `is_`) for scheduler
7. Set up monitoring and error tracking (optional)

---

## Troubleshooting

### If Login Still Returns 500 After Fixing DATABASE_URL:
- Check Railway logs for new error messages
- Verify DATABASE_URL is correct (test connection locally)
- Check if Supabase database is accessible (not paused)

### If Frontend Still Shows 404 to Old URL:
- Clear browser cache and hard refresh (Ctrl+Shift+R)
- Check Vercel deployment logs to see which API URL was used in build
- Try incognito/private browser window

### If CORS Errors Persist:
- Verify CORS_ORIGINS has no spaces after commas
- Check Railway logs to see what origin is being set
- Test with wildcard temporarily: `CORS_ORIGINS=*`
