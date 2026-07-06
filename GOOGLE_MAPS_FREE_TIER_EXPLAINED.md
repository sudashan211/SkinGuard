# Google Maps Free Tier - How Long Will It Last?

## Quick Answer
**The free tier never expires!** You get **$200 credit EVERY MONTH, forever**, as long as your account is active.

---

## How Google Maps Pricing Works

### Monthly Free Credit
- **$200 USD credit** per month
- **Resets on the 1st of every month**
- **Never expires** as long as you have billing enabled
- If you don't use it all, it doesn't roll over (fresh $200 next month)

### What Happens If You Exceed $200?
- You'll be charged for usage beyond $200
- But for your app, this is **highly unlikely** during development/testing
- For small production apps, you'll likely stay within the free tier

---

## Your App's Estimated Usage

### Development/Testing Phase (Now)
**Estimated Monthly Usage: $0 - $5**

- **You (developer)**: Testing the map ~50 times/day
- **Maybe 2-3 friends**: Helping you test
- **Total**: ~1,500 map loads/month
- **Cost**: ~$10.50
- **Within free tier**: ✅ YES (you have $200 free)

### Small Production (100 Active Users)
**Estimated Monthly Usage: $15 - $30**

If each user:
- Opens "Find Hospitals" page: 10 times/month
- Searches for hospitals: 10 times/month
- Views hospital details: 20 times/month

**Total API calls per month:**
- Map loads: 1,000 × $7/1000 = $7
- Places API searches: 1,000 × $17/1000 = $17
- Places details: 2,000 × $17/1000 = $34
- **Total**: ~$58/month
- **Within free tier**: ✅ YES (you have $200 free)

### Medium Production (500 Active Users)
**Estimated Monthly Usage: $75 - $150**

- Still within the **$200 free tier** ✅
- You won't pay anything

### Large Production (1,000+ Active Users)
**Estimated Monthly Usage: $150 - $300**

- This is when you **might** exceed $200
- You'd pay: $100-$150/month
- But by this point, your app is successful and making money! 💰

---

## Detailed Pricing Breakdown

### 1. Maps JavaScript API (Loading the Map)
- **Free**: First 28,000 map loads/month (included in $200 credit)
- **Cost after free**: $7 per 1,000 loads
- **Your usage**: ~1,000-2,000 loads/month (development)
- **Your cost**: ~$7-14/month ✅ FREE

### 2. Places API - Nearby Search (Finding Hospitals)
- **Free**: First 11,700 requests/month
- **Cost after free**: $17 per 1,000 requests
- **Your usage**: ~500-1,000 requests/month
- **Your cost**: ~$8-17/month ✅ FREE

### 3. Places API - Place Details (Hospital Info)
- **Free**: First 11,700 requests/month
- **Cost after free**: $17 per 1,000 requests
- **Your usage**: ~1,000-2,000 requests/month
- **Your cost**: ~$17-34/month ✅ FREE

### 4. Geocoding API (Converting Addresses)
- **Free**: First 40,000 requests/month
- **Cost after free**: $5 per 1,000 requests
- **Your usage**: Minimal (only if you add address search)
- **Your cost**: ~$0-5/month ✅ FREE

---

## Real-World Scenarios

### Scenario 1: Student Project / Thesis Demo
**Timeline**: 3-6 months of development + presentation

- **Month 1-5**: Heavy testing (you + advisor)
  - Usage: ~$5-10/month
  - **Cost to you**: $0 ✅

- **Month 6**: Final demo + presentation
  - Usage: ~$15-20/month (lots of demos)
  - **Cost to you**: $0 ✅

**Total Cost**: **$0** (completely free!)

### Scenario 2: Startup Launch (First Year)
**Timeline**: 12 months

- **Months 1-3**: Development + beta testing (50 users)
  - Usage: ~$10-20/month
  - **Cost**: $0/month ✅

- **Months 4-8**: Public launch (200 users)
  - Usage: ~$40-80/month
  - **Cost**: $0/month ✅

- **Months 9-12**: Growth phase (500 users)
  - Usage: ~$100-150/month
  - **Cost**: $0/month ✅

**Total First Year Cost**: **$0** (completely free!)

### Scenario 3: Successful App (Years 2-3)
**Timeline**: Months 13-36

- **Users**: 1,000-2,000 active users
- **Usage**: $200-400/month
- **Cost to you**: $0-200/month
- **But**: Your app has revenue by now (ads, subscriptions, hospital partnerships)
- **Net profit**: Positive 💰

---

## How to Monitor Your Usage

### Check Monthly Usage:
1. Go to: https://console.cloud.google.com
2. Click **"Billing"** in left sidebar
3. Click **"Reports"**
4. You'll see a chart showing:
   - Current month spending
   - Daily breakdown
   - Which API is costing most

