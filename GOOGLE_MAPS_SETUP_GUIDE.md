# Google Maps API Setup Guide - New Account

## Step-by-Step Instructions to Set Up Google Maps API

### Step 1: Sign Out of Current Google Account
1. Go to https://console.cloud.google.com
2. Click your profile picture (top-right corner)
3. Click **"Sign out"**
4. Or use an **Incognito/Private browsing window** to avoid signing out

### Step 2: Sign In with Different Google Account
1. Go to https://console.cloud.google.com
2. Click **"Sign in"**
3. Use a **different Google account** (personal, school, or create new one)
4. If you don't have another account:
   - Click **"Create account"**
   - Follow the prompts to create a new Gmail account
   - Then come back to Google Cloud Console

### Step 3: Create a New Project
1. Once logged in, you'll see the Google Cloud Console dashboard
2. Click the **project dropdown** at the top (next to "Google Cloud")
3. Click **"NEW PROJECT"**
4. Enter project name: `SkinGuard-Maps` (or any name you like)
5. Click **"CREATE"**
6. Wait for the project to be created (takes 10-20 seconds)
7. Make sure the new project is selected in the dropdown

### Step 4: Enable Required APIs
You need to enable **3 APIs** for the hospital map feature to work:

#### 4.1 Enable Maps JavaScript API
1. In the left sidebar, click **"APIs & Services"** → **"Library"**
2. In the search box, type: `Maps JavaScript API`
3. Click on **"Maps JavaScript API"**
AIzaSyCQolRXIHc3HZZA59TcAOPyzJ_qeAjJBYA
4. Click the blue **"ENABLE"** button
5. Wait for it to enable (takes a few seconds)

#### 4.2 Enable Places API
1. Click **"Library"** again (or press the back button)
2. Search for: `Places API`
3. Click on **"Places API"**
4. Click **"ENABLE"**
5. Wait for it to enable

#### 4.3 Enable Geocoding API (Optional but Recommended)
1. Click **"Library"** again
2. Search for: `Geocoding API`
3. Click on **"Geocoding API"**
4. Click **"ENABLE"**

### Step 5: Create API Key
1. In the left sidebar, click **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** at the top
3. Select **"API key"**
4. A popup will show your new API key
5. **COPY THE API KEY** - it looks like: `AIzaSyAbc123def456GHI789jklMNO012pqrSTU`
6. Keep this window open for now

### Step 6: Restrict API Key (Important for Security)

#### 6.1 Set Application Restrictions
1. Click **"EDIT API KEY"** (or click the key name in the credentials list)
2. Under **"Application restrictions"**:
   - Select **"HTTP referrers (web sites)"**
3. Under **"Website restrictions"**, click **"ADD AN ITEM"**:
   - Add: `http://localhost:3000/*`
   - Click **"ADD AN ITEM"** again
   - Add: `http://localhost:5173/*`
   - Click **"ADD AN ITEM"** again
   - Add: `https://yourdomain.com/*` (if you have a production domain)
4. This prevents others from stealing and using your API key

#### 6.2 Set API Restrictions
1. Scroll down to **"API restrictions"**
2. Select **"Restrict key"**
3. Click the dropdown and select:
   - ✅ Maps JavaScript API
   - ✅ Places API
   - ✅ Geocoding API
4. Click **"SAVE"** at the bottom

### Step 7: Set Up Billing (Required but Free Tier Available)

⚠️ **Google requires a credit card, but you get $200 FREE credit per month!**

1. You'll see a banner saying "Enable billing"
2. Click **"ENABLE BILLING"**
3. Click **"CREATE BILLING ACCOUNT"**
4. Fill in your details:
   - Country: (Select your country)
   - Click **"Continue"**
5. Enter **payment information** (credit card or debit card)
   - ✅ You won't be charged unless you exceed $200/month
   - ✅ For your app usage, you'll likely stay well within free tier
6. Click **"START MY FREE TRIAL"**

### Step 8: Update Your SkinGuard App

