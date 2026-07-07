# Admin Dashboard - Live Users Tracking Explanation

## 🔍 Issue Analysis

### Issue 1: Dashboard Shows 0 Daily Active Users

**Why This Happens:**

The "Daily Active Users" metric does **NOT** track currently logged-in users. Instead, it tracks:

> **Users who have created medical reports (performed skin screenings) in the last 24 hours**

**How It's Calculated:**

```python
# From backend/app/analytics.py line 53-69
# Step 1: Get timestamp from 24 hours ago
yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()

# Step 2: Try to use RPC function (if exists in database)
daily_users_result = supabase.rpc(
    'get_daily_active_users',
    {'since_timestamp': yesterday}
).execute()

# Step 3: Fallback - Count distinct patient_ids from medical_reports table
# in the last 24 hours
reports_result = supabase.table("medical_reports")\
    .select("patient_id")\
    .gte("created_at", yesterday)\
    .execute()

# Count unique patient IDs
unique_patients = set(r["patient_id"] for r in reports_result.data)
daily_active_users = len(unique_patients)
```

**Why You're Seeing 0:**

1. ✅ You're logged in as admin
2. ✅ You can see the dashboard
3. ❌ BUT: No users have performed **skin screenings** (uploaded images for analysis) in the last 24 hours

---

## 💡 How to Get Real "Daily Active Users"

### Option 1: Perform a Skin Screening (Recommended for Testing)

1. **Login as a regular user** (not admin)
2. Go to the **"Skin Screening"** page
3. **Upload a skin image** for analysis
4. Wait for AI to process and generate a report
5. Go back to admin dashboard → Refresh
6. "Daily Active Users" should now show **1**

### Option 2: Have Multiple Users Perform Screenings

The count increases based on **unique users** who upload images:
- 1 user uploads 5 images = 1 daily active user
- 5 users upload 1 image each = 5 daily active users

---

## 🎯 What "Daily Active Users" Actually Means

| Metric | What It Tracks | What It DOESN'T Track |
|--------|----------------|----------------------|
| **Daily Active Users** | Users who uploaded skin images for screening in last 24h | Users who just logged in |
| | Users who created medical reports | Users browsing the site |
| | Actual platform usage | Page views or sessions |

---

## 📊 Admin Dashboard Metrics Breakdown

### 1. Daily Active Users
- **Source**: `medical_reports` table
- **Calculation**: Count distinct `patient_id` where `created_at >= 24 hours ago`
- **Updates**: Real-time (refreshes on page load)

### 2. Total Screenings
- **Source**: `medical_reports` table
- **Calculation**: Total count of all medical reports (all time)
- **Updates**: Increases each time a user uploads an image

### 3. Average Processing Time
- **Source**: `audit_logs` table
- **Calculation**: Average of `metadata.total_processing_time` for `action="ai_processing"`
- **Updates**: Recalculated each time dashboard loads

### 4. Most Common Cancer Types
- **Source**: `medical_reports.ai_prediction` field
- **Calculation**: Count of each cancer type from AI predictions
- **Shows**: Bar chart of cancer types detected

### 5. Geographic Distribution
- **Source**: `doctors` table (doctor locations)
- **Calculation**: Groups doctors by rounded lat/lng coordinates
- **Shows**: Distribution of medical professionals on the platform

---

## 🐛 Issue 2: 401 Unauthorized on Logout

### Error Message
```
Failed to load resource: the server responded with a status of 401 (Unauthorized)
:8001/api/auth/logout:1
```

### Why This Happens

The logout endpoint **requires authentication** (`Depends(get_current_user)`), but the frontend might be:

1. **Calling logout after token expires** - Token is no longer valid
2. **Clearing token before calling API** - Token removed from headers before API call
3. **Token format issue** - Bearer token not properly formatted

### Is This Actually a Problem?

**No!** This is a **visual error** that doesn't affect functionality:

✅ **Logout still works** - Frontend clears tokens locally
✅ **User is logged out** - Redirected to login page
✅ **Security is fine** - JWT-based logout is client-side

The 401 error appears in console but doesn't break the user experience.

---

## 🔧 How to Fix the 401 Logout Error (Optional)