### Set Up Billing Alerts:
1. Go to **"Billing"** → **"Budgets & alerts"**
2. Click **"CREATE BUDGET"**
3. Set alerts at:
   - **$50** (25% of free tier) - Low warning
   - **$100** (50% of free tier) - Medium warning
   - **$150** (75% of free tier) - High warning
   - **$180** (90% of free tier) - Critical warning

4. You'll receive email notifications when you hit these thresholds

### Set Quota Limits (Recommended):
1. Go to **"APIs & Services"** → **"Quotas"**
2. Find **"Maps JavaScript API"**
3. Click **"All quotas"**
4. Set **"Requests per day"** to: **1,000** (safe limit for development)
5. This prevents accidental overuse if there's a bug

---

## What Can Make You Exceed the Free Tier?

### ❌ Bad Scenarios (Avoid These):
1. **Infinite loop bug**: Your code keeps calling Maps API in a loop
   - Could cost $1,000s in one day! 🔥
   - **Prevention**: Set quota limits (see above)

2. **Bot attacks**: Someone discovers your API and abuses it
   - **Prevention**: Use HTTP referrer restrictions (you already did this! ✅)

3. **Viral success**: App gets 10,000 users overnight
   - **Prevention**: Set billing alerts + daily quotas
   - **Good problem to have!** 🎉

### ✅ You're Protected Because:
1. ✅ You set **HTTP referrer restrictions** (only your domain can use it)
2. ✅ You set **API restrictions** (only Maps, Places, Geocoding)
3. ✅ Your app is for medical use (reasonable, not spam)
4. ✅ You can set **quota limits** to prevent runaway costs

---

## Comparison with Your Old API Key

### Why Did Your Old Key Run Out?
Two possible reasons:

1. **Free Trial Expired**:
   - Google gives $300 credit for **90 days** when you first sign up
   - After 90 days, it drops to $200/month ongoing
   - Your old account might have passed the 90-day trial

2. **Billing Not Enabled**:
   - Without billing, you get NO free tier
   - Even the $200/month requires billing to be enabled

### Your New Key:
- ✅ Billing enabled from the start
- ✅ $200/month ongoing (forever)
- ✅ Should last for your entire project

---

## Tips to Maximize Free Tier

### 1. Cache Map Results
```javascript
// Instead of fetching every time:
const [hospitals, setHospitals] = useState([]);

// Cache for 5 minutes:
const [lastFetch, setLastFetch] = useState(null);

if (!lastFetch || Date.now() - lastFetch > 5*60*1000) {
  // Fetch new data
  fetchHospitals();
  setLastFetch(Date.now());
}
```

### 2. Limit Search Radius
```javascript
// Instead of searching entire city:
radius: 50000 // 50km (very large)

// Use smaller radius:
radius: 5000 // 5km (more reasonable)
```

### 3. Lazy Load the Map
```javascript
// Don't load map on every page
// Only load when user clicks "Find Hospitals"
```

### 4. Use Static Maps for Thumbnails
- For hospital list items, use static images instead of interactive maps
- Static Map API is cheaper: $2 per 1,000 vs $7 per 1,000

---

## Summary: Will You Run Out?

### Development Phase (Now - 6 months):
**Answer**: ❌ **NO**, you won't run out
- Your usage: $5-20/month
- Free tier: $200/month
- **You're using only 2-10% of free tier**

### Small Production (First Year):
**Answer**: ❌ **NO**, you won't run out
- Your usage: $50-150/month
- Free tier: $200/month
- **You're using 25-75% of free tier**

### Large Production (Year 2+):
**Answer**: ⚠️ **MAYBE**, but it's a good problem!
- Your usage: $200-400/month
- Free tier: $200/month
- You'd pay: $0-200/month
- **But your app is successful and making money by then**

---

## Bottom Line

### For Your Thesis/Project:
**The $200/month free tier will last your entire project lifetime** ✅

You could run this app for **2-3 years** without paying a cent, as long as you stay under 500 active users.

### When Would You Actually Pay?
Only if your app becomes **very successful** with 1,000+ daily active users - and by then, you'll have monetization strategies in place!

---

## Questions?

### "What if I exceed $200 accidentally?"
- Set billing alerts (get email warnings)
- Set daily quota limits (API stops at limit)
- Google sends multiple warnings before charging

### "Can I use multiple free accounts?"
- ⚠️ Against Google's Terms of Service
- They can detect and ban all accounts
- Not worth the risk

### "What if I'm a student?"
- Some universities have Google Cloud credits ($300-500/year)
- Check if your school has a partnership
- Ask your CS department or advisor

---

**You're all set!** 🎉 Your $200/month free tier will easily last your entire development and early production phase.