1. Open your project folder: `d:\SkinGuard`
2. Open the file: `frontend\.env`
3. Find the line that starts with `VITE_GOOGLE_MAPS_API_KEY=`
4. Replace the old API key with your new one:

```env
VITE_GOOGLE_MAPS_API_KEY=YOUR_NEW_API_KEY_HERE
```

**Example:**
```env
VITE_GOOGLE_MAPS_API_KEY=AIzaSyAbc123def456GHI789jklMNO012pqrSTU
```

5. **Save the file**

### Step 9: Restart Frontend Server

1. Stop the current frontend server:
   - Find the terminal/command prompt running `npm run dev`
   - Press `Ctrl + C` to stop it

2. Start it again:
   ```bash
   cd d:\SkinGuard\frontend
   npm run dev
   ```

3. Wait for it to start (should see: "Local: http://localhost:3000/")

### Step 10: Test the Map

1. Open your browser: http://localhost:3000
2. Login as a patient
3. Go to **"Find Hospitals"** page
4. The map should now load properly!
5. You should see hospital markers and the hospital list

---

## Understanding Google Maps Pricing (Free Tier)

### What You Get for FREE Every Month:
- **$200 credit** = approximately:
  - **28,000 map loads**
  - **100,000 places searches**
  - **40,000 geocoding requests**

### Your App Usage (Estimated):
- **For development/testing**: You'll likely use $0-5/month
- **For small production app** (100 users): ~$10-20/month
- You're well within the free tier for now!

### How to Monitor Usage:
1. Go to Google Cloud Console
2. Left sidebar → **"APIs & Services"** → **"Dashboard"**
3. You'll see charts showing your API usage
4. Set up billing alerts:
   - Go to **"Billing"** → **"Budgets & alerts"**
   - Create alert for when you reach $50, $100, $150

---

## Troubleshooting

### Error: "This API project is not authorized to use this API"
- **Solution**: Make sure you enabled all 3 APIs (Maps JavaScript, Places, Geocoding)

### Error: "ApiNotActivatedMapError"
- **Solution**: Wait 2-5 minutes after enabling APIs (propagation delay)
- Then refresh your browser

### Error: "RefererNotAllowedMapError"
- **Solution**: Check API key restrictions
- Make sure `http://localhost:3000/*` is in the HTTP referrers list

### Map loads but no hospitals appear
- **Solution**: Check browser console for errors
- Make sure Places API is enabled
- Check if your location permission is granted

### "This page didn't load Google Maps correctly"
- **Solution**: Check the API key in `frontend/.env`
- Make sure there are no extra spaces or quotes
- Restart the frontend server

---

## Quick Reference

### Your New API Key Location:
- File: `frontend\.env`
- Variable: `VITE_GOOGLE_MAPS_API_KEY`

### APIs You Need Enabled:
1. ✅ Maps JavaScript API
2. ✅ Places API
3. ✅ Geocoding API (optional)

### Allowed Domains (HTTP Referrers):
- `http://localhost:3000/*`
- `http://localhost:5173/*`

### Where to Manage Your API Key:
https://console.cloud.google.com/apis/credentials

---

## Need Help?

### Check Current API Key:
Your frontend `.env` file currently has this key (you'll need to replace it):
```
Check the file: d:\SkinGuard\frontend\.env
```

### Verify APIs are Enabled:
1. Go to: https://console.cloud.google.com/apis/dashboard
2. You should see:
   - Maps JavaScript API (enabled)
   - Places API (enabled)

### Check Billing Status:
https://console.cloud.google.com/billing

---

## After Setup Checklist

- [ ] Created new Google Cloud project
- [ ] Enabled Maps JavaScript API
- [ ] Enabled Places API
- [ ] Created and copied API key
- [ ] Set HTTP referrer restrictions
- [ ] Set API restrictions
- [ ] Enabled billing (free tier)
- [ ] Updated `frontend\.env` with new key
- [ ] Restarted frontend server
- [ ] Tested map loads correctly
- [ ] Hospital markers appear on map

---

Good luck! The entire process should take about 10-15 minutes.