### Option 1: Make Logout Endpoint Public (Simplest)

**File**: `backend/app/routers/auth.py`

```python
@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout():
    """
    Logout - stateless JWT system, handled client-side
    No authentication required since logout just returns a message
    """
    return {"message": "Successfully logged out"}
```

### Option 2: Handle 401 Gracefully in Frontend (Better UX)

**File**: `frontend/src/services/auth.ts` (or wherever logout is called)

```typescript
async logout() {
  try {
    // Try to call backend logout endpoint
    await api.post('/api/auth/logout')
  } catch (error) {
    // Ignore 401 errors on logout - token may be expired
    if (error.response?.status !== 401) {
      console.error('Logout error:', error)
    }
  } finally {
    // Always clear local tokens regardless of API response
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    // Redirect to login page
    window.location.href = '/login'
  }
}
```

### Option 3: Clear Tokens Before API Call (Current Behavior)

This is what's happening now - frontend clears tokens then calls API, which causes 401 because there's no token to authenticate with.

**Fix**: Call API **before** clearing tokens, then clear tokens in the `finally` block.

---

## 🧪 Testing the Dashboard Metrics

### Step-by-Step Test

1. **Open browser DevTools** (F12) → Network tab
2. **Login as admin** at http://localhost:3000
3. **Check API call**: Should see `GET /api/admin/analytics`
4. **Check response**:
   ```json
   {
     "daily_active_users": 0,
     "total_screenings": 0,
     "average_processing_time": 0.0,
     "most_common_cancer_types": [],
     "geographic_distribution": []
   }
   ```

5. **In a new browser tab**, login as a **regular user**
6. **Upload a skin image** for screening
7. **Wait for AI processing** to complete
8. **Go back to admin tab** → Refresh dashboard
9. **Check metrics again**:
   ```json
   {
     "daily_active_users": 1,  // ← Should now be 1
     "total_screenings": 1,    // ← Should now be 1
     "average_processing_time": 3.2,  // ← Actual AI time
     "most_common_cancer_types": [
       {"type": "melanoma", "count": 1}
     ],
     "geographic_distribution": [...]
   }
   ```

---

## 📝 Summary

### The "0 Daily Active Users" is Normal Because:

1. ✅ Metric tracks **screening activity**, not login sessions
2. ✅ No users have uploaded images for analysis in last 24 hours
3. ✅ System is working correctly - just no activity to report

### To See Real Metrics:

- Upload skin images as a regular user
- The dashboard will immediately reflect the activity
- Each unique user who uploads counts as 1 active user (regardless of how many images they upload)

### The 401 Logout Error:

- Visual console error, not a functional problem
- Logout still works correctly
- Can be fixed by adjusting frontend error handling
- Low priority unless it bothers you in DevTools

---

## 🔍 Database Tables Involved

```sql
-- Daily Active Users query
SELECT DISTINCT patient_id 
FROM medical_reports 
WHERE created_at >= NOW() - INTERVAL '24 hours';

-- Total Screenings query
SELECT COUNT(*) FROM medical_reports;

-- Average Processing Time query
SELECT AVG((metadata->>'total_processing_time')::float) 
FROM audit_logs 
WHERE action = 'ai_processing';

-- Most Common Cancer Types query
SELECT 
  ai_prediction->'predictions'->0->>'type' as cancer_type,
  COUNT(*) as count
FROM medical_reports
GROUP BY cancer_type
ORDER BY count DESC;
```

---

## 💡 Pro Tips

1. **Testing locally?** Create test medical reports to see metrics populate
2. **Dashboard empty?** Run the AI screening workflow as a regular user
3. **Want more users?** Create multiple accounts and have each upload images
4. **Checking database directly?** Query `medical_reports` table for recent activity

---

## 🚀 Next Steps

1. **Test the workflow**:
   - Login as regular user → Upload skin image → Check admin dashboard
   
2. **Fix logout 401** (optional):
   - Implement Option 2 (graceful error handling) in frontend

3. **Monitor real usage**:
   - Once deployed, dashboard will show actual user activity
   - Metrics will populate as users perform screenings

---

**Remember**: Daily Active Users = Users who uploaded images in last 24h, NOT just logged-in users!
