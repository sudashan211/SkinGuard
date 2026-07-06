# Troubleshooting Guide - 403 Forbidden Errors

## Issue: Getting 403 Forbidden errors after login

### Root Cause
The authentication token refresh endpoint had an issue in demo mode, which has now been fixed. However, your browser still has old/invalid tokens stored.

### Solution: Clear Browser Storage and Re-login

Follow these steps:

#### Step 1: Clear Browser Storage
1. Open your browser's Developer Tools (F12)
2. Go to the "Application" tab (Chrome) or "Storage" tab (Firefox)
3. Find "Local Storage" in the left sidebar
4. Click on `http://localhost:3000`
5. **Delete these keys**:
   - `access_token`
   - `refresh_token`
   - `auth-storage`
6. Refresh the page (F5)

#### Step 2: Log In Again
1. You should now see the login page
2. Log in with demo credentials:
   - **Patient**: `patient@demo.com` / `demo123`
   - **Doctor**: `doctor@demo.com` / `demo123`
   - **Admin**: `admin@demo.com` / `demo123`

#### Step 3: Verify It Works
1. After login, you should be redirected to your dashboard
2. Try uploading an image (for patient account)
3. The 403 errors should be gone

### Alternative: Use Incognito/Private Window

If clearing storage doesn't work:
1. Open a new Incognito/Private browsing window
2. Navigate to http://localhost:3000
3. Log in with demo credentials
4. Everything should work fresh

### What Was Fixed

The backend had these issues that are now resolved:

1. ✅ **Token Refresh in Demo Mode**: The `/api/auth/refresh` endpoint now works correctly in demo mode
2. ✅ **User Profile Fields**: Added missing `updated_at` field to user profiles
3. ✅ **Analytics Demo Data**: Analytics dashboard now returns demo data instead of trying to query database

### Verify Backend is Working

You can test the backend directly:

```bash
# Test login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"patient@demo.com","password":"demo123"}'

# You should get a response with access_token and refresh_token
```

### Still Having Issues?

If you're still seeing 403 errors after clearing storage:

1. **Check the browser console** for the exact error message
2. **Check the Network tab** to see which endpoint is failing
3. **Restart both servers**:
   - Stop the frontend (Ctrl+C in the terminal)
   - Stop the backend (Ctrl+C in the terminal)
   - Start them again

### Common Mistakes

❌ **Don't do this**:
- Trying to use old tokens after backend changes
- Not clearing browser storage after fixes
- Using wrong credentials

✅ **Do this**:
- Clear browser storage after backend updates
- Use exact demo credentials
- Check that both servers are running

### Server Status Check

Run this command to verify servers are running:

```bash
# Check frontend
curl http://localhost:3000

# Check backend
curl http://localhost:8000/api/health
```

Both should return HTTP 200 OK.

---

## Quick Fix Summary

1. **Clear browser localStorage** (F12 → Application → Local Storage → Delete all)
2. **Refresh page** (F5)
3. **Log in again** with demo credentials
4. **Try uploading image** - should work now!

The backend fixes are already applied and the servers are running. You just need to clear the old tokens from your browser.
