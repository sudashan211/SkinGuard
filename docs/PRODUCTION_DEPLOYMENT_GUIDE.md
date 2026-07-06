# Production Deployment Guide

## Current Status vs Production Ready

### Current Setup (Development)
```env
DEMO_MODE=true          # ⚠️ In-memory storage (data lost on restart)
USE_REAL_AI=true        # ✅ Real AI model (96.95% accuracy)
```

### Production Setup (What You Need)
```env
DEMO_MODE=false         # ✅ Persistent Supabase database
USE_REAL_AI=true        # ✅ Real AI model (96.95% accuracy)
```

## Steps to Make It Production Ready

### Step 1: Verify Supabase Configuration

Your Supabase credentials are already in `backend/.env`:

```env
SUPABASE_URL=https://fqvxrlltwymecsuqfzcg.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

✅ These are already configured!

### Step 2: Verify Supabase Database Schema

Make sure your Supabase database has all required tables:

**Required Tables**:
1. `profiles` - User profiles (id, email, full_name, role, verified, etc.)
2. `patient_data` - Patient health profiles (age, skin_type, family_history)
3. `doctors` - Doctor profiles (license_no, clinic_name, lat, lng, etc.)
4. `medical_reports` - Screening reports (image_url, ai_prediction, status, etc.)
5. `appointments` - Appointments (patient_id, doctor_id, scheduled_at, status)
6. `reviews` - Doctor reviews (patient_id, doctor_id, rating, review_text)

**Check Your Database**:
1. Go to https://supabase.com/dashboard
2. Select your project: `fqvxrlltwymecsuqfzcg`
3. Go to "Table Editor"
4. Verify all tables exist with correct columns

### Step 3: Switch to Production Mode

**Option A: Edit .env file directly**

Open `backend/.env` and change:
```env
DEMO_MODE=false    # Change from true to false
```

**Option B: Use command line**
```bash
# On Windows (PowerShell)
cd backend
(Get-Content .env) -replace 'DEMO_MODE=true', 'DEMO_MODE=false' | Set-Content .env

# On Linux/Mac
cd backend
sed -i 's/DEMO_MODE=true/DEMO_MODE=false/' .env
```

### Step 4: Restart Backend Server

**IMPORTANT**: You MUST restart the server for changes to take effect!

```bash
# Stop the current server (Ctrl+C)

# Start fresh (without --reload to avoid issues)
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Step 5: Test Production Mode

1. **Login**: Try logging in with a real account (not demo accounts)
2. **Upload Image**: Upload a skin lesion image
3. **Check Report**: Verify the report is saved
4. **Restart Server**: Stop and restart the backend
5. **Verify Persistence**: Login again and check if reports are still there

If reports persist after restart, you're in production mode! ✅

## What Changes in Production Mode?

### Data Storage
- **Demo Mode**: Data stored in RAM (lost on restart)
- **Production Mode**: Data stored in Supabase (persistent)

### User Accounts
- **Demo Mode**: Pre-created demo accounts (patient@demo.com, doctor@demo.com)
- **Production Mode**: Real user registration and authentication

### Reports
- **Demo Mode**: Reports lost when server restarts
- **Production Mode**: Reports saved permanently in database

### Images
- **Demo Mode**: Images saved to local `backend/uploads/` folder
- **Production Mode**: Images should be uploaded to Supabase Storage (or keep local for now)

## Common Issues and Solutions

### Issue 1: "NoneType object has no attribute 'table'"

**Cause**: Supabase client not initialized properly

**Solution**:
1. Verify Supabase credentials in `.env`
2. Make sure `DEMO_MODE=false`
3. Restart server completely (stop and start, don't use --reload)
4. Check backend logs for Supabase connection errors

### Issue 2: "User not found" after switching

**Cause**: Demo accounts don't exist in Supabase

**Solution**:
1. Create a new account using the signup page
2. Or manually create users in Supabase dashboard
3. Don't use demo credentials (patient@demo.com) in production mode

### Issue 3: "Table does not exist"

**Cause**: Database schema not set up

**Solution**:
1. Run database migrations (if you have them)
2. Or manually create tables in Supabase dashboard
3. Check the database schema documentation

### Issue 4: Images not displaying

**Cause**: Image URLs pointing to local storage

**Solution**:
1. For now, keep using local storage (`backend/uploads/`)
2. Make sure backend serves static files at `/uploads/`
3. Later, migrate to Supabase Storage for production

## Production Checklist

Before going live, verify:

- [ ] `DEMO_MODE=false` in `backend/.env`
- [ ] `USE_REAL_AI=true` in `backend/.env`
- [ ] Supabase credentials configured
- [ ] All database tables exist in Supabase
- [ ] Backend server restarted (not using --reload)
- [ ] Can create new user accounts
- [ ] Can login with real accounts
- [ ] Can upload images and get AI analysis
- [ ] Reports persist after server restart
- [ ] Can book appointments
- [ ] Can update health profile
- [ ] Images are accessible via URLs

## Recommended Production Setup

### Environment Variables
```env
# Production Configuration
DEMO_MODE=false
USE_REAL_AI=true

# Supabase (already configured)
SUPABASE_URL=https://fqvxrlltwymecsuqfzcg.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# JWT (generate secure keys for production!)
JWT_SECRET_KEY=generate-with-openssl-rand-hex-32
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# API
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false    # Disable reload in production

# CORS (update with your production domain)
CORS_ORIGINS=https://yourdomain.com,http://localhost:3000
```

### Security Recommendations

1. **Generate Secure JWT Secret**:
   ```bash
   openssl rand -hex 32
   ```
   Replace `JWT_SECRET_KEY` with the generated value

2. **Update CORS Origins**:
   - Remove localhost in production
   - Add your production domain

3. **Enable HTTPS**:
   - Use a reverse proxy (nginx, Caddy)
   - Get SSL certificate (Let's Encrypt)

4. **Environment Variables**:
   - Never commit `.env` to git
   - Use environment variables in deployment platform

## Deployment Platforms

### Option 1: Railway
- Easy deployment
- Automatic HTTPS
- Environment variables support
- Free tier available

### Option 2: Render
- Free tier for backend
- Automatic deployments from GitHub
- Built-in PostgreSQL (but you're using Supabase)

### Option 3: DigitalOcean App Platform
- $5/month for basic app
- Automatic scaling
- Built-in monitoring

### Option 4: AWS/GCP/Azure
- Most flexible
- Requires more setup
- Best for large scale

## Next Steps After Production Mode

1. **Test Thoroughly**: Test all features with real data
2. **Monitor Logs**: Watch for errors in production
3. **Backup Database**: Set up automatic backups in Supabase
4. **Set Up Monitoring**: Use tools like Sentry for error tracking
5. **Performance Testing**: Test with multiple concurrent users
6. **Security Audit**: Review authentication and authorization
7. **Deploy Frontend**: Deploy React app to Vercel/Netlify
8. **Custom Domain**: Set up your domain name
9. **Email Service**: Configure real email sending (SendGrid, etc.)
10. **Analytics**: Add usage analytics (Google Analytics, Mixpanel)

## Summary

**To make it production ready**:
1. Change `DEMO_MODE=false` in `backend/.env`
2. Verify Supabase database is set up
3. Restart backend server completely
4. Test that data persists after restart

That's it! Your AI is already production-ready (96.95% accuracy). You just need to enable persistent database storage.
