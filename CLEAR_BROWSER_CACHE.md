# How to Clear Browser Cache for SkinGuard

Your browser is caching the old JavaScript files. Here's how to fix it:

## Option 1: Hard Refresh (Easiest)
1. Go to http://localhost:3000
2. Hold **Ctrl + Shift** and press **R** (or **F5**)
3. Do this 2-3 times
4. Try signing up again

## Option 2: Clear Site Data (Most Effective)
1. Go to http://localhost:3000
2. Press **F12** to open Developer Tools
3. Right-click the **Refresh button** (next to address bar)
4. Select **"Empty Cache and Hard Reload"**
5. Close Developer Tools
6. Try signing up again

## Option 3: Manual Cache Clear
1. Press **Ctrl + Shift + Delete**
2. Select **"Last hour"** for time range
3. Check **"Cached images and files"**
4. Click **"Clear data"**
5. Go to http://localhost:3000
6. Try signing up again

## Option 4: Developer Tools Method (100% Works)
1. Go to http://localhost:3000
2. Press **F12** to open Developer Tools
3. Go to **Application** tab (or **Storage** in Firefox)
4. In left sidebar, find **"Cache Storage"**
5. Right-click on each cache and select **"Delete"**
6. Go to **"Local Storage"** → Right-click → **"Clear"**
7. Go to **"Session Storage"** → Right-click → **"Clear"**
8. Close Developer Tools
9. Press **Ctrl + Shift + R** to hard refresh
10. Try signing up again

## Verification
After clearing cache, when you sign up as a patient, you should be redirected to:
```
http://localhost:3000/setup-profile
```

If you still see the patient dashboard, the cache wasn't fully cleared. Try Option 4.

## Why This Happens
The browser cached the old JavaScript code that redirected patients to `/patient` instead of `/setup-profile`. The new code redirects to `/setup-profile`, but your browser is still using the old cached version.
