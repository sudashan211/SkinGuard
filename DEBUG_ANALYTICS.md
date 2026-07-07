# Debug Analytics - Why Dashboard Shows 0 Users

## 🔍 Quick Diagnosis

I've added a debug endpoint to check your database directly.

### Step 1: Check the Debug Endpoint

Open your browser and go to:

```
http://localhost:8001/api/admin/analytics/debug
```

**You'll need to include your admin token in the header**, or just:

1. **Open your admin dashboard** at http://localhost:3000/admin
2. **Open Browser DevTools** (F12)
3. **Go to Console tab**
4. **Paste this code**:

```javascript
fetch('http://localhost:8001/api/admin/analytics/debug', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
})
.then(r => r.json())
.then(data => {
  console.log('=== ANALYTICS DEBUG DATA ===');
  console.log('Current Time:', data.current_time_utc);
  console.log('Cutoff (24h ago):', data.cutoff_time_24h_ago);
  console.log('Total Reports (all time):', data.total_reports_all_time);
  console.log('Reports (last 24h):', data.total_reports_last_24h);
  console.log('Unique Patients (last 24h):', data.unique_patients_last_24h);
  console.log('\nMost Recent Reports:');
  data.most_recent_reports.forEach((r, i) => {
    console.log(`${i+1}. ID: ${r.id}, Patient: ${r.patient_id}, Created: ${r.created_at}`);
  });
  console.log('\n=== END DEBUG ===');
});
```

### Step 2: Interpret the Results

#### Scenario A: `total_reports_all_time = 0`
**Diagnosis:** No screenings in database at all
**Solution:** The patient needs to upload an image through the skin screening feature

#### Scenario B: `total_reports_all_time > 0` but `total_reports_last_24h = 0`
**Diagnosis:** Screenings exist but are older than 24 hours
**Solution:** Either:
1. Have the patient upload a new screening
2. Change the time window (see below)

#### Scenario C: `total_reports_last_24h > 0` but dashboard still shows 0
**Diagnosis:** Frontend/backend mismatch or caching issue
**Solution:** Hard refresh the dashboard (Ctrl+Shift+R)

---

## 🔧 Solutions Based on Your Situation

### Solution 1: Upload a New Screening (Recommended)

1. **Login as patient** (sudashanrao0702@gmail.com)
2. **Go to "Skin Screening" or "Upload"** section
3. **Select an image** (any image will work for testing)
4. **Wait for AI processing** to complete
5. **Go back to admin dashboard** → Refresh

### Solution 2: Change Time Window to 7 Days (For Testing)

If you want to see historical data, modify the time window:

**File:** `backend/app/analytics.py`

**Find line 50:**
```python
yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
```

**Change to:**
```python
yesterday = (datetime.utcnow() - timedelta(days=7)).isoformat()  # 7 days instead of 1
```

**Restart backend:**
- The uvicorn server should auto-reload
- Or manually restart: Ctrl+C then `uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload`

**Refresh admin dashboard** and you should see users from the last 7 days

---

## 📊 Understanding the Timestamps

### What to Look For in Debug Output

```json
{
  "current_time_utc": "2026-07-07T14:30:00",       // ← Current server time
  "cutoff_time_24h_ago": "2026-07-06T14:30:00",   // ← Cutoff (reports before this don't count)
  "total_reports_all_time": 5,                     // ← Total screenings ever
  "total_reports_last_24h": 0,                     // ← Screenings in last 24h (THIS is what shows on dashboard)
  "unique_patients_last_24h": 0,                   // ← Number that appears as "Daily Active Users"
  "most_recent_reports": [
    {
      "id": "abc123",
      "patient_id": "xyz789",
      "created_at": "2026-07-05T10:00:00"         // ← This report is 2 days old (won't count!)
    }
  ]
}
```

**Key Question:** Are any `created_at` timestamps **after** the `cutoff_time_24h_ago`?
- **YES** → Those should appear in dashboard (if not, there's a bug)
- **NO** → All screenings are too old, need new uploads

---

## 🎯 Most Likely Cause

Based on your screenshot showing "Last Login: Never" for all users, the screenings were probably created when you were testing the system earlier (days or weeks ago), and they're now outside the 24-hour window.

**Quick Test:**
1. Login as patient
2. Upload ONE image
3. Refresh admin dashboard
4. Should show "1" daily active user

---

## 📝 Alternative: Query Database Directly

If you have access to Supabase Dashboard:

1. Go to https://supabase.com/dashboard
2. Select your project
3. Go to **Table Editor** → `medical_reports`
4. Check the `created_at` column for recent entries

Or run this SQL query:

```sql
-- Count reports by recency
SELECT 
  COUNT(*) as total_reports,
  COUNT(CASE WHEN created_at >= NOW() - INTERVAL '24 hours' THEN 1 END) as reports_last_24h,
  COUNT(DISTINCT CASE WHEN created_at >= NOW() - INTERVAL '24 hours' THEN patient_id END) as unique_patients_24h,
  MAX(created_at) as most_recent_report
FROM medical_reports;
```

---

## 💡 Pro Tip: Demo Mode

For demonstration purposes, you can temporarily enable demo mode which returns fake data:

**File:** `backend/.env` (or Railway environment variables)

**Add:**
```
DEMO_MODE=true
```

This will make the dashboard show sample data (42 daily users, 156 screenings, etc.) without needing real database entries.

---

## 🚀 Next Steps

1. **Run the debug endpoint** (see Step 1 above)
2. **Check the timestamps** in the output
3. **If reports are old:** Upload a new screening as patient
4. **If reports are recent:** Check browser console for errors
5. **If still stuck:** Share the debug output with me

The debug endpoint will tell us exactly what's in your database and why the dashboard shows 0.
