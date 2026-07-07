# 🚨 IMMEDIATE FIX STEPS - Do These Now!

## Step 1: Fix DATABASE_URL in Railway (CRITICAL)

### 1.1 Get Correct Database URL from Supabase
1. Open Supabase: https://supabase.com/dashboard
2. Click your project (`fqvxrlltwymecsuqfzcg`)
3. Go to: **Settings** → **Database** → **Connection String**
4. Select **URI** tab (NOT Transaction pooler)
5. Copy the connection string - it looks like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.fqvxrlltwymecsuqfzcg.supabase.co:5432/postgres
   ```
6. Replace `[YOUR-PASSWORD]` with your actual database password

### 1.2 Update Railway
1. Open Railway: https://railway.app/dashboard
2. Click your `skinguard-production` project
3. Click the **backend service**
4. Go to **Variables** tab
5. Find `DATABASE_URL`
6. Click **three dots** → **Edit**
7. Paste the corrected connection string
8. Click **Update**
9. Railway will automatically redeploy - **WAIT for this to complete!**

---

## Step 2: Fix Vercel Frontend URL (After Railway Deploys)

### 2.1 Delete Old Variable
1. Open Vercel: https://vercel.com/dashboard
2. Click `skin-guard-4kxr` project
3. Go to **Settings** → **Environment Variables**
4. Find `VITE_API_URL`
5. Click **three dots** → **Delete**
6. Confirm deletion

### 2.2 Add Fresh Variable
1. Click **Add New Variable**
2. **Key**: `VITE_API_URL`
3. **Value**: `https://skinguard-production-b846.up.railway.app`
4. **Environments**: Check **only Production** ✅
5. Click **Save**

### 2.3 Force Fresh Deploy
1. Go to **Deployments** tab
2. Click **three dots** on latest deployment → **Redeploy**
3. **UNCHECK** "Use existing Build Cache"
4. Click **Redeploy**

---

## Step 3: Verify Everything Works

### 3.1 Test Backend
Open in browser: https://skinguard-production-b846.up.railway.app/api/health

Expected:
```json
{"status":"healthy","timestamp":"...","version":"1.0.0"}
```

### 3.2 Test Frontend
1. Open: https://skin-guard-4kxr.vercel.app
2. Press **F12** (open DevTools)
3. Go to **Console** tab
4. Try to login or signup
5. Should see NO errors about:
   - ❌ "old URL" `s86fdp`
   - ❌ CORS policy
   - ❌ 500 Internal Server Error

---

## Step 4: Update Backend Code (Already Done Locally)

The PostgreSQL wrapper has been updated to fix scheduler errors. You need to commit and push:

```bash
cd d:\SkinGuard
git add backend/app/postgres_db.py
git commit -m "Fix PostgreSQL wrapper: add lt, gte, gt, lte, is_, not_ methods"
git push origin main
```

Railway will auto-deploy the updated code.

---

## Quick Checklist

- [ ] Got correct DATABASE_URL from Supabase
- [ ] Updated DATABASE_URL in Railway
- [ ] Waited for Railway deployment to complete
- [ ] Checked Railway logs (no more "port" errors)
- [ ] Deleted `VITE_API_URL` in Vercel
- [ ] Added fresh `VITE_API_URL` in Vercel (Production only)
- [ ] Redeployed Vercel without cache
- [ ] Tested backend health endpoint
- [ ] Tested frontend login (no CORS errors)
- [ ] Committed postgres_db.py changes
- [ ] Pushed to GitHub

---

## If Something Goes Wrong

### Railway still showing "port" error:
- Double-check DATABASE_URL value (no spaces, correct port `:5432`)
- Make sure it's `postgresql://` not `postgres://`
- Check Supabase database is not paused

### Vercel still using old URL:
- Clear browser cache (Ctrl + Shift + R)
- Try incognito mode
- Check Vercel deployment logs to see which API_URL was used

### Login returns 500:
- Check Railway logs for new error messages
- Verify DATABASE_URL connects successfully
- Test database connection from local backend

---

## Support Information

- **Backend URL**: https://skinguard-production-b846.up.railway.app
- **Frontend URL**: https://skin-guard-4kxr.vercel.app
- **Supabase Project**: `fqvxrlltwymecsuqfzcg`
- **GitHub**: https://github.com/sudashan211/SkinGuard

**DO STEP 1 FIRST!** Everything else depends on fixing the DATABASE_URL.
