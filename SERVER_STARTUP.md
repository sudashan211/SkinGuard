# SkinGuard Server Startup Guide

**IMPORTANT**: Read this document every time before starting the servers!

## Quick Start Commands

### 1. Start Backend Server (Port 8001)
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### 2. Start Frontend Server (Port 3000)
```bash
cd frontend
npm run dev
```

## Server Configuration

### Backend API
- **Port**: `8001` (NOT 8000!)
- **URL**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs
- **Working Directory**: `backend/`
- **Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8001`

### Frontend Application
- **Port**: `3000`
- **URL**: http://localhost:3000
- **Working Directory**: `frontend/`
- **Command**: `npm run dev`
- **Environment**: Uses `VITE_API_URL=http://localhost:8001` from `frontend/.env`

### PostgreSQL Database
- **Port**: `5432`
- **Host**: localhost
- **Database**: `skinguard`
- **Username**: `postgres`
- **Password**: `12345`
- **Connection**: `postgresql://postgres:12345@localhost:5432/skinguard`

## Pre-Startup Checklist

### ✅ Before Starting Backend:
1. PostgreSQL is running (check pgAdmin or Task Manager)
2. Database `skinguard` exists
3. All tables are created (run `database_setup.sql` if needed)
4. `backend/.env` file exists with correct settings
5. Virtual environment is activated (if using one)

### ✅ Before Starting Frontend:
1. `frontend/.env` file exists
2. `VITE_API_URL=http://localhost:8001` is set correctly
3. Node modules are installed (`npm install` if needed)
4. Backend server is running on port 8001

## Environment Variables

### Backend (.env in backend/)
```env
DATABASE_URL=postgresql://postgres:12345@localhost:5432/skinguard
USE_REAL_AI=true
API_PORT=8001
```

### Frontend (.env in frontend/)
```env
VITE_API_URL=http://localhost:8001
VITE_SUPABASE_URL=https://fqvxrlltwymecsuqfzcg.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
VITE_GOOGLE_MAPS_API_KEY=AIzaSyC6O-zjhPXY0o5mbu5PJNwstS1D_4LUGeY
```

## User Accounts

### Patient Account
- **Email**: sudashanrao0702@gmail.com
- **Password**: Password123

### Doctor Accounts
1. doctor@skinguard.com / Doctor123
2. pratap@gmail.com / (user set)
3. kesava@gmaill.com / Kesava55
4. satya@gmail.com / (user set)

### Admin Account
- **Email**: admin@skinguard.com
- **Password**: Admin123

## Startup Sequence

### Step 1: Start PostgreSQL
- Open pgAdmin 4 or ensure PostgreSQL service is running
- Verify connection to `skinguard` database

### Step 2: Start Backend (Terminal 1)
```bash
cd D:\SkinGuard\backend
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

**Expected Output:**
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

### Step 3: Start Frontend (Terminal 2)
```bash
cd D:\SkinGuard\frontend
npm run dev
```

**Expected Output:**
```
VITE v5.4.21  ready in 549 ms
➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

### Step 4: Verify Services
1. Open http://localhost:8001/docs - Should show Swagger API docs
2. Open http://localhost:3000 - Should show SkinGuard login page
3. Test login with any account above

## Common Issues & Solutions

### Issue: Backend shows "Port 8001 already in use"
**Solution:**
```bash
# Find process using port 8001
netstat -ano | findstr :8001

# Kill the process
taskkill /PID <process_id> /F

# Restart backend
```

### Issue: Frontend shows "Failed to fetch" or "ERR_CONNECTION_REFUSED"
**Cause**: Backend is not running or running on wrong port

**Solution:**
1. Check backend is running: http://localhost:8001/docs
2. Verify `frontend/.env` has `VITE_API_URL=http://localhost:8001`
3. Hard refresh browser (Ctrl+Shift+R)
4. Restart frontend server

### Issue: Database connection errors
**Solution:**
1. Check PostgreSQL is running
2. Verify credentials: postgres/12345
3. Ensure database `skinguard` exists
4. Check `backend/.env` has correct `DATABASE_URL`

### Issue: Admin dashboard shows connection errors
**Cause**: Hardcoded URLs or browser cache

**Solution:**
1. Hard refresh browser (Ctrl+Shift+R or Ctrl+F5)
2. Clear browser cache
3. Verify all admin components use `import.meta.env.VITE_API_URL`
4. Restart frontend server

### Issue: AI model loading errors
**Expected**: Some TensorFlow warnings are normal
```
AttributeError: 'MessageFactory' object has no attribute 'GetPrototype'
```
These warnings don't affect functionality - the AI model still works!

## Port Reference

| Service | Port | URL |
|---------|------|-----|
| Backend API | 8001 | http://localhost:8001 |
| Frontend | 3000 | http://localhost:3000 |
| PostgreSQL | 5432 | localhost:5432 |
| API Docs | 8001 | http://localhost:8001/docs |

## Important Notes

### ⚠️ CRITICAL: Port Configuration
- **Backend MUST run on port 8001** (not 8000!)
- **Frontend MUST run on port 3000**
- All frontend API calls use `import.meta.env.VITE_API_URL`
- Never hardcode `http://localhost:8000` in any file!

### 🔧 Configuration Files
- `backend/.env` - Backend environment variables
- `frontend/.env` - Frontend environment variables (includes API URL)
- `database_setup.sql` - Database schema
- `docs/PORT_CONFIGURATION.md` - Detailed port documentation

### 📝 Database Mode
- **Production Mode**: Using PostgreSQL (pgAdmin)
- **NOT using Supabase** (cloud database disabled)
- All data stored locally in PostgreSQL

### 🤖 AI Model
- **Real AI Model**: 96.95% accuracy
- `USE_REAL_AI=true` in backend/.env
- Model loads on backend startup (takes ~10 seconds)
- TensorFlow warnings are normal and can be ignored

## Stopping Servers

### Stop Backend
- Press `Ctrl+C` in backend terminal

### Stop Frontend
- Press `Ctrl+C` in frontend terminal

### Stop PostgreSQL
- Use pgAdmin or Windows Services
- Not recommended to stop unless necessary

## Testing After Startup

### 1. Test Backend API
```bash
curl http://localhost:8001/docs
```
Should return Swagger UI HTML

### 2. Test Frontend
Open http://localhost:3000 in browser
Should show login page

### 3. Test Database Connection
Login to any account and try creating a report
Should work without errors

### 4. Test Admin Dashboard
1. Login as admin@skinguard.com / Admin123
2. Navigate to Admin Dashboard
3. Click "System Health" - should load without errors
4. Click "User Management" - should show users
5. Click "Audit Logs" - should show logs

## Maintenance Commands

### Update Database Schema
```bash
psql -U postgres -d skinguard -f database_setup.sql
```

### Clear Python Cache (if code changes not reflecting)
```bash
cd backend
find . -type d -name __pycache__ -exec rm -rf {} +
# Or on Windows:
# Get-ChildItem -Path . -Filter __pycache__ -Recurse | Remove-Item -Recurse -Force
```

### Reinstall Frontend Dependencies
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

**Last Updated**: April 3, 2026  
**Version**: PostgreSQL Production Mode  
**Status**: All systems operational ✅
