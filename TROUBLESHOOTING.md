# 🔧 SkinGuard Troubleshooting Guide

Quick solutions to common issues when running SkinGuard.

## Table of Contents
1. [Backend Issues](#backend-issues)
2. [Frontend Issues](#frontend-issues)
3. [Database Issues](#database-issues)
4. [Port Conflicts](#port-conflicts)
5. [Authentication Issues](#authentication-issues)
6. [Admin Dashboard Issues](#admin-dashboard-issues)

---

## Backend Issues

### ❌ Backend won't start - "Port 8001 already in use"

**Symptoms:**
```
ERROR: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8001)
```

**Solution:**
```bash
# Find what's using port 8001
netstat -ano | findstr :8001

# Kill the process (replace <PID> with actual process ID)
taskkill /PID <PID> /F

# Restart backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### ❌ Database connection error

**Symptoms:**
```
psycopg2.OperationalError: could not connect to server
```

**Solutions:**
1. Check PostgreSQL is running:
   - Open Task Manager → Services
   - Look for "postgresql-x64-14" or similar
   - If not running, start it

2. Verify credentials:
   ```bash
   # Test connection
   psql -U postgres -d skinguard
   # Password: 12345
   ```

3. Check DATABASE_URL in `backend/.env`:
   ```env
   DATABASE_URL=postgresql://postgres:12345@localhost:5432/skinguard
   ```

### ❌ AI Model loading errors

**Symptoms:**
```
AttributeError: 'MessageFactory' object has no attribute 'GetPrototype'
```

**Solution:**
- These TensorFlow warnings are NORMAL and can be ignored
- The AI model still works correctly
- If model fails to load, check:
  - `USE_REAL_AI=true` in backend/.env
  - Model files exist in `backend/app/ai_model/`

### ❌ Import errors or module not found

**Symptoms:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

### ❌ Code changes not reflecting

**Solution:**
```bash
# Clear Python cache
cd backend
# Windows PowerShell:
Get-ChildItem -Path . -Filter __pycache__ -Recurse | Remove-Item -Recurse -Force

# Restart backend
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

---

## Frontend Issues

### ❌ Images not displaying in reports

**Symptoms:**
- Broken image icons in report history
- Images not showing in report detail page
- Comparison view shows broken images

**Solutions:**

1. **Check image URLs in browser console:**
   - Open DevTools (F12) → Network tab
   - Look for 404 errors on image requests
   - Verify URLs start with `http://localhost:8001/uploads/`

2. **Verify backend is serving images:**
   - Open http://localhost:8001/docs
   - Backend should be running
   - Check backend logs for image requests

3. **Check uploads directory exists:**
   ```bash
   # Should have files
   ls backend/uploads/
   ```

4. **Hard refresh browser:**
   - Ctrl+Shift+R or Ctrl+F5
   - Clear browser cache

5. **Verify environment variable:**
   ```bash
   # Check frontend/.env
   VITE_API_URL=http://localhost:8001
   ```

**Technical Details:**
- Images stored in: `backend/uploads/{user_id}/{filename}.jpg`
- Database stores: `/uploads/{user_id}/{filename}.jpg`
- Frontend must prepend: `${import.meta.env.VITE_API_URL}`
- Final URL: `http://localhost:8001/uploads/{user_id}/{filename}.jpg`

See `docs/IMAGE_DISPLAY_FIX.md` for complete details.

### ❌ Frontend shows "Failed to fetch" or "ERR_CONNECTION_REFUSED"

**Symptoms:**
```
GET http://localhost:8001/api/... net::ERR_CONNECTION_REFUSED
```

**Solutions:**

1. **Check backend is running:**
   - Open http://localhost:8001/docs
   - Should show Swagger UI
   - If not, start backend first

2. **Verify environment variable:**
   ```bash
   # Check frontend/.env
   VITE_API_URL=http://localhost:8001
   ```
   - Must be port 8001, NOT 8000!

3. **Hard refresh browser:**
   - Chrome/Edge: Ctrl+Shift+R or Ctrl+F5
   - Firefox: Ctrl+Shift+R
   - Clear cache if needed

4. **Restart frontend:**
   ```bash
   # Stop frontend (Ctrl+C)
   cd frontend
   npm run dev
   ```

### ❌ Frontend won't start - "Port 3000 already in use"

**Solution:**
```bash
# Find what's using port 3000
netstat -ano | findstr :3000

# Kill the process
taskkill /PID <PID> /F

# Restart frontend
cd frontend
npm run dev
```

### ❌ Compilation errors

**Symptoms:**
```
ERROR in ./src/...
Module not found
```

**Solutions:**

1. **Reinstall dependencies:**
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Check TypeScript errors:**
   ```bash
   npm run build
   ```

### ❌ Environment variables not loading

**Symptoms:**
- API calls go to wrong URL
- Features not working

**Solution:**
```bash
# Restart frontend after changing .env
# Vite only loads .env on startup
cd frontend
# Stop with Ctrl+C
npm run dev
```

---

## Database Issues

### ❌ Database "skinguard" does not exist

**Solution:**
```bash
# Create database
psql -U postgres
CREATE DATABASE skinguard;
\q

# Run setup script
psql -U postgres -d skinguard -f database_setup.sql
```

### ❌ Tables don't exist

**Symptoms:**
```
relation "profiles" does not exist
```

**Solution:**
```bash
# Run database setup
psql -U postgres -d skinguard -f database_setup.sql
```

### ❌ Password authentication failed

**Solution:**
1. Reset PostgreSQL password:
   ```bash
   psql -U postgres
   ALTER USER postgres PASSWORD '12345';
   ```

2. Update backend/.env:
   ```env
   DATABASE_URL=postgresql://postgres:12345@localhost:5432/skinguard
   ```

### ❌ Connection timeout

**Solution:**
1. Check PostgreSQL is listening:
   ```bash
   netstat -ano | findstr :5432
   ```

2. Check postgresql.conf:
   - listen_addresses = 'localhost'
   - port = 5432

---

## Port Conflicts

### Quick Port Check

```bash
# Check all required ports
netstat -ano | findstr :3000
netstat -ano | findstr :8001
netstat -ano | findstr :5432
```

### Port Reference
- Frontend: **3000**
- Backend: **8001** (NOT 8000!)
- Database: **5432**

### Kill Process by Port

```bash
# Windows
netstat -ano | findstr :<PORT>
taskkill /PID <PID> /F

# Example for port 8001
netstat -ano | findstr :8001
taskkill /PID 12345 /F
```

---

## Authentication Issues

### ❌ Login fails - "Invalid credentials"

**Solutions:**

1. **Verify account exists:**
   ```sql
   psql -U postgres -d skinguard
   SELECT email, role FROM profiles WHERE email = 'your@email.com';
   ```

2. **Reset password:**
   ```python
   # Use create_admin.py or similar script
   python create_admin.py
   ```

3. **Check password requirements:**
   - Minimum 8 characters
   - At least one uppercase letter
   - At least one lowercase letter
   - At least one digit

### ❌ Token expired or invalid

**Solution:**
```javascript
// Clear localStorage in browser console (F12)
localStorage.clear()
// Then login again
```

### ❌ "Unauthorized" or 401 errors

**Solutions:**

1. **Check token is being sent:**
   - Open browser DevTools (F12)
   - Network tab
   - Check request headers for: `Authorization: Bearer <token>`

2. **Login again:**
   - Token may have expired
   - Logout and login again

---

## Admin Dashboard Issues

### ❌ Admin dashboard shows "ERR_CONNECTION_REFUSED" on port 8000

**Symptoms:**
```
GET http://localhost:8000/api/admin/... net::ERR_CONNECTION_REFUSED
```

**This is the MOST COMMON issue!**

**Solutions:**

1. **Hard refresh browser:**
   - Ctrl+Shift+R or Ctrl+F5
   - This clears cached JavaScript

2. **Clear browser cache:**
   - Chrome: Settings → Privacy → Clear browsing data
   - Select "Cached images and files"
   - Clear data

3. **Verify environment variable:**
   ```bash
   # Check frontend/.env
   VITE_API_URL=http://localhost:8001
   ```

4. **Restart frontend:**
   ```bash
   cd frontend
   # Stop with Ctrl+C
   npm run dev
   ```

5. **Check code doesn't have hardcoded URLs:**
   - All admin components should use `import.meta.env.VITE_API_URL`
   - No hardcoded `http://localhost:8000`

### ❌ System Health shows "Failed to fetch"

**Solution:**
Same as above - hard refresh and verify backend is on port 8001

### ❌ User Management shows no users

**Solution:**
```sql
-- Check users exist in database
psql -U postgres -d skinguard
SELECT id, email, role FROM profiles;
```

---

## General Debugging Tips

### Check Server Status

```bash
# Backend
curl http://localhost:8001/docs

# Frontend
curl http://localhost:3000

# Database
psql -U postgres -d skinguard -c "SELECT version();"
```

### View Logs

**Backend logs:**
- Check terminal where backend is running
- Look for error messages and stack traces

**Frontend logs:**
- Open browser DevTools (F12)
- Console tab for JavaScript errors
- Network tab for API call failures

**Database logs:**
- Check PostgreSQL logs in data directory
- Usually in: `C:\Program Files\PostgreSQL\14\data\log\`

### Common Error Patterns

| Error Message | Likely Cause | Solution |
|---------------|--------------|----------|
| ERR_CONNECTION_REFUSED | Backend not running | Start backend |
| Port already in use | Process using port | Kill process |
| Module not found | Missing dependencies | npm install / pip install |
| Database does not exist | DB not created | Create database |
| Invalid credentials | Wrong password | Check credentials |
| Token expired | Old JWT token | Login again |
| CORS error | Wrong origin | Check CORS settings |

### Emergency Reset

If nothing works, try this complete reset:

```bash
# 1. Stop all servers
# Press Ctrl+C in all terminals

# 2. Kill all processes
taskkill /F /IM node.exe
taskkill /F /IM python.exe

# 3. Clear caches
cd backend
Get-ChildItem -Path . -Filter __pycache__ -Recurse | Remove-Item -Recurse -Force

cd ../frontend
rm -rf node_modules package-lock.json .vite
npm install

# 4. Verify environment files
# Check backend/.env has DATABASE_URL with port 8001
# Check frontend/.env has VITE_API_URL=http://localhost:8001

# 5. Restart PostgreSQL
# Use pgAdmin or Services

# 6. Start backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8001

# 7. Start frontend (new terminal)
cd frontend
npm run dev

# 8. Hard refresh browser
# Ctrl+Shift+R
```

---

## Still Having Issues?

### Checklist
- [ ] PostgreSQL is running
- [ ] Database `skinguard` exists
- [ ] Backend is on port 8001
- [ ] Frontend is on port 3000
- [ ] Environment files are correct
- [ ] Browser cache is cleared
- [ ] No port conflicts

### Get Help
1. Check SERVER_STARTUP.md for detailed startup guide
2. Review SYSTEM_ARCHITECTURE.md for system overview
3. Check backend terminal for error messages
4. Check browser console (F12) for frontend errors
5. Verify all ports with `netstat -ano`

---

**Last Updated**: April 3, 2026  
**Remember**: Backend on port 8001, NOT 8000! 🚨
