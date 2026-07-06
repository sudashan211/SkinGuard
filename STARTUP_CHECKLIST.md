# 📋 SkinGuard Startup Checklist

Print this or keep it open when starting the servers!

## Pre-Startup Checks

### Database
- [ ] PostgreSQL service is running
- [ ] pgAdmin can connect to database
- [ ] Database `skinguard` exists
- [ ] All tables are created

### Backend
- [ ] Located in `backend/` directory
- [ ] `.env` file exists
- [ ] `DATABASE_URL=postgresql://postgres:12345@localhost:5432/skinguard`
- [ ] `USE_REAL_AI=true`
- [ ] `API_PORT=8001`

### Frontend
- [ ] Located in `frontend/` directory
- [ ] `.env` file exists
- [ ] `VITE_API_URL=http://localhost:8001` (NOT 8000!)
- [ ] `node_modules/` folder exists (run `npm install` if missing)

## Startup Commands

### Step 1: Start Backend
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

**Wait for this message:**
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

- [ ] Backend started successfully
- [ ] No error messages (TensorFlow warnings are OK)
- [ ] Port 8001 is listening

### Step 2: Start Frontend
```bash
cd frontend
npm run dev
```

**Wait for this message:**
```
➜  Local:   http://localhost:3000/
```

- [ ] Frontend started successfully
- [ ] Port 3000 is listening
- [ ] No compilation errors

## Post-Startup Verification

### Test Backend API
- [ ] Open http://localhost:8001/docs
- [ ] Swagger UI loads correctly
- [ ] API endpoints are visible

### Test Frontend
- [ ] Open http://localhost:3000
- [ ] Login page loads
- [ ] No console errors (F12)

### Test Login
- [ ] Login as patient: sudashanrao0702@gmail.com / Password123
- [ ] Dashboard loads
- [ ] Can navigate between pages

### Test Admin Dashboard
- [ ] Login as admin: admin@skinguard.com / Admin123
- [ ] Navigate to Admin Dashboard
- [ ] System Health loads (no port 8000 errors!)
- [ ] User Management loads
- [ ] Audit Logs loads

## Port Verification

Run these commands to verify ports:

```bash
# Check backend (should show port 8001)
netstat -ano | findstr :8001

# Check frontend (should show port 3000)
netstat -ano | findstr :3000

# Check database (should show port 5432)
netstat -ano | findstr :5432
```

- [ ] Backend on port 8001 ✅
- [ ] Frontend on port 3000 ✅
- [ ] PostgreSQL on port 5432 ✅

## Common Issues Quick Fix

### ❌ Port 8001 already in use
```bash
netstat -ano | findstr :8001
taskkill /PID <process_id> /F
```

### ❌ Frontend shows "ERR_CONNECTION_REFUSED"
1. Check backend is running: http://localhost:8001/docs
2. Hard refresh browser: Ctrl+Shift+R
3. Check frontend/.env has correct VITE_API_URL

### ❌ Database connection error
1. Check PostgreSQL is running
2. Verify credentials: postgres/12345
3. Test connection in pgAdmin

### ❌ Admin dashboard shows port 8000 errors
1. Hard refresh browser: Ctrl+Shift+R or Ctrl+F5
2. Clear browser cache
3. Restart frontend server

## URLs Reference Card

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Main application |
| Backend API | http://localhost:8001 | REST API |
| API Docs | http://localhost:8001/docs | Swagger UI |
| Database | localhost:5432 | PostgreSQL |

## Login Credentials Card

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@skinguard.com | Admin123 |
| Patient | sudashanrao0702@gmail.com | Password123 |
| Doctor | doctor@skinguard.com | Doctor123 |
| Doctor | kesava@gmaill.com | Kesava55 |

## Shutdown Procedure

### Stop Frontend
- [ ] Press Ctrl+C in frontend terminal
- [ ] Wait for "Process terminated"

### Stop Backend
- [ ] Press Ctrl+C in backend terminal
- [ ] Wait for "Shutting down"

### PostgreSQL
- [ ] Leave running (don't stop unless necessary)

## Notes Section

Use this space to note any issues or changes:

```
Date: _______________

Issues encountered:
_____________________________________
_____________________________________
_____________________________________

Solutions applied:
_____________________________________
_____________________________________
_____________________________________

Changes made:
_____________________________________
_____________________________________
_____________________________________
```

---

**Remember**: 
- Backend MUST be on port **8001** (not 8000!)
- Always hard refresh browser after code changes
- Check SERVER_STARTUP.md for detailed troubleshooting

**Status**: [ ] All systems operational ✅
